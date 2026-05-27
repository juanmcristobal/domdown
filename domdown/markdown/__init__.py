from __future__ import annotations

from bs4 import Tag

from .._core import DomdownOptions
from .._text import normalize_markdown_text
from .block import render_block
from .postprocess import postprocess_markdown

__all__ = ["postprocess_markdown", "render_markdown"]


def render_markdown(root: Tag, options: DomdownOptions) -> str:
    """Render a cleaned HTML subtree into Markdown text."""

    parts = [part for part in (render_block(child, options) for child in root.children) if part]
    return normalize_markdown_text("\n\n".join(parts))
