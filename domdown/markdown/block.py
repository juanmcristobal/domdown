from __future__ import annotations

from bs4 import NavigableString, Tag

from .._constants import SKIP_TAGS
from .._core import DomdownOptions
from .._text import normalize_inline_text, normalize_markdown_text
from .code import render_code_block
from .images import render_image
from .inline import render_inline_children
from .links import render_link
from .lists import render_list, render_list_item
from .tables import render_table


def render_block(node: object, options: DomdownOptions) -> str:
    """Render a single block-level HTML node to Markdown."""

    if isinstance(node, NavigableString):
        return normalize_inline_text(str(node))
    if not isinstance(node, Tag):
        return ""
    name = node.name.lower()
    if name in SKIP_TAGS:
        return ""
    if name in {"h1", "h2", "h3", "h4", "h5", "h6"}:
        level = int(name[1])
        text = render_inline_children(node, options)
        return f"{'#' * level} {text}".strip()
    if name == "img":
        return render_image(node, options)
    if name == "a":
        return render_link(node, options)
    if name == "br":
        return ""
    if name == "pre":
        return render_code_block(node, options)
    if name == "ul":
        return render_list(node, options, ordered=False)
    if name == "ol":
        return render_list(node, options, ordered=True)
    if name == "blockquote":
        content = render_container(node, options)
        return "\n".join(f"> {line}" if line else ">" for line in content.splitlines())
    if name == "table":
        return render_table(node, options)
    if name == "li":
        return render_list_item(node, options, ordered=False)
    if name == "p":
        return render_inline_children(node, options)
    return render_container(node, options)


def render_container(node: Tag, options: DomdownOptions) -> str:
    """Render a tag by recursively rendering each child block."""

    parts = [part for part in (render_block(child, options) for child in node.children) if part]
    return normalize_markdown_text("\n\n".join(parts))
