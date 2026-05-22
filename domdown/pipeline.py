"""Pipeline orchestration for HTML to Markdown extraction."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from .stages.base import PipelineStage
from .stages.clean import CleanStage
from .stages.frontmatter import FrontmatterStage
from .stages.markdown import MarkdownStage
from .stages.metadata import MetadataStage
from .stages.parse import ParseStage
from .stages.postprocess import PostProcessStage
from .stages.preserve import PreserveStage
from .types import DomdownOptions, HtmlToMarkdownResult, PipelineContext


@dataclass(slots=True)
class HtmlToMarkdownPipeline:
    """Orchestrate the ordered stages that transform HTML into Markdown."""

    options: DomdownOptions | None = None
    stages: Sequence[PipelineStage] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        """Populate the default stage chain when none is supplied."""

        if not self.stages:
            self.stages = (
                ParseStage(),
                MetadataStage(),
                CleanStage(),
                PreserveStage(),
                MarkdownStage(),
                PostProcessStage(),
                FrontmatterStage(),
            )

    def run(self, html: str) -> HtmlToMarkdownResult:
        """Run the configured pipeline over raw HTML and return the result."""

        context = PipelineContext(html=html, options=self.options or DomdownOptions())
        for stage in self.stages:
            context = stage.run(context)
        return HtmlToMarkdownResult(
            markdown=context.markdown,
            cleaned_html=context.cleaned_html,
            metadata=context.metadata,
            frontmatter=context.frontmatter,
            document=context.rendered_document,
            warnings=tuple(context.warnings),
        )
