"""Stage interface for structural cleanup."""

from __future__ import annotations

from dataclasses import dataclass

from .._constants import DEFAULT_REMOVE_SELECTORS, SKIP_TAGS
from .._core import PipelineContext
from .._document import choose_root, clean_root


@dataclass(slots=True)
class CleanStage:
    """Remove noise and normalize the document before preservation."""

    name: str = "clean"

    def run(self, context: PipelineContext) -> PipelineContext:
        """Choose the main content root and strip irrelevant nodes."""

        if context.document is None:
            return context
        root = choose_root(context.document, context.options.prefer_article_body)
        root = clean_root(root, context.options.remove_selectors or DEFAULT_REMOVE_SELECTORS, SKIP_TAGS)
        context.document = root
        context.cleaned_html = str(root)
        return context
