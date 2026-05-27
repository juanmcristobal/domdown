from __future__ import annotations

from typing import Protocol

from .._core import PipelineContext


class ArticleAdapter(Protocol):
    """Optional family-specific hook that can refine a pipeline context."""

    name: str

    def matches(self, context: PipelineContext) -> bool:
        """Return True when the adapter should run for the given HTML."""

        raise NotImplementedError

    def preprocess(self, context: PipelineContext) -> PipelineContext:
        """Adjust the context before the core stages continue."""

        raise NotImplementedError

    def refine_metadata(self, context: PipelineContext) -> PipelineContext:
        """Adjust extracted metadata after the metadata stage has run."""

        raise NotImplementedError

    def postprocess(self, context: PipelineContext) -> PipelineContext:
        """Adjust the context after the core stages have finished."""

        raise NotImplementedError
