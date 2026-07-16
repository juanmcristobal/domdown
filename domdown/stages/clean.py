"""Stage interface for structural cleanup."""

from __future__ import annotations

from dataclasses import dataclass

from bs4 import Tag

from .._constants import DEFAULT_REMOVE_SELECTORS, JS_SHELL_PHRASES, SKIP_TAGS
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
        preserve_chrome = False
        if _root_is_empty(root):
            fallback = _fallback_root(context.document, root)
            if fallback is not None:
                root.decompose()
                root = fallback
        elif _looks_like_js_shell(root) and _body_has_more_content(context.document, root):
            body = context.document.body
            if body is not None:
                root.decompose()
                root = body
                preserve_chrome = True
        root = clean_root(
            root,
            context.options.remove_selectors or DEFAULT_REMOVE_SELECTORS,
            SKIP_TAGS,
            preserve_chrome=preserve_chrome,
        )
        context.document = root
        context.cleaned_html = str(root)
        return context


def _root_is_empty(root) -> bool:
    """Detect a selected shell that contains no visible text to render."""

    return not root.get_text(" ", strip=True)


def _fallback_root(document, current: Tag) -> Tag | None:
    """Return the first non-empty document-level fallback root."""

    candidates = (document.body, document.select_one("main"), document.html)
    for candidate in candidates:
        if isinstance(candidate, Tag) and candidate is not current and candidate.get_text(" ", strip=True):
            return candidate
    return None


def _looks_like_js_shell(root) -> bool:
    """Detect portal shells that only render placeholder text without JavaScript."""

    text = root.get_text(" ", strip=True).lower()
    return any(phrase in text for phrase in JS_SHELL_PHRASES)


def _body_has_more_content(document, root) -> bool:
    """Require a real body fallback only when the body is materially richer than the shell."""

    body = document.body
    if body is None:
        return False
    body_words = len(body.get_text(" ", strip=True).split())
    root_words = len(root.get_text(" ", strip=True).split())
    return body_words >= max(root_words + 8, 20)
