from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional

from bs4 import Tag

from domdown.extractors._base import BaseExtractor, ExtractorOptions
from domdown.types import ExtractorResult
from domdown.utils.dom import closest, parse_html

INJECTED_ATTR = "data-domdown-substack-post"


class SubstackExtractor(BaseExtractor):
    def __init__(
        self,
        document: Tag,
        url: str,
        schema_org_data: Any = None,
        options: Optional[ExtractorOptions] = None,
    ):
        super().__init__(document, url, schema_org_data, options)
        self.note_text: Optional[Tag] = None
        self.note_image: Optional[Tag] = None
        self.post_data: Optional[Dict[str, Any]] = None
        self.post_content_selector: Optional[str] = None

        if self.document.select_one("div.body.markup"):
            self.post_data = self._extract_preload_data()
            self.post_content_selector = "div.body.markup"
            return

        self.post_data = self._extract_preload_data()
        if self.post_data and self.post_data.get("body_html"):
            existing = self.document.select_one(f"[{INJECTED_ATTR}]")
            if not existing:
                wrapper = Tag(name="div")
                wrapper[INJECTED_ATTR] = ""
                rendered = self.post_data["body_html"]
                parsed = parse_html(rendered)
                wrapper.append(parsed)
                if self.document.body:
                    self.document.body.append(wrapper)
            self.post_content_selector = f"[{INJECTED_ATTR}]"
            return

        permalink_unit = self.document.select_one('[class*="feedPermalinkUnit"]')
        search_root = permalink_unit if permalink_unit else self.document
        self.note_text = search_root.select_one("div.ProseMirror.FeedProseMirror")

        if self.note_text:
            feed_comment_body = closest(
                self.note_text, '[class*="feedCommentBody"]:not([class*="feedCommentBodyInner"])'
            )
            if feed_comment_body:
                candidates = [
                    feed_comment_body.next_sibling,
                    feed_comment_body.parent.next_sibling if feed_comment_body.parent else None,
                ]
                for el in candidates:
                    if el:
                        el_class = el.get("class") or ""
                        if (
                            isinstance(el_class, str)
                            and "imageGrid" in el_class
                            or (isinstance(el_class, list) and any("imageGrid" in c for c in el_class))
                        ):
                            self.note_image = el
                            break

    def can_extract(self) -> bool:
        return self.post_content_selector is not None or self.note_text is not None

    def extract(self) -> ExtractorResult:
        if self.post_content_selector:
            return self._extract_post()
        return self._extract_note()

    def _extract_post(self) -> ExtractorResult:
        title = self.post_data.get("title", "") if self.post_data else ""
        if not title:
            og_title = self.document.select_one('meta[property="og:title"]')
            title = og_title.get("content", "") if og_title else ""

        description = self.post_data.get("subtitle", "") if self.post_data else ""
        if not description:
            og_desc = self.document.select_one('meta[property="og:description"]')
            description = og_desc.get("content", "") if og_desc else ""

        bylines = self.post_data.get("publishedBylines", []) if self.post_data else []
        author = bylines[0].get("name", "") if bylines else ""
        if not author:
            author_link = self.document.select_one('a[href*="substack.com/@"]')
            if author_link:
                author = author_link.get_text().strip()

        published = self.post_data.get("post_date", "") if self.post_data else ""
        if not published:
            published = self._parse_date_from_byline()

        return ExtractorResult(
            content="",
            content_html="",
            content_selector=self.post_content_selector,
            variables={
                "title": title,
                "author": author,
                "site": "Substack",
                "description": description,
                "published": published,
            },
        )

    def _extract_note(self) -> ExtractorResult:
        text_html = str(self.note_text) if self.note_text else ""
        image_html = self._build_image_html()
        content = f"{text_html}\n{image_html}" if image_html else text_html

        og_title = self.document.select_one('meta[property="og:title"]')
        title = og_title.get("content", "") if og_title else ""

        og_desc = self.document.select_one('meta[property="og:description"]')
        description = og_desc.get("content", "") if og_desc else ""

        author = re.sub(r"\s*\(@[^)]+\)\s*$", "", title).strip()

        return ExtractorResult(
            content=content,
            content_html=content,
            variables={
                "title": title,
                "author": author,
                "site": "Substack",
                "description": description,
            },
        )

    def _parse_date_from_byline(self) -> str:
        byline = self.document.select_one('[class*="byline-wrapper"]')
        if not byline:
            return ""

        text = byline.get_text().strip()
        text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)

        abbrev_months = "Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec"
        month_map = {
            "Jan": "01",
            "Feb": "02",
            "Mar": "03",
            "Apr": "04",
            "May": "05",
            "Jun": "06",
            "Jul": "07",
            "Aug": "08",
            "Sep": "09",
            "Oct": "10",
            "Nov": "11",
            "Dec": "12",
        }

        match = re.search(rf"\b({abbrev_months})\s+(\d{{1,2}}),?\s+(\d{{4}})\b", text)
        if match:
            month = month_map.get(match.group(1), "")
            day = match.group(2).zfill(2)
            return f"{match.group(3)}-{month}-{day}T00:00:00+00:00"

        return ""

    def _extract_preload_data(self) -> Optional[Dict[str, Any]]:
        scripts = list(self.document.select("script"))
        for script in scripts:
            text = script.get_text()
            if "window._preloads" not in text or "body_html" not in text:
                continue

            json_parse_idx = text.find('JSON.parse("')
            if json_parse_idx == -1:
                continue

            start_idx = json_parse_idx + len('JSON.parse("')
            i = start_idx
            while i < len(text):
                if text[i] == "\\":
                    i += 2
                elif text[i] == '"':
                    break
                else:
                    i += 1

            try:
                inner_str = text[start_idx:i]
                json_string = json.loads('"' + inner_str + '"')
                data = json.loads(json_string)
                feed_data = data.get("feedData", {})
                initial_post = feed_data.get("initialPost", {})
                post = initial_post.get("post")
                if post and post.get("body_html"):
                    return post
            except Exception:
                pass

        return None

    def _build_image_html(self) -> str:
        if not self.note_image:
            return ""

        og_image = self.document.select_one('meta[property="og:image"]')
        if og_image:
            content = og_image.get("content", "")
            if content:
                return f'<img src="{content}" alt="" />'

        img = self.note_image.select_one("img")
        if not img:
            return ""
        src = self._get_largest_src(img)
        return f'<img src="{src}" alt="" />' if src else ""

    def _get_largest_src(self, img: Tag) -> str:
        srcset = img.get("srcset", "")
        if srcset:
            entry_pattern = re.compile(r"(.+?)\s+(\d+(?:\.\d+)?)w")
            best_url = ""
            best_width = 0
            last_index = 0

            for match in entry_pattern.finditer(srcset):
                url = match.group(1).strip()
                if last_index > 0:
                    url = re.sub(r"^,\s*", "", url)
                last_index = match.end()
                width = float(match.group(2))
                if url and width > best_width:
                    best_width = width
                    best_url = url

            if best_url:
                return re.sub(r",w_\d+", "", re.sub(r",c_\w+", "", best_url))

        return img.get("src", "")
