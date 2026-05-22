"""Data structures shared by the public API and pipeline stages."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class DomdownOptions:
    """Configuration for HTML parsing, cleanup, and output shaping."""

    base_url: str | None = None
    created: str | None = None
    extract_metadata: bool = True
    emit_frontmatter: bool = True
    prefer_article_body: bool = True
    frontmatter_tags: tuple[str, ...] = ()
    preserve_images: bool = True
    preserve_tables: bool = True
    preserve_code_blocks: bool = True
    strip_hidden: bool = True
    remove_selectors: tuple[str, ...] = ()
    keep_selectors: tuple[str, ...] = ()
    unwrap_selectors: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class HtmlToMarkdownResult:
    """Final output produced by the pipeline."""

    markdown: str
    cleaned_html: str | None = None
    metadata: "HtmlMetadata" | None = None
    frontmatter: str | None = None
    document: str | None = None
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class HtmlMetadata:
    """Normalized article metadata extracted from the source HTML."""

    title: str | None = None
    source: str | None = None
    author: tuple[str, ...] = ()
    published: str | None = None
    created: str | None = None
    description: str | None = None
    tags: tuple[str, ...] = ()
    language: str | None = None
    canonical_url: str | None = None
    image: str | None = None


@dataclass(slots=True)
class PipelineContext:
    """Mutable state passed between pipeline stages."""

    html: str
    options: DomdownOptions
    document: Any | None = None
    cleaned_html: str | None = None
    markdown: str = ""
    metadata: HtmlMetadata | None = None
    frontmatter: str | None = None
    rendered_document: str | None = None
    warnings: list[str] = field(default_factory=list)
