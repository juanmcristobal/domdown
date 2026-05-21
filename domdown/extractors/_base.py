from __future__ import annotations

from typing import Any, Callable, Optional

from bs4 import Tag

from domdown.types import ExtractorResult


class ExtractorOptions:
    include_replies: bool | str
    language: Optional[str]
    fetch: Optional[Callable]

    def __init__(
        self,
        include_replies: bool | str = "extractors",
        language: Optional[str] = None,
        fetch: Optional[Callable] = None,
    ):
        self.include_replies = include_replies
        self.language = language
        self.fetch = fetch


class BaseExtractor:
    def __init__(
        self,
        document: Tag,
        url: str,
        schema_org_data: Any = None,
        options: Optional[ExtractorOptions] = None,
    ):
        self.document = document
        self.url = url
        self.schema_org_data = schema_org_data
        self.options = options or ExtractorOptions()

    def can_extract(self) -> bool:
        raise NotImplementedError

    def extract(self) -> ExtractorResult:
        raise NotImplementedError

    def can_extract_async(self) -> bool:
        return False

    def prefers_async(self) -> bool:
        return False

    async def extract_async(self) -> ExtractorResult:
        return self.extract()

    def post_title(self, author: str, site: str) -> str:
        return f"Post by {author} on {site}"
