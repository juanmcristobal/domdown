"""Stage interface for metadata extraction."""

from __future__ import annotations

from dataclasses import dataclass

from ..metadata import extract_metadata
from ..types import PipelineContext


@dataclass(slots=True)
class MetadataStage:
    """Extract normalized article metadata from the parsed document."""

    name: str = "metadata"

    def run(self, context: PipelineContext) -> PipelineContext:
        if context.document is None:
            return context
        context.metadata = extract_metadata(context.document, context.options)
        return context
