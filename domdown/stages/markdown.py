"""Stage interface for Markdown rendering."""

from __future__ import annotations

from dataclasses import dataclass

from ..types import PipelineContext


@dataclass(slots=True)
class MarkdownStage:
    """Convert the cleaned document into Markdown text."""

    name: str = "markdown"

    def run(self, context: PipelineContext) -> PipelineContext:
        raise NotImplementedError("MarkdownStage is not implemented yet")
