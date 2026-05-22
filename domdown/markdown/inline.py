from __future__ import annotations

import html as html_lib
import re

from bs4 import NavigableString, Tag

from ..text_utils import normalize_inline_text
from ..types import DomdownOptions


def render_inline_children(node: Tag, options: DomdownOptions) -> str:
    parts = []
    for child in node.children:
        rendered = render_inline(child, options)
        if rendered:
            parts.append(rendered)
    return normalize_inline_text("".join(parts))


def render_inline(node: object, options: DomdownOptions) -> str:
    if isinstance(node, NavigableString):
        return re.sub(r"\s+", " ", html_lib.unescape(str(node)))
    if not isinstance(node, Tag):
        return ""
    name = node.name.lower()
    if name in {"script", "style", "noscript"}:
        return ""
    if name == "br":
        return "\n"
    if name == "img":
        from .images import render_image

        return render_image(node, options)
    if name == "a":
        from .links import render_link

        return render_link(node, options)
    if name in {"code", "kbd", "samp"}:
        content = render_inline_children(node, options)
        return f"`{content}`" if content else ""
    if name in {"strong", "b", "em", "i", "span"}:
        return render_inline_children(node, options)
    if name in {"p", "div", "li"}:
        return render_inline_children(node, options)
    return render_inline_children(node, options)
