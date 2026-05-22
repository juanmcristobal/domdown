"""Stage interface for Markdown post-processing."""

from __future__ import annotations

from dataclasses import dataclass

from .._core import PipelineContext
from ..markdown import postprocess_markdown


@dataclass(slots=True)
class PostProcessStage:
    """Normalize the final Markdown output for readability and stability."""

    name: str = "postprocess"

    def run(self, context: PipelineContext) -> PipelineContext:
        """Apply final Markdown cleanup to the current document text."""

        context.markdown = postprocess_markdown(context.markdown)
        return context
