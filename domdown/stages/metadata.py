"""Stage interface for metadata extraction."""

from __future__ import annotations

from dataclasses import dataclass

from ..types import PipelineContext


@dataclass(slots=True)
class MetadataStage:
    """Extract normalized article metadata from the parsed document."""

    name: str = "metadata"

    def run(self, context: PipelineContext) -> PipelineContext:
        raise NotImplementedError("MetadataStage is not implemented yet")
