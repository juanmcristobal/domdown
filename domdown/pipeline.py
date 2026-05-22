from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from .stages.base import PipelineStage
from .stages.clean import CleanStage
from .stages.markdown import MarkdownStage
from .stages.parse import ParseStage
from .stages.postprocess import PostProcessStage
from .stages.preserve import PreserveStage
from .types import DomdownOptions, HtmlToMarkdownResult, PipelineContext


@dataclass(slots=True)
class HtmlToMarkdownPipeline:
    options: DomdownOptions | None = None
    stages: Sequence[PipelineStage] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.stages:
            self.stages = (
                ParseStage(),
                CleanStage(),
                PreserveStage(),
                MarkdownStage(),
                PostProcessStage(),
            )

    def run(self, html: str) -> HtmlToMarkdownResult:
        context = PipelineContext(html=html, options=self.options or DomdownOptions())
        for stage in self.stages:
            context = stage.run(context)
        return HtmlToMarkdownResult(
            markdown=context.markdown,
            cleaned_html=context.cleaned_html,
            warnings=tuple(context.warnings),
        )
