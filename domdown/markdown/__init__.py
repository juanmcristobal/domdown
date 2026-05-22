from __future__ import annotations

from bs4 import Tag

from ..text_utils import normalize_markdown_text
from ..types import DomdownOptions
from .block import render_block
from .postprocess import postprocess_markdown

__all__ = ["postprocess_markdown", "render_markdown"]


def render_markdown(root: Tag, options: DomdownOptions) -> str:
    parts = [part for part in (render_block(child, options) for child in root.children) if part]
    return normalize_markdown_text("\n\n".join(parts))
