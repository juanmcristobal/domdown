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
            before = _present_node_ids(context)
            context = adapter.preprocess(context)
            removed = sorted(before - _present_node_ids(context))
            context.adapter_trace.append(
                {"name": adapter.name, "hook": "preprocess", "removed_node_ids": removed}
            )
        return context

    def preprocess_for_criteria(self, context: PipelineContext) -> PipelineContext:
        """Apply only non-extraction setup while an explicit criteria owns DOM filtering."""
        for adapter in self.matching(context):
            hook = getattr(adapter, "preprocess_for_criteria", None)
            if hook is not None:
                context = hook(context)
        return context

    def post_clean(self, context: PipelineContext) -> PipelineContext:
        """Run deferred source filters after generic extraction has selected a root."""
        for adapter in self.matching(context):
            hook = getattr(adapter, "post_clean", None)
            if hook is None:
                continue
            before = _present_node_ids(context)
            context = hook(context)
            removed = sorted(before - _present_node_ids(context))
            if removed:
                context.adapter_trace.append(
                    {"name": adapter.name, "hook": "post_clean", "removed_node_ids": removed}
                )
        return context

    def refine_metadata(self, context: PipelineContext) -> PipelineContext:
        """Run metadata refinement hooks for matching adapters."""

        for adapter in self.matching(context):
            before_document = context.document
            before = _present_node_ids(context)
            context = adapter.refine_metadata(context)
            removed = sorted(before - _present_node_ids(context))
            if context.document is not before_document:
                context.adapter_trace.append({"name": adapter.name, "hook": "refine_metadata", "selected_subtree": True, "removed_node_ids": removed})
            elif removed:
                context.adapter_trace.append({"name": adapter.name, "hook": "refine_metadata", "removed_node_ids": removed})
        return context

    def postprocess(self, context: PipelineContext) -> PipelineContext:
        """Run post-processing hooks for matching adapters."""

        for adapter in self.matching(context):
            before = context.markdown
            context = adapter.postprocess(context)
            if context.markdown != before:
                context.adapter_trace.append({"name": adapter.name, "hook": "postprocess", "markdown_changed": True})
        return context


def build_default_registry(adapters: Sequence[ArticleAdapter] | None = None) -> AdapterRegistry:
    """Create a registry for the supplied adapters."""

    return AdapterRegistry(adapters=tuple(adapters or ()))


def _present_node_ids(context: PipelineContext) -> set[int]:
    document = context.document
    if document is None:
        return set()
    nodes = [document, *document.find_all(True)]
    return {context.node_ids[id(node)] for node in nodes if id(node) in context.node_ids}
