from __future__ import annotations

from dataclasses import dataclass

from ..types import PipelineContext


@dataclass(slots=True)
class CleanStage:
    name: str = "clean"

    def run(self, context: PipelineContext) -> PipelineContext:
        raise NotImplementedError("CleanStage is not implemented yet")
