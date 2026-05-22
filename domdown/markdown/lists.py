from __future__ import annotations

from bs4 import Tag

from .._core import DomdownOptions
from .._text import normalize_inline_text
from .inline import render_inline


def render_list(node: Tag, options: DomdownOptions, ordered: bool) -> str:
    """Render a list tag and its direct list items."""

    items = []
    for index, li in enumerate(node.find_all("li", recursive=False), 1):
        item = render_list_item(li, options, ordered=ordered, index=index)
        if item:
            items.append(item)
    return "\n".join(items)


def render_list_item(node: Tag, options: DomdownOptions, ordered: bool, index: int | None = None) -> str:
    """Render a single list item including nested lists."""

    prefix = f"{index}." if ordered and index is not None else "-"
    inline_parts = []
    nested_parts = []
    for child in node.children:
        if isinstance(child, Tag) and child.name and child.name.lower() in {"ul", "ol"}:
            nested_parts.append(render_list(child, options, ordered=child.name.lower() == "ol"))
        else:
            rendered = render_inline(child, options)
            if rendered:
                inline_parts.append(rendered)
    head = normalize_inline_text("".join(inline_parts))
    blocks = [f"{prefix} {head}".rstrip() if head else prefix]
    blocks.extend(nested_parts)
    return "\n".join(blocks)
