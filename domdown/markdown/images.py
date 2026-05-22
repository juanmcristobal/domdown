from __future__ import annotations

from bs4 import Tag

from ..text_utils import resolve_url
from ..types import DomdownOptions


def render_image(node: Tag, options: DomdownOptions) -> str:
    src = node.get("src") or node.get("data-src") or node.get("data-original") or ""
    src = resolve_url(src, options.base_url)
    alt = node.get("alt") or node.get("title") or ""
    return f"![{alt}]({src})" if src else ""
