"""Stage interface for Markdown rendering."""

from __future__ import annotations

from dataclasses import dataclass

from ..markdown import render_markdown
from ..types import PipelineContext


@dataclass(slots=True)
class MarkdownStage:
    """Convert the cleaned document into Markdown text."""

    name: str = "markdown"

    def run(self, context: PipelineContext) -> PipelineContext:
        if context.document is None:
            return context
        context.markdown = render_markdown(context.document, context.options)
        return context
