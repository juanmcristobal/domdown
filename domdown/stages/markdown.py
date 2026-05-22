from __future__ import annotations

from dataclasses import dataclass

from ..types import PipelineContext


@dataclass(slots=True)
class MarkdownStage:
    name: str = "markdown"

    def run(self, context: PipelineContext) -> PipelineContext:
        raise NotImplementedError("MarkdownStage is not implemented yet")
