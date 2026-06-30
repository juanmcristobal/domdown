from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from .._core import PipelineContext
from .base import ArticleAdapter


@dataclass(slots=True)
class AdapterRegistry:
    """Hold optional article adapters and apply them in order."""

    adapters: Sequence[ArticleAdapter] = field(default_factory=tuple)

    def matching(self, context: PipelineContext) -> tuple[ArticleAdapter, ...]:
        """Return adapters that want to handle the current document."""

        if context.matched_adapters is not None:
            return tuple(context.matched_adapters)
        return tuple(adapter for adapter in self.adapters if adapter.matches(context))

    def preprocess(self, context: PipelineContext) -> PipelineContext:
        """Run pre-processing hooks for matching adapters."""

        for adapter in self.matching(context):
            context = adapter.preprocess(context)
        return context

    def refine_metadata(self, context: PipelineContext) -> PipelineContext:
        """Run metadata refinement hooks for matching adapters."""

        for adapter in self.matching(context):
            context = adapter.refine_metadata(context)
        return context

    def postprocess(self, context: PipelineContext) -> PipelineContext:
        """Run post-processing hooks for matching adapters."""

        for adapter in self.matching(context):
            context = adapter.postprocess(context)
        return context


def build_default_registry(adapters: Sequence[ArticleAdapter] | None = None) -> AdapterRegistry:
    """Create a registry for the supplied adapters."""

    return AdapterRegistry(adapters=tuple(adapters or ()))
