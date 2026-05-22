from __future__ import annotations

from bs4 import Tag

from .._core import DomdownOptions
from .._text import resolve_url


def render_image(node: Tag, options: DomdownOptions) -> str:
    """Render an image node as Markdown image syntax."""

    src = node.get("src") or node.get("data-src") or node.get("data-original") or ""
    src = resolve_url(src, options.base_url)
    alt = node.get("alt") or node.get("title") or ""
    return f"![{alt}]({src})" if src else ""
