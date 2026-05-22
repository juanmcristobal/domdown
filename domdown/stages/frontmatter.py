"""Stage interface for frontmatter rendering."""

from __future__ import annotations

from dataclasses import dataclass

from .._core import PipelineContext
from .._frontmatter import compose_document, render_frontmatter


@dataclass(slots=True)
class FrontmatterStage:
    """Render extracted metadata into frontmatter when requested."""

    name: str = "frontmatter"

    def run(self, context: PipelineContext) -> PipelineContext:
        if context.metadata is None or not context.options.emit_frontmatter:
            context.rendered_document = context.markdown
            return context
        context.frontmatter = render_frontmatter(context.metadata)
        context.rendered_document = compose_document(context.frontmatter, context.markdown)
        return context
