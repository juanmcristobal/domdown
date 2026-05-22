from __future__ import annotations

from typing import Protocol

from ..types import PipelineContext


class PipelineStage(Protocol):
    name: str

    def run(self, context: PipelineContext) -> PipelineContext:
        raise NotImplementedError
