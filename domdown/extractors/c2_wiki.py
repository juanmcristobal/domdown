from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from bs4 import Tag

from domdown.extractors._base import BaseExtractor, ExtractorOptions
from domdown.types import ExtractorResult
from domdown.utils.dom import escape_html, is_dangerous_url

C2_API = "https://c2.com/wiki/remodel/pages/"


class C2WikiExtractor(BaseExtractor):
    def __init__(
        self,
        document: Tag,
        url: str,
        schema_org_data: Any = None,
        options: Optional[ExtractorOptions] = None,
    ):
        super().__init__(document, url, schema_org_data, options)
        self.page_title: Optional[str] = None

    def can_extract(self) -> bool:
        return False

    def can_extract_async(self) -> bool:
        return self._get_page_title() is not None

    def prefers_async(self) -> bool:
        return True

    def extract(self) -> ExtractorResult:
        return ExtractorResult(content="", content_html="")

    async def extract_async(self) -> ExtractorResult:
        title = self._get_page_title()
        if not title:
            return ExtractorResult(content="", content_html="")

        try:
            response = await self.fetch(C2_API + title)
            json_data = response.json() if hasattr(response, "json") else await response.json()
        except Exception:
            return ExtractorResult(content="", content_html="")

        if not json_data or not json_data.get("text"):
            return ExtractorResult(content="", content_html="")

        words = re.sub(r"([a-z])([A-Z])", r"\1 \2", title)
        content_html = self._render_page(json_data)

        variables: Dict[str, str] = {
            "title": words,
            "site": "C2 Wiki",
        }
        if json_data.get("date"):
            variables["published"] = json_data["date"]

        return ExtractorResult(
            content=content_html,
            content_html=content_html,
            variables=variables,
        )

    def _get_page_title(self) -> Optional[str]:
        if self.page_title is not None:
            return self.page_title

        try:
            from urllib.parse import urlparse

            parsed = urlparse(self.url)
            search = parsed.query
            match = re.search(r"[?&]([A-Za-z]\w*)", search)
            self.page_title = match.group(1) if match else "WelcomeVisitors"
        except Exception:
            self.page_title = None

        return self.page_title

    def _render_page(self, json_data: Dict[str, Any]) -> str:
        body = self._markup(json_data.get("text", ""))
        footer = f"<hr><p>Last edit {escape_html(json_data.get('date', ''))}</p>" if json_data.get("date") else ""
        return f"{body}{footer}"

    def _markup(self, text: str) -> str:
        lines = text.replace("\\n", " ").split("\n")
        parts: List[str] = []
        open_tags: List[str] = []

        for line in lines:
            result = self._apply_bullets(line, open_tags)
            parts.append(self._apply_inline(result["html"]))
            open_tags = result["open_tags"]

        while open_tags:
            parts.append(f"</{open_tags.pop()}>")

        return "\n".join(parts)

    def _apply_bullets(self, text: str, open_tags: List[str]) -> Dict[str, Any]:
        new_open_tags = list(open_tags)
        prefix = ""

        def close_to_depth(depth: int, tag: Optional[str] = None) -> None:
            nonlocal prefix
            while len(new_open_tags) > depth:
                prefix += f"</{new_open_tags.pop()}>"
            if tag and len(new_open_tags) < depth:
                prefix += f"<{tag}>"
                new_open_tags.append(tag)
            elif tag and len(new_open_tags) == depth and new_open_tags[depth - 1] != tag:
                prefix += f"</{new_open_tags.pop()}><{tag}>"
                new_open_tags.append(tag)

        if re.match(r"^\s*$", text):
            in_list = any(t in ("ul", "ol", "dl") for t in new_open_tags)
            if in_list:
                return {"html": "", "open_tags": new_open_tags}
            close_to_depth(0)
            return {"html": prefix + "<p></p>", "open_tags": new_open_tags}

        if re.match(r"^-----*", text):
            close_to_depth(0)
            return {"html": prefix + "<hr>", "open_tags": new_open_tags}

        dl_match = re.match(r"^(\t+)(.+):\t", text)
        if dl_match:
            close_to_depth(len(dl_match.group(1)), "dl")
            return {
                "html": prefix + f"<dt>{dl_match.group(2)}<dd>" + text[len(dl_match.group(0)) :],
                "open_tags": new_open_tags,
            }

        tab_ul_match = re.match(r"^(\t+)\*", text)
        if tab_ul_match:
            close_to_depth(len(tab_ul_match.group(1)), "ul")
            return {"html": prefix + "<li>" + text[len(tab_ul_match.group(0)) :], "open_tags": new_open_tags}

        star_ul_match = re.match(r"^(\*+)", text)
        if star_ul_match:
            close_to_depth(len(star_ul_match.group(1)), "ul")
            return {"html": prefix + "<li>" + text[len(star_ul_match.group(0)) :], "open_tags": new_open_tags}

        ol_match = re.match(r"^(\t+)\d+\.?", text)
        if ol_match:
            close_to_depth(len(ol_match.group(1)), "ol")
            return {"html": prefix + "<li>" + text[len(ol_match.group(0)) :], "open_tags": new_open_tags}

        if re.match(r"^\s", text):
            close_to_depth(1, "pre")
            return {"html": prefix + text, "open_tags": new_open_tags}

        close_to_depth(0)
        return {"html": prefix + text, "open_tags": new_open_tags}

    def _apply_inline(self, text: str) -> str:
        text = re.sub(r"'''(.*?)'''", r"<strong>\1</strong>", text)
        text = re.sub(r"''(.*?)''", r"<em>\1</em>", text)

        def replace_url(url: str) -> str:
            if is_dangerous_url(url):
                return escape_html(url)
            if re.search(r"\.(gif|jpg|jpeg|png)$", url, re.IGNORECASE):
                return f'<img src="{_escape_attr(url)}">'
            return f'<a href="{_escape_attr(url)}" rel="nofollow" target="_blank">{escape_html(url)}</a>'

        text = re.sub(
            r'\b(https?|ftp|mailto|file|telnet|news):[^\s<>[\]"' + r"'" + r'()]*[^\s<>[\]"' + r"'" + r",.?]",
            replace_url,
            text,
        )

        return text


def _escape_attr(text: str) -> str:
    return text.replace('"', "&quot;").replace("'", "&#39;")
