"""Stage interface for structural cleanup."""

from __future__ import annotations

from dataclasses import dataclass

from ..constants import DEFAULT_REMOVE_SELECTORS, SKIP_TAGS
from ..document import choose_root, clean_root
from ..types import PipelineContext


@dataclass(slots=True)
class CleanStage:
    """Remove noise and normalize the document before preservation."""

    name: str = "clean"

    def run(self, context: PipelineContext) -> PipelineContext:
        if context.document is None:
            return context
        root = choose_root(context.document, context.options.prefer_article_body)
        root = clean_root(root, context.options.remove_selectors or DEFAULT_REMOVE_SELECTORS, SKIP_TAGS)
        context.document = root
        context.cleaned_html = str(root)
        return context
