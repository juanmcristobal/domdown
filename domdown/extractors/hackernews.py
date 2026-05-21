from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional

from bs4 import Tag

from domdown.extractors._base import BaseExtractor, ExtractorOptions
from domdown.types import ExtractorResult
from domdown.utils.comments import CommentData, build_comment_tree, build_content_html
from domdown.utils.dom import escape_html, serialize_html


@dataclass
class StoryData:
    id: str
    title: str
    url: str
    site: str
    score: str
    author: str
    date: str
    comments: str
    comments_url: str


class HackerNewsExtractor(BaseExtractor):
    def __init__(
        self,
        document: Tag,
        url: str,
        schema_org_data: any = None,
        options: Optional[ExtractorOptions] = None,
    ):
        super().__init__(document, url, schema_org_data, options)
        self.main_post = document.select_one(".fatitem")
        self.is_listing_page = self._detect_listing_page()
        self.is_comment_page = self._detect_comment_page()
        self.main_comment = self.main_post.select_one("tr.athing") if self.is_comment_page and self.main_post else None

    def _detect_listing_page(self) -> bool:
        if self.main_post:
            return False
        stories = self.document.select("tr.athing")
        return len(stories) > 1

    def _detect_comment_page(self) -> bool:
        if not self.main_post:
            return False
        return bool(self.main_post.select_one(".onstory")) and not self.main_post.select_one(".titleline")

    def can_extract(self) -> bool:
        return bool(self.main_post) or self.is_listing_page

    def extract(self) -> ExtractorResult:
        if self.is_listing_page:
            return self._extract_listing()

        post_content = self._get_post_content()
        comments = self._extract_comments() if self.options.include_replies is not False else ""

        content_html = build_content_html("hackernews", post_content, comments)
        post_title = self._get_post_title()
        post_author = self._get_post_author()
        description = self._create_description()
        published = self._get_post_date()

        return ExtractorResult(
            content=content_html,
            content_html=content_html,
            variables={
                "title": post_title,
                "author": post_author,
                "site": "Hacker News",
                "description": description,
                "published": published,
            },
        )

    def _get_more_link(self) -> Optional[dict]:
        more_link = self.document.select_one(".morelink")
        if not more_link:
            return None
        href = more_link.get("href", "")
        text = more_link.get_text(strip=True) or "More"
        return {"url": href, "text": text}

    def _extract_listing(self) -> ExtractorResult:
        stories = self._extract_stories()
        more_link = self._get_more_link()
        content_html = self._build_listing_html(stories, more_link)
        title = (
            re.sub(r"\s*\|\s*Hacker News$", "", self.document.title).strip() if self.document.title else "Hacker News"
        )

        return ExtractorResult(
            content=content_html,
            content_html=content_html,
            variables={
                "title": title,
                "site": "Hacker News",
            },
        )

    def _extract_stories(self) -> List[StoryData]:
        story_rows = self.document.select("tr.athing")
        stories: List[StoryData] = []

        for row in story_rows:
            row_id = row.get("id", "")
            title_el = row.select_one(".titleline a")
            if not title_el:
                continue

            title = title_el.get_text(strip=True)
            story_url = title_el.get("href", "")

            site_elem = row.select_one(".sitestr")
            site = site_elem.get_text(strip=True) if site_elem else ""

            sub_row = row.next_sibling
            if sub_row and isinstance(sub_row, Tag):
                score_elem = sub_row.select_one(".score")
                score = score_elem.get_text(strip=True) if score_elem else ""
                author_elem = sub_row.select_one(".hnuser")
                author = author_elem.get_text(strip=True) if author_elem else ""
                age_el = sub_row.select_one(".age")
                timestamp = age_el.get("title", "") if age_el else ""
                date = timestamp.split("T")[0] if timestamp else ""

                sub_links = sub_row.select("td.subtext a") if sub_row else []
                last_link = sub_links[-1] if sub_links else None
                comments_text = last_link.get_text(strip=True).replace("\u00a0", " ") if last_link else ""
                comments = comments_text if re.search(r"\d+\s*comment", comments_text) else ""
                comments_url = f"https://news.ycombinator.com/item?id={row_id}" if row_id else ""
            else:
                score, author, date, comments, comments_url = "", "", "", "", ""

            stories.append(
                StoryData(
                    id=row_id,
                    title=title,
                    url=story_url,
                    site=site,
                    score=score,
                    author=author,
                    date=date,
                    comments=comments,
                    comments_url=comments_url,
                )
            )

        return stories

    def _build_listing_html(self, stories: List[StoryData], more_link: Optional[dict]) -> str:
        if not stories:
            return ""

        items = []
        for story in stories:
            html = "<li>"
            html += f'<a href="{escape_html(story.url)}">{escape_html(story.title)}</a>'

            if story.site:
                html += f" <small>({escape_html(story.site)})</small>"

            meta: List[str] = []
            if story.score:
                meta.append(escape_html(story.score))
            if story.author:
                meta.append(f"by {escape_html(story.author)}")
            if story.comments:
                meta.append(f'<a href="{escape_html(story.comments_url)}">{escape_html(story.comments)}</a>')

            if meta:
                html += f"<br><small>{' · '.join(meta)}</small>"

            html += "</li>"
            items.append(html)

        html = f"<ol>{''.join(items)}</ol>"

        if more_link:
            html += f'<p><a href="{escape_html(more_link["url"])}">{escape_html(more_link["text"])}</a></p>'

        return html

    def _get_post_content(self) -> str:
        if not self.main_post:
            return ""

        if self.is_comment_page and self.main_comment:
            author = (
                self.main_comment.select_one(".hnuser").get_text()
                if self.main_comment.select_one(".hnuser")
                else "[deleted]"
            )
            commtext = self.main_comment.select_one(".commtext")
            comment_text = serialize_html(commtext) if commtext else ""
            time_element = self.main_comment.select_one(".age")
            timestamp = time_element.get("title", "") if time_element else ""
            date = timestamp.split("T")[0] if timestamp else ""
            points = (
                self.main_comment.select_one(".score").get_text(strip=True)
                if self.main_comment.select_one(".score")
                else ""
            )

            from ..utils.comments import build_comment

            return build_comment(
                CommentData(
                    author=author,
                    date=date,
                    content=comment_text,
                    score=points or None,
                )
            )

        title_row = self.main_post.select_one("tr.athing")
        url = (
            title_row.select_one(".titleline a").get("href", "")
            if title_row and title_row.select_one(".titleline a")
            else ""
        )

        content = ""
        if url:
            content += f'<p><a href="{url}" target="_blank">{url}</a></p>'

        text = self.main_post.select_one(".toptext")
        if text:
            content += f'<div class="post-text">{serialize_html(text)}</div>'

        return content

    def _extract_comments(self) -> str:
        comments = self.document.select("tr.comtr")
        return self._process_comments(comments)

    def _process_comments(self, comments: List[Tag]) -> str:
        comment_data: List[CommentData] = []
        processed_ids = set()

        for comment in comments:
            comment_id = comment.get("id")
            if not comment_id or comment_id in processed_ids:
                continue
            processed_ids.add(comment_id)

            ind = comment.select_one(".ind img")
            indent = ind.get("width", "0") if ind else "0"
            depth = int(indent) // 40 if indent.isdigit() else 0

            comment_text = comment.select_one(".commtext")
            author = comment.select_one(".hnuser").get_text() if comment.select_one(".hnuser") else "[deleted]"
            time_element = comment.select_one(".age")
            points = comment.select_one(".score").get_text(strip=True) if comment.select_one(".score") else ""

            if not comment_text:
                continue

            comment_url = f"https://news.ycombinator.com/item?id={comment_id}"
            timestamp = time_element.get("title", "") if time_element else ""
            date = timestamp.split("T")[0] if timestamp else ""

            comment_data.append(
                CommentData(
                    author=author,
                    date=date,
                    content=serialize_html(comment_text),
                    depth=depth,
                    score=points or None,
                    url=comment_url,
                )
            )

        return build_comment_tree(comment_data)

    def _get_post_id(self) -> str:
        import re

        match = re.search(r"id=(\d+)", self.url)
        return match.group(1) if match else ""

    def _get_post_title(self) -> str:
        if self.is_comment_page and self.main_comment:
            author = (
                self.main_comment.select_one(".hnuser").get_text()
                if self.main_comment.select_one(".hnuser")
                else "[deleted]"
            )
            comment_text = (
                self.main_comment.select_one(".commtext").get_text()
                if self.main_comment.select_one(".commtext")
                else ""
            )
            preview = (comment_text.strip()[:50] + "...") if len(comment_text.strip()) > 50 else comment_text.strip()
            return f"Comment by {author}: {preview}"
        title_elem = self.main_post.select_one(".titleline") if self.main_post else None
        return title_elem.get_text(strip=True) if title_elem else ""

    def _get_post_author(self) -> str:
        if not self.main_post:
            return ""
        author_elem = self.main_post.select_one(".hnuser")
        return author_elem.get_text(strip=True) if author_elem else ""

    def _create_description(self) -> str:
        title = self._get_post_title()
        author = self._get_post_author()
        if self.is_comment_page:
            return f"Comment by {author} on Hacker News"
        return f"{title} - by {author} on Hacker News"

    def _get_post_date(self) -> str:
        if not self.main_post:
            return ""
        time_element = self.main_post.select_one(".age")
        if not time_element:
            return ""
        timestamp = time_element.get("title", "")
        return timestamp.split("T")[0] if timestamp else ""
