from __future__ import annotations

from html import escape

from bs4 import NavigableString, Tag

from .._constants import SKIP_TAGS
from .._core import DomdownOptions
from .._text import normalize_inline_text, normalize_markdown_text
from .code import render_code_block
from .images import render_image
from .inline import render_inline, render_inline_children
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
        title_link = _heading_title_link(node, options)
        if title_link is not None:
            return f"{'#' * level} {title_link}".strip()
        text = _render_heading_text(node, options)
        return f"{'#' * level} {text}".strip()
    if name == "img":
        return render_image(node, options)
    if name == "figure":
        return render_figure(node, options)
    if name in {"div", "section", "article"} and _looks_like_definition_list(node, options):
        return render_definition_list(node, options)
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


def render_figure(node: Tag, options: DomdownOptions) -> str:
    """Render a figure as its media content followed by an optional caption."""

    caption = next(
        (child for child in node.children if isinstance(child, Tag) and child.name.lower() == "figcaption"),
        None,
    )
    if caption is None:
        return render_container(node, options)

    media_parts = [
        part
        for part in (
            render_block(child, options)
            for child in node.children
            if not (isinstance(child, Tag) and child.name.lower() == "figcaption")
        )
        if part
    ]
    caption_text = render_inline_children(caption, options)
    if not caption_text:
        caption_text = render_container(caption, options)
    if caption_text:
        media_parts.append(caption_text)
    return normalize_markdown_text("\n\n".join(media_parts))


def render_definition_list(node: Tag, options: DomdownOptions) -> str:
    """Render definition-style metadata blocks as a semantic HTML definition list."""

    items = _collect_definition_items(node, options)
    if len(items) < 3:
        return render_container(node, options)

    lines = ["<dl>"]
    for term, value_html in items:
        lines.append(f"<dt>{escape(term)}</dt>")
        lines.append(f"<dd>{value_html}</dd>")
    lines.append("</dl>")
    return "\n".join(lines)


def _looks_like_definition_list(node: Tag, options: DomdownOptions) -> bool:
    """Detect repeated label/value rows that can be normalized to <dl>."""

    return len(_collect_definition_items(node, options)) >= 3


def _collect_definition_items(node: Tag, options: DomdownOptions) -> list[tuple[str, str]]:
    """Extract generic label/value pairs from a metadata-style container."""

    items: list[tuple[str, str]] = []
    for child in node.find_all(recursive=False):
        if not isinstance(child, Tag):
            continue
        items.extend(_collect_definition_items_from_node(child, options))
    return items


def _collect_definition_items_from_node(node: Tag, options: DomdownOptions) -> list[tuple[str, str]]:
    """Extract one or more definition items from a candidate child node."""

    parsed = _parse_definition_item(node, options)
    if parsed is not None:
        return [parsed]

    direct_children = [child for child in node.find_all(recursive=False) if isinstance(child, Tag)]
    if len(direct_children) < 2:
        return []

    if any(child.name.lower() in {"p", "ul", "ol", "table", "figure", "blockquote", "pre"} for child in direct_children):
        return []

    nested_items: list[tuple[str, str]] = []
    for child in direct_children:
        nested_items.extend(_collect_definition_items_from_node(child, options))
    return nested_items


def _parse_definition_item(node: Tag, options: DomdownOptions) -> tuple[str, str] | None:
    """Parse a single label/value row from a node."""

    direct_children = [child for child in node.find_all(recursive=False) if isinstance(child, Tag)]
    if len(direct_children) > 1:
        return None

    text = render_inline_children(node, options).strip()
    if not text:
        return None

    colon_index = text.find(":")
    if 0 < colon_index < 80:
        term = text[:colon_index].strip()
        value = text[colon_index + 1 :].strip()
        if term and value:
            return term, escape(value)

    anchors = [child for child in node.find_all("a", recursive=True) if isinstance(child, Tag)]
    if len(anchors) == 1 and len(direct_children) == 1:
        anchor = anchors[0]
        term = anchor.get_text(" ", strip=True)
        return term, str(anchor)

    return None


def _heading_title_link(node: Tag, options: DomdownOptions) -> str | None:
    """Return plain text for headings that only wrap a single self-link."""

    anchors = [child for child in node.children if isinstance(child, Tag) and child.name.lower() == "a"]
    if len(anchors) != 1:
        return None
    non_whitespace_children = [child for child in node.children if not isinstance(child, NavigableString) or str(child).strip()]
    if len(non_whitespace_children) != 1 or non_whitespace_children[0] is not anchors[0]:
        return None
    text = render_inline_children(anchors[0], options)
    return text or None


def _render_heading_text(node: Tag, options: DomdownOptions) -> str:
    """Render heading text while skipping permalink anchors."""

    has_permalink_anchor = any(
        isinstance(child, Tag)
        and child.name.lower() == "a"
        and str(child.get("href", "")).startswith("#")
        for child in node.children
    )
    parts: list[str] = []
    for child in node.children:
        if isinstance(child, Tag) and child.name.lower() == "a":
            href = str(child.get("href", ""))
            if href.startswith("#"):
                continue
        if has_permalink_anchor and isinstance(child, NavigableString):
            stripped = str(child).strip()
            if stripped in {"[", "]", "[[", "]]"}:
                continue
            if stripped.startswith("[[") and stripped.endswith("]]") and len(stripped) > 4:
                rendered = stripped[2:-2].strip()
                if rendered:
                    parts.append(rendered)
                continue
        rendered = render_inline(child, options)
        if rendered:
            parts.append(rendered)
    return normalize_inline_text("".join(parts))
