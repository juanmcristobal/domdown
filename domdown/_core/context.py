from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .metadata import HtmlMetadata
from .options import DomdownOptions


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
    matched_adapters: tuple[Any, ...] | None = None
