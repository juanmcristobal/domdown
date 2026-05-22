from __future__ import annotations

from dataclasses import dataclass

from ..types import PipelineContext


@dataclass(slots=True)
class PreserveStage:
    name: str = "preserve"

    def run(self, context: PipelineContext) -> PipelineContext:
        raise NotImplementedError("PreserveStage is not implemented yet")
