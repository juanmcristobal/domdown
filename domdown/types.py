from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class DomdownOptions:
    base_url: str | None = None
    preserve_images: bool = True
    preserve_tables: bool = True
    preserve_code_blocks: bool = True
    strip_hidden: bool = True
    remove_selectors: tuple[str, ...] = ()
    keep_selectors: tuple[str, ...] = ()
    unwrap_selectors: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class HtmlToMarkdownResult:
    markdown: str
    cleaned_html: str | None = None
    warnings: tuple[str, ...] = ()


@dataclass(slots=True)
class PipelineContext:
    html: str
    options: DomdownOptions
    document: Any | None = None
    cleaned_html: str | None = None
    markdown: str = ""
    warnings: list[str] = field(default_factory=list)
