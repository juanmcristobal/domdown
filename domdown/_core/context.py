from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .metadata import HtmlMetadata
from .options import DomdownOptions
from .criteria import ExtractionCriteria, ExtractionTrace, ExtractionPlan


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
    extraction_criteria: ExtractionCriteria | None = None
    extraction_trace: ExtractionTrace | None = None
    extraction_plan: ExtractionPlan | None = None
    node_ids: dict[int, Any] = field(default_factory=dict)
    node_refs: list[Any] = field(default_factory=list)
    node_descriptors: dict[int, dict[str, Any]] = field(default_factory=dict)
    selected_root_id: int | None = None
    selected_strategy: str | None = None
    cleanup_removed_node_ids: tuple[int, ...] = ()
    adapter_trace: list[dict[str, Any]] = field(default_factory=list)
    reproducibility_limitations: list[str] = field(default_factory=list)
