"""Shared interfaces for pipeline stages."""

from __future__ import annotations

from typing import Protocol

from ..types import PipelineContext


class PipelineStage(Protocol):
    """Contract implemented by every pipeline stage."""

    name: str

    def run(self, context: PipelineContext) -> PipelineContext:
        """Transform the pipeline context and return the updated context."""

        raise NotImplementedError
