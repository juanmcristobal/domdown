from __future__ import annotations

import json
from typing import Any, Optional

from bs4 import Tag

from domdown.extractors._base import BaseExtractor, ExtractorOptions
from domdown.types import ExtractorResult
from domdown.utils.bbcode import bbcode_to_html


class BbcodeDataExtractor(BaseExtractor):
    def __init__(
        self,
        document: Tag,
        url: str,
        schema_org_data: Any = None,
        options: Optional[ExtractorOptions] = None,
    ):
        super().__init__(document, url, schema_org_data, options)
        self.event_data = self._get_event_data()

    def can_extract(self) -> bool:
        event = self._get_event_data()
        return bool(event and event.get("announcement_body", {}).get("body"))

    def extract(self) -> ExtractorResult:
        event = self._get_event_data()
        body = event.get("announcement_body", {})
        content_html = bbcode_to_html(body.get("body", ""))
        title = body.get("headline") or event.get("event_name") or ""
        published = ""
        if body.get("posttime"):
            import time

            published = time.strftime("%Y-%m-%d", time.gmtime(body["posttime"]))
        author = self._get_group_name()

        return ExtractorResult(
            content=content_html,
            content_html=content_html,
            extracted_content=None,
            variables={
                "title": title,
                "author": author,
                "published": published,
            },
        )

    def _get_event_data(self) -> Optional[dict]:
        config = self.document.select_one("#application_config")
        if config is None:
            return None
        raw = config.get("data-partnereventstore")
        if not raw:
            return None
        try:
            parsed = json.loads(raw)
            return parsed[0] if isinstance(parsed, list) else parsed
        except (json.JSONDecodeError, IndexError, TypeError):
            return None

    def _get_group_name(self) -> str:
        config = self.document.select_one("#application_config")
        if config is None:
            return ""
        raw = config.get("data-groupvanityinfo")
        if not raw:
            return ""
        try:
            data = json.loads(raw)
            if isinstance(data, list):
                data = data[0]
            return data.get("group_name", "") if isinstance(data, dict) else ""
        except (json.JSONDecodeError, IndexError, TypeError):
            return ""
