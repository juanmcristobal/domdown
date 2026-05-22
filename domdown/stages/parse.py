from __future__ import annotations

from dataclasses import dataclass

from ..types import PipelineContext


@dataclass(slots=True)
class ParseStage:
    name: str = "parse"

    def run(self, context: PipelineContext) -> PipelineContext:
        raise NotImplementedError("ParseStage is not implemented yet")
