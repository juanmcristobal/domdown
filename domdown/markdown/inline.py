from __future__ import annotations

import html as html_lib
import re

from bs4 import NavigableString, Tag

from .._core import DomdownOptions
from .._text import normalize_inline_text


def render_inline_children(node: Tag, options: DomdownOptions) -> str:
    """Render all inline descendants of a tag and normalize whitespace."""

    parts = []
    for child in node.children:
        rendered = render_inline(child, options)
        if rendered:
            parts.append(rendered)
    return _normalize_inline_children("".join(parts))


def render_inline(node: object, options: DomdownOptions) -> str:
    """Render an inline HTML node into Markdown-compatible text."""

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
    if name in {"strong", "b"}:
        content = render_inline_children(node, options)
        return f"**{content}**" if content else ""
    if name in {"em", "i"}:
        content = render_inline_children(node, options)
        return f"_{content}_" if content else ""
    if name == "span":
        content = render_inline_children(node, options)
        if _looks_like_caption_credit(node):
            return f"\n\n{content}" if content else ""
        return content
    if name in {"p", "div", "li"}:
        return render_inline_children(node, options)
    return render_inline_children(node, options)


def _normalize_inline_children(text: str) -> str:
    """Normalize inline content while preserving hard line breaks from <br>."""

    text = html_lib.unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _looks_like_caption_credit(node: Tag) -> bool:
    """Detect inline credit spans that should start on their own line."""

    classes = node.get("class") or ()
    if isinstance(classes, (list, tuple)):
        tokens = {str(token).lower() for token in classes}
    else:
        tokens = {str(classes).lower()}
    marker_text = " ".join([*tokens, str(node.get("id", "")).lower()])
    return any(marker in marker_text for marker in ("caption-credit", "gallery-caption-credit", "credit"))
