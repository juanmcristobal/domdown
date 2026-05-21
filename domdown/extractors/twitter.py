from __future__ import annotations

import copy
import re
from typing import List, Optional

from bs4 import Tag

from domdown.extractors._base import BaseExtractor, ExtractorOptions
from domdown.types import ExtractorResult
from domdown.utils.comments import CommentData, build_comment_tree, build_content_html, build_quoted_post
from domdown.utils.dom import escape_html, parse_html, serialize_html


class TwitterExtractor(BaseExtractor):
    def __init__(
        self,
        document: Tag,
        url: str,
        schema_org_data: any = None,
        options: Optional[ExtractorOptions] = None,
    ):
        super().__init__(document, url, schema_org_data, options)

        timeline = document.select_one('[aria-label="Timeline: Conversation"]')
        if not timeline:
            single_tweet = document.select_one('article[data-testid="tweet"]')
            if single_tweet:
                self.main_tweet = single_tweet
            return

        cells = timeline.select('[data-testid="cellInnerDiv"]')

        first_section = timeline.select_one("section, h2")
        first_section_parent = first_section.parent if first_section else None

        main_handle = ""
        is_first_tweet = True
        thread_ended = False
        last_was_tweet = False
        current_depth = 0

        self.main_tweet: Optional[Tag] = None
        self.thread_tweets: List[Tag] = []
        self.reply_tweets: List[Tag] = []
        self.reply_depths: List[int] = []

        for cell in cells:
            if first_section_parent and first_section_parent.find_previous(cell):
                if first_section_parent.find_previous(cell):
                    break

            article = cell.select_one('article[data-testid="tweet"]')
            if article:
                if is_first_tweet:
                    self.main_tweet = article
                    main_handle = self._get_handle(article)
                    is_first_tweet = False
                    last_was_tweet = True
                    continue

                handle = self._get_handle(article)

                if not thread_ended and handle == main_handle:
                    self.thread_tweets.append(article)
                    last_was_tweet = True
                    continue

                if not thread_ended:
                    thread_ended = True

                if last_was_tweet:
                    current_depth += 1
                else:
                    current_depth = 0

                self.reply_tweets.append(article)
                self.reply_depths.append(current_depth)
                last_was_tweet = True
            else:
                last_was_tweet = False

    def can_extract(self) -> bool:
        return bool(self.main_tweet)

    def extract(self) -> ExtractorResult:
        parts = [self._extract_tweet_content(self.main_tweet)]
        for tweet in self.thread_tweets:
            parts.append(self._extract_tweet_content(tweet))
        post_content = "\n<hr>\n".join(parts)

        comments = self._extract_comments() if self.options.include_replies is not False else ""

        content_html = build_content_html("twitter", post_content, comments)

        tweet_author = self._get_tweet_author()
        description = self._create_description(self.main_tweet)
        title = self.post_title(tweet_author, "X")

        return ExtractorResult(
            content=content_html,
            content_html=content_html,
            variables={
                "title": title,
                "author": tweet_author,
                "site": "X (Twitter)",
                "description": description,
            },
        )

    def _extract_comments(self) -> str:
        if not self.reply_tweets:
            return ""

        comment_data: List[CommentData] = []
        for i, tweet in enumerate(self.reply_tweets):
            user_info = self._extract_user_info(tweet)
            content = self._extract_tweet_content(tweet)

            author = (
                f"{user_info['full_name']} {user_info['handle']}" if user_info["full_name"] else user_info["handle"]
            )
            comment_data.append(
                CommentData(
                    author=author,
                    date=user_info["date"],
                    content=content,
                    depth=self.reply_depths[i],
                    url=user_info["permalink"],
                )
            )

        return build_comment_tree(comment_data)

    def _get_handle(self, tweet: Tag) -> str:
        name_element = tweet.select_one("[data-testid='User-Name']")
        links = name_element.select("a") if name_element else []
        return links[1].get_text(strip=True) if len(links) > 1 else ""

    def _format_tweet_text(self, text: str) -> str:
        if not text:
            return ""

        temp_div = parse_html(text)

        for link in temp_div.select("a"):
            handle = link.get_text(strip=True)
            link.replace_with(link.get_text() or handle)

        for element in temp_div.select("span, div"):
            element.unwrap()

        clean_text = serialize_html(temp_div)
        paragraphs = [line.strip() for line in clean_text.split("\n") if line.strip()]

        return "\n".join(f"<p>{p}</p>" for p in paragraphs)

    def _replace_emoji_images(self, container: Tag) -> None:
        for img in container.select('img[src*="/emoji/"]'):
            alt_text = img.get("alt")
            if alt_text:
                img.replace_with(img.get_text() or alt_text)

    def _find_quoted_tweet(self, tweet: Tag) -> Optional[Tag]:
        labelled = tweet.select_one('[aria-labelledby*="id__"]')
        if not labelled:
            return None
        user_name = labelled.select_one('[data-testid="User-Name"]')
        if not user_name:
            return None
        return user_name.find_parent('[aria-labelledby*="id__"]')

    def _extract_tweet_content(self, tweet: Optional[Tag]) -> str:
        if not tweet:
            return ""

        tweet_clone = copy.copy(tweet)
        self._replace_emoji_images(tweet_clone)

        tweet_text_el = tweet_clone.select_one('[data-testid="tweetText"]')
        tweet_text = serialize_html(tweet_text_el) if tweet_text_el else ""
        formatted_text = self._format_tweet_text(tweet_text)

        quoted_tweet = self._find_quoted_tweet(tweet)
        images = self._extract_images(tweet, quoted_tweet)
        quoted_html = self._extract_quoted_tweet(quoted_tweet) if quoted_tweet else ""
        card_link = self._extract_card(tweet)

        html = ""
        if formatted_text:
            html += formatted_text
        if images:
            html += f"\n{images}"
        if card_link:
            html += f"\n{card_link}"
        if quoted_html:
            html += f"\n{quoted_html}"

        return html

    def _extract_quoted_tweet(self, quoted_tweet: Optional[Tag]) -> str:
        if not quoted_tweet:
            return ""

        tweet_clone = copy.copy(quoted_tweet)
        self._replace_emoji_images(tweet_clone)

        tweet_text_el = tweet_clone.select_one('[data-testid="tweetText"]')
        tweet_text = serialize_html(tweet_text_el) if tweet_text_el else ""
        formatted_text = self._format_tweet_text(tweet_text)
        user_info = self._extract_user_info(quoted_tweet)
        images = self._extract_images(quoted_tweet, None)

        content = ""
        if formatted_text:
            content += formatted_text
        if images:
            content += f"\n{images}"

        author = f"{user_info['full_name']} {user_info['handle']}" if user_info["full_name"] else user_info["handle"]

        return build_quoted_post(
            type(
                "QuotedPostData",
                (),
                {
                    "author": author if author else None,
                    "date": user_info["date"] if user_info["date"] else None,
                    "content": content,
                },
            )()
        )

    def _extract_user_info(self, tweet: Tag) -> dict:
        name_element = tweet.select_one('[data-testid="User-Name"]')
        if not name_element:
            return {"full_name": "", "handle": "", "date": "", "permalink": ""}

        links = name_element.select("a")
        full_name = links[0].get_text(strip=True) if links else ""
        handle = links[1].get_text(strip=True) if len(links) > 1 else ""

        if not full_name or not handle:
            children = list(name_element.children)
            if len(children) >= 2:
                full_name = children[0].get_text(strip=True) if children[0] else ""
                second_text = children[1].get_text(strip=True) if len(children) > 1 and children[1] else ""
                handle_match = re.search(r"(@\w+)", second_text)
                handle = handle_match.group(1) if handle_match else ""

        timestamp = tweet.select_one("time")
        datetime = timestamp.get("datetime", "") if timestamp else ""
        date = ""
        if datetime:
            try:
                from datetime import datetime as dt

                date = dt.fromisoformat(datetime.replace("Z", "+00:00")).strftime("%Y-%m-%d")
            except Exception:
                pass

        permalink = ""
        if timestamp:
            link = timestamp.find_parent("a")
            permalink = link.get("href", "") if link else ""

        return {"full_name": full_name, "handle": handle, "date": date, "permalink": permalink}

    def _extract_images(self, tweet: Tag, quoted_tweet: Optional[Tag]) -> List[str]:
        image_containers = ['[data-testid="tweetPhoto"]', '[data-testid="tweet-image"]', 'img[src*="media"]']

        images: List[str] = []

        for selector in image_containers:
            elements = tweet.select(selector)

            for img in elements:
                if quoted_tweet and img.find_parent(quoted_tweet):
                    continue

                if img.name == "img" and img.get("alt"):
                    high_quality_src = (img.get("src") or "").replace(r"&name=\w+$", "&name=large")
                    clean_alt = (img.get("alt") or "").replace(r"\s+", " ").strip()
                    images.append(f'<img src="{escape_html(high_quality_src)}" alt="{escape_html(clean_alt)}" />')

        return images

    def _extract_card(self, tweet: Tag) -> str:
        card = tweet.select_one('[data-testid="card.wrapper"]')
        if not card:
            return ""

        card_link = card.select_one("a[href]")
        if not card_link:
            return ""

        href = card_link.get("href", "")
        label = card_link.get("aria-label", "")
        title = label.split("\n")[0].strip() if label else href

        return f'<p><a href="{escape_html(href)}">{escape_html(title)}</a></p>'

    def _get_tweet_id(self) -> str:
        match = re.search(r"status/(\d+)", self.url)
        return match.group(1) if match else ""

    def _get_tweet_author(self) -> str:
        handle = self._get_handle(self.main_tweet)
        return handle if handle.startswith("@") else f"@{handle}"

    def _create_description(self, tweet: Optional[Tag]) -> str:
        if not tweet:
            return ""

        tweet_text_elem = tweet.select_one('[data-testid="tweetText"]')
        tweet_text = tweet_text_elem.get_text(strip=True) if tweet_text_elem else ""
        return tweet_text[:140].replace(r"\s+", " ")
