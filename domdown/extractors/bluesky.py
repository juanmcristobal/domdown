from __future__ import annotations

import copy
from typing import List, Optional

from bs4 import Tag

from domdown.extractors._base import BaseExtractor, ExtractorOptions
from domdown.types import ExtractorResult
from domdown.utils.comments import CommentData, build_comment_tree, build_content_html, build_quoted_post
from domdown.utils.dom import escape_html


class BlueskyExtractor(BaseExtractor):
    def __init__(
        self,
        document: Tag,
        url: str,
        schema_org_data: any = None,
        options: Optional[ExtractorOptions] = None,
    ):
        super().__init__(document, url, schema_org_data, options)
        self.thread_screen = document.select_one('[data-testid="postThreadScreen"]')
        self.post_items: List[Tag] = []
        if self.thread_screen:
            self.post_items = list(self.thread_screen.select('[data-testid^="postThreadItem-by-"]'))

    def can_extract(self) -> bool:
        return len(self.post_items) > 0

    def extract(self) -> ExtractorResult:
        main_handle = self._get_handle(self.post_items[0])

        thread_items: List[Tag] = []
        reply_items: List[Tag] = []
        thread_ended = False

        for item in self.post_items:
            handle = self._get_handle(item)
            if not thread_ended and handle == main_handle:
                thread_items.append(item)
            else:
                thread_ended = True
                reply_items.append(item)

        post_parts = [self._extract_post_content(item) for item in thread_items]
        post_content = "\n<hr>\n".join(post_parts)

        comments = self._extract_comments(reply_items) if self.options.include_replies is not False else ""

        content_html = build_content_html("bluesky", post_content, comments)
        author = f"@{main_handle}"
        display_name = self._get_display_name(self.post_items[0])
        description = self._create_description(self.post_items[0])
        published = self._get_published_date()
        title = self.post_title(display_name or author, "Bluesky")

        return ExtractorResult(
            content=content_html,
            content_html=content_html,
            variables={
                "title": title,
                "author": display_name or author,
                "site": "Bluesky",
                "description": description,
                "published": published if published else None,
            },
        )

    def _extract_comments(self, reply_items: List[Tag]) -> str:
        if not reply_items:
            return ""

        current_depth = 0
        comment_data: List[CommentData] = []

        for item in reply_items:
            handle = self._get_handle(item)
            display_name = self._get_display_name(item)
            content = self._extract_post_content(item)
            date = self._get_reply_date(item)
            permalink = self._get_permalink(item)

            if self._has_top_connector(item):
                current_depth += 1
            else:
                current_depth = 0

            author = f"{display_name} @{handle}" if display_name else f"@{handle}"
            comment_data.append(
                CommentData(
                    author=author,
                    date=date,
                    content=content,
                    depth=current_depth,
                    url=permalink if permalink else None,
                )
            )

        return build_comment_tree(comment_data)

    def _has_top_connector(self, item: Tag) -> bool:
        children = list(item.children)
        if not children:
            return False
        connector = children[0]
        if not connector:
            return False
        divs = connector.select("div")
        for div in divs:
            style = div.get("style", "")
            if "width: 2px" in style and "background-color" in style:
                return True
        return False

    def _get_handle(self, item: Tag) -> str:
        test_id = item.get("data-testid", "")
        import re

        match = re.match(r"postThreadItem-by-(.+)$", test_id)
        return match.group(1) if match else ""

    def _get_display_name(self, item: Tag) -> str:
        avatar_link = item.select_one('a[aria-label*="avatar"]')
        if avatar_link:
            label = avatar_link.get("aria-label", "")
            match = label.match(r"^(.+)'s avatar$") if hasattr(label, "match") else None
            if match:
                return match.group(1)

        profile_links = item.select('a[href^="/profile/"]')
        for link in profile_links:
            text = link.get_text(strip=True)
            if text and not text.startswith("@") and "avatar" not in text and "·" not in text:
                return text

        return ""

    def _get_published_date(self) -> str:
        meta_tag = self.document.select_one('meta[name="twitter:value1"]')
        if meta_tag:
            datetime = meta_tag.get("content", "")
            if datetime:
                try:
                    from datetime import datetime as dt

                    return dt.fromisoformat(datetime.replace("Z", "+00:00")).strftime("%Y-%m-%d")
                except Exception:
                    pass
        return ""

    def _get_reply_date(self, item: Tag) -> str:
        time_link = item.select_one('a[href*="/post/"]')
        if not time_link:
            return ""

        label = time_link.get("aria-label", "")
        if not label:
            return ""

        try:
            parsed = label.replace(" at ", " ")
            from datetime import datetime

            dt = datetime.strptime(parsed, "%B %d, %Y %I:%M %p")
            return dt.strftime("%Y-%m-%d")
        except Exception:
            pass

        return ""

    def _get_permalink(self, item: Tag) -> str:
        link = item.select_one('a[href*="/post/"]')
        if not link:
            return ""
        href = link.get("href", "")
        return href if href.startswith("http") else f"https://bsky.app{href}"

    def _extract_post_content(self, item: Tag) -> str:
        parts: List[str] = []

        text_div = item.select_one('div[data-word-wrap="1"]')
        if text_div:
            text = self._clean_text(text_div)
            if text:
                parts.append(text)

        images = self._extract_images(item)
        if images:
            parts.append(images)

        card = self._extract_link_card(item)
        if card:
            parts.append(card)

        quoted = self._extract_quoted_post(item)
        if quoted:
            parts.append(quoted)

        return "\n".join(parts)

    def _clean_text(self, text_div: Tag) -> str:
        clone = copy.copy(text_div)

        for link in clone.select('a[href*="/profile/"]'):
            text = link.get_text(strip=True)
            href = link.get("href", "")
            if text.startswith("@"):
                handle = text[1:]
                link["href"] = f"https://bsky.app/profile/{handle}"
                link.string = text
            elif href.startswith("/profile/"):
                link["href"] = f"https://bsky.app{href}"

        for link in clone.select('a[href^="http"]'):
            href = link.get("href", "")
            text = link.get_text(strip=True)
            link["href"] = href
            link.string = text

        for el in clone.select("span, div"):
            el.unwrap()

        html = (clone.decode_contents() or clone.get_text() or "").strip()
        html = html.replace("\u200e", "").replace("\u200f", "").replace("\u200b", "")
        html = html.replace(r"[^\S\n]+", " ").strip()

        if not html:
            return ""

        paragraphs = [p.strip() for p in html.split("\n") if p.strip()]
        return "\n".join(f"<p>{p}</p>" for p in paragraphs)

    def _extract_images(self, item: Tag) -> str:
        images: List[str] = []

        for img in item.select('img[src*="/feed_thumbnail/"], img[src*="/feed_fullsize/"]'):
            src = img.get("src", "")
            if not src:
                continue
            full_src = src.replace("/feed_thumbnail/", "/feed_fullsize/")
            images.append(f'<img src="{escape_html(full_src)}" alt="" />')

        return "\n".join(images)

    def _extract_link_card(self, item: Tag) -> str:
        links = item.select('a[aria-label][href^="http"]')
        for link in links:
            has_border = link.select_one('div[style*="border"]')
            if not has_border:
                continue

            href = link.get("href", "")
            title = link.get("aria-label", "")
            img = link.select_one("img")

            if title:
                html = ""
                if img:
                    src = img.get("src", "")
                    html += f'<a href="{escape_html(href)}"><img src="{escape_html(src)}" alt="{escape_html(title)}" /></a>\n'
                html += f'<p><a href="{escape_html(href)}">{escape_html(title)}</a></p>'
                return html

        return ""

    def _extract_quoted_post(self, item: Tag) -> str:
        embeds = item.select('[data-testid^="postThreadItem-by-"]')
        for embed in embeds:
            if embed is item:
                continue

            handle = self._get_handle(embed)
            display_name = self._get_display_name(embed)
            text_div = embed.select_one('div[data-word-wrap="1"]')
            text = self._clean_text(text_div) if text_div else ""

            author = f"{display_name} @{handle}" if display_name else f"@{handle}"
            return build_quoted_post(type("QuotedPostData", (), {"author": author, "content": text})())

        return ""

    def _create_description(self, item: Tag) -> str:
        text_div = item.select_one('div[data-word-wrap="1"]')
        if not text_div:
            return ""
        return (
            (text_div.get_text() or "")
            .replace("\u200e", "")
            .replace("\u200f", "")
            .replace("\u200b", "")
            .strip()[:140]
            .replace(r"\s+", " ")
        )
