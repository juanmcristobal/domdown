"""Stage interface for Markdown post-processing."""

from __future__ import annotations

from dataclasses import dataclass

from ..types import PipelineContext


@dataclass(slots=True)
class PostProcessStage:
    """Normalize the final Markdown output for readability and stability."""

    name: str = "postprocess"

    def run(self, context: PipelineContext) -> PipelineContext:
        raise NotImplementedError("PostProcessStage is not implemented yet")
