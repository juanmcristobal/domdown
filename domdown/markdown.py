from __future__ import annotations

import re

from bs4 import NavigableString, Tag

from .constants import SKIP_TAGS
from .text_utils import normalize_inline_text, normalize_markdown_text, resolve_url
from .types import DomdownOptions


def render_markdown(root: Tag, options: DomdownOptions) -> str:
    parts = [part for part in (_render_block(child, options) for child in root.children) if part]
    return normalize_markdown_text("\n\n".join(parts))


def postprocess_markdown(markdown: str) -> str:
    text = markdown.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _render_block(node: object, options: DomdownOptions) -> str:
    if isinstance(node, NavigableString):
        return normalize_inline_text(str(node))
    if not isinstance(node, Tag):
        return ""
    name = node.name.lower()
    if name in SKIP_TAGS:
        return ""
    if name in {"h1", "h2", "h3", "h4", "h5", "h6"}:
        level = int(name[1])
        text = _render_inline_children(node, options)
        return f"{'#' * level} {text}".strip()
    if name == "img":
        return _render_image(node, options)
    if name == "a":
        return _render_link(node, options)
    if name == "br":
        return ""
    if name == "ul":
        return _render_list(node, options, ordered=False)
    if name == "ol":
        return _render_list(node, options, ordered=True)
    if name == "blockquote":
        content = _render_container(node, options)
        return "\n".join(f"> {line}" if line else ">" for line in content.splitlines())
    if name == "table":
        return _render_table(node, options)
    if name == "li":
        return _render_list_item(node, options, ordered=False)
    if name == "p":
        return _render_inline_children(node, options)
    return _render_container(node, options)


def _render_container(node: Tag, options: DomdownOptions) -> str:
    parts = [part for part in (_render_block(child, options) for child in node.children) if part]
    return normalize_markdown_text("\n\n".join(parts))


def _render_inline_children(node: Tag, options: DomdownOptions) -> str:
    parts = []
    for child in node.children:
        rendered = _render_inline(child, options)
        if rendered:
            parts.append(rendered)
    return normalize_inline_text("".join(parts))


def _render_inline(node: object, options: DomdownOptions) -> str:
    if isinstance(node, NavigableString):
        return re.sub(r"\s+", " ", __import__("html").unescape(str(node)))
    if not isinstance(node, Tag):
        return ""
    name = node.name.lower()
    if name in {"script", "style", "noscript"}:
        return ""
    if name == "br":
        return "\n"
    if name == "img":
        return _render_image(node, options)
    if name == "a":
        return _render_link(node, options)
    if name in {"code", "kbd", "samp"}:
        content = _render_inline_children(node, options)
        return f"`{content}`" if content else ""
    if name in {"strong", "b", "em", "i", "span"}:
        return _render_inline_children(node, options)
    if name in {"p", "div", "li"}:
        return _render_inline_children(node, options)
    return _render_inline_children(node, options)


def _render_link(node: Tag, options: DomdownOptions) -> str:
    href = resolve_url(node.get("href"), options.base_url)
    content = "".join(_render_inline(child, options) for child in node.children).strip()
    if not content:
        return href or ""
    if content.startswith("![") and href:
        return f"[{content}]({href})"
    if href:
        return f"[{content}]({href})"
    return content


def _render_image(node: Tag, options: DomdownOptions) -> str:
    src = node.get("src") or node.get("data-src") or node.get("data-original") or ""
    src = resolve_url(src, options.base_url)
    alt = node.get("alt") or node.get("title") or ""
    return f"![{alt}]({src})" if src else ""


def _render_list(node: Tag, options: DomdownOptions, ordered: bool) -> str:
    items = []
    for index, li in enumerate(node.find_all("li", recursive=False), 1):
        item = _render_list_item(li, options, ordered=ordered, index=index)
        if item:
            items.append(item)
    return "\n".join(items)


def _render_list_item(node: Tag, options: DomdownOptions, ordered: bool, index: int | None = None) -> str:
    prefix = f"{index}." if ordered and index is not None else "-"
    inline_parts = []
    nested_parts = []
    for child in node.children:
        if isinstance(child, Tag) and child.name and child.name.lower() in {"ul", "ol"}:
            nested_parts.append(_render_list(child, options, ordered=child.name.lower() == "ol"))
        else:
            rendered = _render_inline(child, options)
            if rendered:
                inline_parts.append(rendered)
    head = normalize_inline_text("".join(inline_parts))
    blocks = [f"{prefix} {head}".rstrip() if head else prefix]
    blocks.extend(nested_parts)
    return "\n".join(blocks)


def _render_table(node: Tag, options: DomdownOptions) -> str:
    rows = []
    for tr in node.find_all("tr", recursive=True):
        cells = []
        for cell in tr.find_all(["th", "td"], recursive=False):
            cells.append(normalize_inline_text(_render_inline_children(cell, options)))
        if cells:
            rows.append(cells)
    if not rows:
        return ""
    header = rows[0]
    divider = ["---" for _ in header]
    body = rows[1:]
    lines = ["| " + " | ".join(header) + " |", "| " + " | ".join(divider) + " |"]
    for row in body:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)

