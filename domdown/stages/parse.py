"""Stage interface for turning HTML into a parsed document."""

from __future__ import annotations

from dataclasses import dataclass

from .._core import PipelineContext
from .._document import parse_html


@dataclass(slots=True)
class ParseStage:
    """Build the document representation used by later stages."""

    name: str = "parse"

    def run(self, context: PipelineContext) -> PipelineContext:
        context.document = parse_html(context.html)
        return context
