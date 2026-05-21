from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from bs4 import Tag

from domdown.extractors._base import BaseExtractor, ExtractorOptions
from domdown.types import ExtractorResult
from domdown.utils.dom import parse_html

INJECTED_ATTR = "data-domdown-nyt"


class NytimesExtractor(BaseExtractor):
    def __init__(
        self,
        document: Tag,
        url: str,
        schema_org_data: Any = None,
        options: Optional[ExtractorOptions] = None,
    ):
        super().__init__(document, url, schema_org_data, options)
        self.preloaded_data: Optional[Dict[str, Any]] = None
        self.content_selector: Optional[str] = None

        self.preloaded_data = self._extract_preload_data()

        if self.preloaded_data:
            body = self.preloaded_data.get("sprinkledBody") or self.preloaded_data.get("body")
            if body and body.get("content"):
                existing = self.document.select_one(f"[{INJECTED_ATTR}]")
                if not existing:
                    wrapper = Tag(name="div")
                    wrapper[INJECTED_ATTR] = ""
                    rendered = self._render_blocks(body["content"])
                    parsed = parse_html(rendered)
                    wrapper.append(parsed)
                    if self.document.body:
                        self.document.body.append(wrapper)
                self.content_selector = f"[{INJECTED_ATTR}]"

    def can_extract(self) -> bool:
        return self.content_selector is not None

    def extract(self) -> ExtractorResult:
        article = self.preloaded_data

        title = article.get("headline", {}).get("default", "") if article else ""

        bylines = article.get("bylines", []) if article else []
        authors = ""
        if bylines:
            first_byline = bylines[0]
            creators = first_byline.get("creators", [])
            author_names = [c.get("displayName", "") for c in creators if c.get("displayName")]
            authors = ", ".join(author_names)

        published = article.get("firstPublished", "") if article else ""
        description = article.get("summary", "") if article else ""

        return ExtractorResult(
            content="",
            content_html="",
            content_selector=self.content_selector,
            variables={
                "title": title,
                "author": authors,
                "published": published,
                "description": description,
            },
        )

    def _extract_preload_data(self) -> Optional[Dict[str, Any]]:
        scripts = self.document.select("script:not([src])")
        for script in scripts:
            text = script.get_text()
            if "window.__preloadedData" not in text:
                continue

            match = re.search(r"window\.__preloadedData\s*=\s*(\{[\s\S]+?\})\s*;?\s*$", text)
            if not match:
                continue

            try:
                raw = match.group(1)
                raw = re.sub(r"(?<=:)undefined(?=[,}\]])", "null", raw)
                data = json.loads(raw)
                initial_data = data.get("initialData", {})
                article_data = initial_data.get("data", {})
                return article_data.get("article")
            except Exception:
                return None

        return None

    def _render_blocks(self, blocks: List[Dict[str, Any]]) -> str:
        parts: List[str] = []

        for block in blocks:
            block_type = block.get("__typename", "")

            if block_type == "ParagraphBlock":
                content = block.get("content", [])
                parts.append(f"<p>{self._render_inlines(content)}</p>")

            elif block_type == "Heading2Block":
                content = block.get("content", [])
                parts.append(f"<h2>{self._render_inlines(content)}</h2>")

            elif block_type == "Heading3Block":
                content = block.get("content", [])
                parts.append(f"<h3>{self._render_inlines(content)}</h3>")

            elif block_type == "Heading4Block":
                content = block.get("content", [])
                parts.append(f"<h4>{self._render_inlines(content)}</h4>")

            elif block_type == "ImageBlock":
                media = block.get("media")
                if not media:
                    break

                src = self._get_best_image_url(media)
                if not src:
                    break

                alt = self._escape_attr(media.get("altText") or media.get("caption", {}).get("text", ""))
                caption_text = media.get("caption", {}).get("text", "")
                credit = media.get("credit", "")

                figcaption_parts = [caption_text, credit]
                figcaption = " ".join([p for p in figcaption_parts if p])

                if figcaption:
                    parts.append(
                        f"<figure>"
                        f'<img src="{self._escape_attr(src)}" alt="{alt}">'
                        f"<figcaption>{self._escape_html(figcaption)}</figcaption>"
                        f"</figure>"
                    )
                else:
                    parts.append(f'<img src="{self._escape_attr(src)}" alt="{alt}">')

            elif block_type in ("HeaderBasicBlock", "Dropzone"):
                pass

            else:
                content = block.get("content", [])
                if content:
                    parts.append(f"<p>{self._render_inlines(content)}</p>")

        return "\n".join(parts)

    def _render_inlines(self, inlines: Optional[List[Dict[str, Any]]]) -> str:
        if not inlines:
            return ""

        result = ""
        for inline in inlines:
            text = self._escape_html(inline.get("text", ""))
            formats = inline.get("formats", [])

            if not formats:
                result += text
                continue

            for fmt in formats:
                fmt_type = fmt.get("__typename", "")
                if fmt_type == "BoldFormat":
                    text = f"<strong>{text}</strong>"
                elif fmt_type == "ItalicFormat":
                    text = f"<em>{text}</em>"
                elif fmt_type == "LinkFormat":
                    url = fmt.get("url")
                    if url:
                        text = f'<a href="{self._escape_attr(url)}">{text}</a>'

            result += text

        return result

    def _get_best_image_url(self, media: Optional[Dict[str, Any]]) -> Optional[str]:
        crops = media.get("crops", []) if media else []
        if not crops:
            return None

        preferred = ["superJumbo", "jumbo", "articleLarge"]

        for name in preferred:
            for crop in crops:
                renditions = crop.get("renditions", [])
                for rendition in renditions:
                    if rendition.get("name") == name and rendition.get("url"):
                        return rendition["url"]

        for crop in crops:
            renditions = crop.get("renditions", [])
            if renditions and renditions[0].get("url"):
                return renditions[0]["url"]

        return None

    def _escape_html(self, text: str) -> str:
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def _escape_attr(self, text: str) -> str:
        return text.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")
