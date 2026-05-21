from __future__ import annotations

import copy
import re
from typing import List, Optional

from bs4 import Tag

from domdown.extractors._base import BaseExtractor, ExtractorOptions
from domdown.types import ExtractorResult
from domdown.utils.comments import CommentData, build_comment_tree, build_content_html
from domdown.utils.dom import escape_html, serialize_html


class LwnExtractor(BaseExtractor):
    def __init__(
        self,
        document: Tag,
        url: str,
        schema_org_data: any = None,
        options: Optional[ExtractorOptions] = None,
    ):
        super().__init__(document, url, schema_org_data, options)

    def can_extract(self) -> bool:
        return bool(self.document.select_one(".PageHeadline")) and bool(self.document.select_one(".ArticleText"))

    def extract(self) -> ExtractorResult:
        main = self.document.select_one(".ArticleText main")
        article_content = self._get_article_content(main) if main else ""
        comments = self._extract_comments(main) if main and self.options.include_replies is not False else ""
        content_html = build_content_html("lwn", article_content, comments)

        byline = self.document.select_one(".Byline").get_text(strip=True) if self.document.select_one(".Byline") else ""

        title_elem = self.document.select_one(".PageHeadline h1")
        title = title_elem.get_text(strip=True) if title_elem else ""
        author_match = re.search(r"by\s+(\w+)", byline, re.IGNORECASE)
        author = author_match.group(1) if author_match else ""

        return ExtractorResult(
            content=content_html,
            content_html=content_html,
            variables={
                "title": title,
                "author": author,
                "site": "LWN.net",
                "published": self._parse_date(byline),
                "description": (
                    self.document.select_one('meta[property="og:description"]').get("content", "")
                    if self.document.select_one('meta[property="og:description"]')
                    else ""
                ),
            },
        )

    def _parse_date(self, text: str) -> str:
        match = re.search(r"Posted\s+(\w+\s+\d+,\s+\d{4})", text)
        if not match:
            return ""
        date_str = match.group(1)
        try:
            from datetime import datetime as dt

            date = dt.strptime(date_str, "%B %d, %Y")
            return date.strftime("%Y-%m-%d")
        except Exception:
            return ""

    def _get_article_content(self, main: Tag) -> str:
        clone = copy.copy(main)

        for el in clone.select("details.CommentBox, form, a[name^='Comm']"):
            el.decompose()

        last_el = clone.find_nextSibling()
        while last_el and (last_el.name == "hr" or (last_el.name == "br" and last_el.get("clear"))):
            prev = last_el.find_nextSibling()
            last_el.decompose()
            last_el = prev

        return serialize_html(clone)

    def _extract_comments(self, main: Tag) -> str:
        all_boxes = main.select("details.CommentBox")
        comment_data: List[CommentData] = []

        for box in all_boxes:
            depth = self._get_comment_depth(box, main)
            data = self._extract_comment_data(box, depth)
            if data:
                comment_data.append(data)

        return build_comment_tree(comment_data) if comment_data else ""

    def _get_comment_depth(self, el: Tag, root: Tag) -> int:
        depth = 0
        parent = el.parent
        while parent and parent != root:
            if parent.name == "details" and "CommentBox" in parent.get("class", []):
                depth += 1
            parent = parent.parent
        return depth

    def _extract_comment_data(self, box: Tag, depth: int) -> Optional[CommentData]:
        poster = box.select_one(":scope > summary .CommentPoster")
        if not poster:
            return None

        author_elem = poster.select_one("b")
        author = author_elem.get_text(strip=True) if author_elem else ""

        link_el = poster.select_one('a[href^="/Articles/"]')
        article_path = link_el.get("href", "") if link_el else ""
        url = f"https://lwn.net{article_path}" if article_path else ""

        date = self._parse_date(poster.get_text() or "")

        title_elem = box.select_one(":scope > summary h3.CommentTitle")
        title = title_elem.get_text(strip=True) if title_elem else ""

        parent_box = box.parent.select_one("details.CommentBox") if box.parent else None
        parent_title = (
            parent_box.select_one(":scope > summary h3.CommentTitle").get_text(strip=True)
            if parent_box and parent_box.select_one(":scope > summary h3.CommentTitle")
            else ""
        )
        unique_title = title if title and title != parent_title else ""

        content = self._get_comment_content(box, unique_title)

        return CommentData(author=author, date=date, content=content, depth=depth, url=url)

    def _get_comment_content(self, box: Tag, title: str) -> str:
        content = ""

        if title:
            content += f"<p><strong>{escape_html(title)}</strong></p>"

        formatted = box.select_one(":scope > .FormattedComment")
        if formatted:
            content += serialize_html(formatted)
        else:
            temp_container = Tag(name="div")
            for child in box.children:
                if hasattr(child, "name") and child.name:
                    tag = child.name
                    if tag in ("summary", "details") or "CommentReplyButton" in child.get("class", []):
                        continue
                    if tag == "form":
                        continue
                    if tag == "a" and child.get("name", "").startswith("CommAnchor"):
                        continue
                    if tag == "p" and not child.get_text(strip=True):
                        continue
                    temp_container.append(copy.copy(child))
            text = serialize_html(temp_container).strip()
            if text:
                content += text

        return content
