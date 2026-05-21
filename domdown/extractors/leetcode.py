from __future__ import annotations

from domdown.extractors._base import BaseExtractor
from domdown.types import ExtractorResult


class LeetCodeExtractor(BaseExtractor):
    def can_extract(self) -> bool:
        return self.document.select('[data-track-load="description_content"]') is not None

    def extract(self) -> ExtractorResult:
        og_title_tag = self.document.select_one('meta[property="og:title"]')
        og_title = og_title_tag.get("content", "") if og_title_tag else ""
        import re

        title = re.sub(r"\s*[-–—]\s*LeetCode\s*$", "", og_title) or og_title

        return ExtractorResult(
            content="",
            content_html="",
            content_selector='[data-track-load="description_content"]',
            variables={
                "title": title,
                "site": "LeetCode",
            },
        )
