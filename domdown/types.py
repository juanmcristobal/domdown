from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union


@dataclass
class DomdownMetadata:
    title: str = ""
    description: str = ""
    domain: str = ""
    favicon: str = ""
    image: str = ""
    language: str = ""
    parse_time: float = 0.0
    published: str = ""
    author: str = ""
    site: str = ""
    schema_org_data: Any = None
    word_count: int = 0


@dataclass
class MetaTagItem:
    name: Optional[str] = None
    property: Optional[str] = None
    content: Optional[str] = None


@dataclass
class DebugRemoval:
    step: str = ""
    selector: Optional[str] = None
    reason: Optional[str] = None
    text: str = ""


@dataclass
class DebugInfo:
    content_selector: str = ""
    removals: List[DebugRemoval] = field(default_factory=list)


@dataclass
class ConversationMessage:
    role: str = ""
    content: str = ""


@dataclass
class ConversationMetadata:
    messages: List[ConversationMessage] = field(default_factory=list)


@dataclass
class Footnote:
    id: str = ""
    content: str = ""


@dataclass
class DomdownResponse:
    title: str = ""
    description: str = ""
    domain: str = ""
    favicon: str = ""
    image: str = ""
    language: str = ""
    parse_time: float = 0.0
    published: str = ""
    author: str = ""
    site: str = ""
    schema_org_data: Any = None
    word_count: int = 0
    content: str = ""
    content_markdown: Optional[str] = None
    extractor_type: Optional[str] = None
    meta_tags: Optional[List[MetaTagItem]] = None
    debug: Optional[DebugInfo] = None
    profile: Optional[Dict[str, float]] = None
    variables: Optional[Dict[str, str]] = None


@dataclass
class DomdownOptions:
    debug: bool = False
    url: Optional[str] = None
    markdown: bool = False
    separate_markdown: bool = False
    remove_exact_selectors: bool = True
    remove_partial_selectors: bool = True
    remove_images: bool = False
    use_async: bool = True
    remove_hidden_elements: bool = True
    remove_low_scoring: bool = True
    remove_small_images: bool = True
    standardize: bool = True
    remove_content_patterns: bool = True
    content_selector: Optional[str] = None
    language: Optional[str] = None
    include_replies: Union[bool, str] = "extractors"
    profile: bool = False
    fetch: Any = None


@dataclass
class ExtractorVariables:
    _store: Dict[str, str] = field(default_factory=dict)

    def __getitem__(self, key: str) -> str:
        return self._store[key]

    def __setitem__(self, key: str, value: str) -> None:
        self._store[key] = value

    def __contains__(self, key: str) -> bool:
        return key in self._store

    def __iter__(self):
        return iter(self._store)

    def items(self):
        return self._store.items()

    def keys(self):
        return self._store.keys()

    def values(self):
        return self._store.values()


@dataclass
class ExtractedContent:
    title: Optional[str] = None
    author: Optional[str] = None
    published: Optional[str] = None
    content: Optional[str] = None
    content_html: Optional[str] = None
    variables: Optional[ExtractorVariables] = None


@dataclass
class ExtractorResult:
    title: Optional[str] = None
    author: Optional[str] = None
    published: Optional[str] = None
    content: Optional[str] = None
    content_html: Optional[str] = None
    content_selector: Optional[str] = None
    extracted_content: Optional[Dict[str, Any]] = None
    variables: Optional[Dict[str, str]] = None
    extractor_type: Optional[str] = None
    messages: Optional[List[ConversationMessage]] = None

    def get(self, key: str, default: Any = None) -> Any:
        field_map = {
            "contentSelector": "content_selector",
            "contentHtml": "content_html",
            "extractedContent": "extracted_content",
        }
        python_key = field_map.get(key, key)
        if hasattr(self, python_key):
            value = getattr(self, python_key)
            if value is not None:
                return value
        return default
