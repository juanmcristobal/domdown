from __future__ import annotations

from dataclasses import dataclass

from .metadata import HtmlMetadata
from .criteria import ExtractionCriteria, ExtractionTrace


@dataclass(frozen=True, slots=True)
class HtmlToMarkdownResult:
    """Final output produced by the pipeline."""

    markdown: str
    cleaned_html: str | None = None
    metadata: HtmlMetadata | None = None
    frontmatter: str | None = None
    document: str | None = None
    warnings: tuple[str, ...] = ()
    criteria: ExtractionCriteria | None = None
    trace: ExtractionTrace | None = None
