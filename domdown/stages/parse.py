"""Stage interface for turning HTML into a parsed document."""

from __future__ import annotations

from dataclasses import dataclass

from ..rendering import parse_html
from ..types import PipelineContext


@dataclass(slots=True)
class ParseStage:
    """Build the document representation used by later stages."""

    name: str = "parse"

    def run(self, context: PipelineContext) -> PipelineContext:
        context.document = parse_html(context.html)
        return context
