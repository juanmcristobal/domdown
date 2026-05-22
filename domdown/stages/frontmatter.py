"""Stage interface for frontmatter rendering."""

from __future__ import annotations

from dataclasses import dataclass

from ..types import PipelineContext


@dataclass(slots=True)
class FrontmatterStage:
    """Render extracted metadata into frontmatter when requested."""

    name: str = "frontmatter"

    def run(self, context: PipelineContext) -> PipelineContext:
        raise NotImplementedError("FrontmatterStage is not implemented yet")
