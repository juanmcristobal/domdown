from __future__ import annotations

from typing import Any, Optional

from bs4 import Tag

from domdown.extractors._base import BaseExtractor, ExtractorOptions
from domdown.types import ExtractorResult
from domdown.utils.dom import closest


class MediumExtractor(BaseExtractor):
    def __init__(
        self,
        document: Tag,
        url: str,
        schema_org_data: Any = None,
        options: Optional[ExtractorOptions] = None,
    ):
        super().__init__(document, url, schema_org_data, options)
        self.article: Optional[Tag] = None
        article = document.select_one("article.meteredContent")
        if article:
            self.article = article
        else:
            self.article = document.select_one("article")

    def can_extract(self) -> bool:
        if not self.article:
            return False

        article_class = self.article.get("class") or []
        article_classes = article_class.split() if isinstance(article_class, str) else article_class
        if "meteredContent" in article_classes:
            return True

        site_name_tag = self.document.select_one('meta[property="og:site_name"]')
        site_name = site_name_tag.get("content", "") if site_name_tag else ""
        app_name_tag = self.document.select_one('meta[property="al:android:app_name"]')
        app_name = app_name_tag.get("content", "") if app_name_tag else ""

        return site_name == "Medium" or app_name == "Medium"

    def extract(self) -> ExtractorResult:
        title = self._get_title()
        subtitle = self._get_subtitle()
        author = self._get_author()
        publication = self._get_publication()

        self._clean_article()
        description = subtitle or self._get_description()

        return ExtractorResult(
            content="",
            content_html="",
            content_selector="article",
            extracted_content={"publication": publication} if publication else None,
            variables={
                "title": title,
                "author": author,
                "site": publication or "Medium",
                "description": description,
            },
        )

    def _clean_article(self) -> None:
        if not self.article:
            return

        for btn in self.article.select('figure [role="button"]'):
            btn.unwrap()

        for el in self.article.select('[role="tooltip"]'):
            if el.get("role"):
                del el["role"]

        for link in self.article.select('a[href*="medium.com/plans"]'):
            wrapper = closest(link, "div")
            if wrapper and wrapper is not self.article:
                wrapper.decompose()
            else:
                link.decompose()

        for el in self.article.select('[data-testid="post-preview"]'):
            el.decompose()

        for el in self.article.select(
            '[data-testid*="Clap"], [data-testid*="Bookmark"], [data-testid*="Share"], [data-testid*="Response"]'
        ):
            el.decompose()

        for el in self.article.select(
            '[data-testid="authorPhoto"], [data-testid="authorName"], [data-testid="storyReadTime"]'
        ):
            el.decompose()

        ui_text = {
            "Member-only story",
            "Listen",
            "Share",
            "Top highlight",
            "·",
            "Press enter or click to view image in full size",
        }

        for el in self.article.select("p, span, div"):
            text = el.get_text().strip()
            if not text:
                continue
            if text in ui_text:
                el.decompose()
                continue
            import re

            if re.match(r"^\w{3}\s+\d{1,2},\s+\d{4}$", text) and len(text) < 30:
                el.decompose()
                continue
            if re.match(r"^·\s*\d+\s*\w+\s*ago$", text):
                el.decompose()
                continue
            if re.match(r"^·?\s*\d+\s*min\s*read$", text):
                el.decompose()

    def _get_title(self) -> str:
        story_title = self.document.select_one('[data-testid="storyTitle"]')
        if story_title:
            return story_title.get_text().strip()
        if self.article:
            h1 = self.article.select_one("h1")
            if h1:
                return h1.get_text().strip()
        return ""

    def _get_subtitle(self) -> str:
        subtitle = self.document.select_one(".pw-subtitle-paragraph")
        return subtitle.get_text().strip() if subtitle else ""

    def _get_author(self) -> str:
        author = self.document.select_one('[data-testid="authorName"]')
        return author.get_text().strip() if author else ""

    def _get_publication(self) -> str:
        meta = self.document.select_one('meta[property="og:site_name"]')
        site_name = meta.get("content", "") if meta else ""
        if site_name and site_name != "Medium":
            return site_name

        schemas = self.schema_org_data
        if not isinstance(schemas, list):
            schemas = [schemas] if schemas else []
        for schema in schemas:
            if schema and isinstance(schema, dict):
                publisher = schema.get("publisher") or {}
                if isinstance(publisher, dict):
                    pub_name = publisher.get("name")
                    if pub_name:
                        return pub_name

        return ""

    def _get_description(self) -> str:
        if not self.article:
            return ""
        paragraphs = self.article.select("p")
        for p in paragraphs:
            text = p.get_text().strip()
            import re

            if len(text) < 3 or re.match(r"^[\d\W]+$", text):
                continue
            return text[:140].replace(r"\s+", " ")
        return ""
