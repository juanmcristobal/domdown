"""Stage interface for Markdown post-processing."""

from __future__ import annotations

from dataclasses import dataclass

from ..markdown import postprocess_markdown
from ..types import PipelineContext


@dataclass(slots=True)
class PostProcessStage:
    """Normalize the final Markdown output for readability and stability."""

    name: str = "postprocess"

    def run(self, context: PipelineContext) -> PipelineContext:
        context.markdown = postprocess_markdown(context.markdown)
        return context
