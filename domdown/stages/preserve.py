"""Stage interface for preserving useful semantic blocks."""

from __future__ import annotations

from dataclasses import dataclass

from ..types import PipelineContext


@dataclass(slots=True)
class PreserveStage:
    """Mark or normalize content that must survive Markdown conversion."""

    name: str = "preserve"

    def run(self, context: PipelineContext) -> PipelineContext:
        raise NotImplementedError("PreserveStage is not implemented yet")
