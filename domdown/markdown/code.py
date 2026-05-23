from __future__ import annotations

import html as html_lib
import re
import textwrap

from bs4 import Tag

from .._core import DomdownOptions


def render_code_block(node: Tag, options: DomdownOptions) -> str:
    """Render a preformatted block as a fenced Markdown code block."""

    code_node = node.find("code", recursive=False)
    source = code_node if isinstance(code_node, Tag) else node
    text = source.get_text("", strip=False)
    text = html_lib.unescape(text).replace("\r\n", "\n").replace("\r", "\n")
    text = textwrap.dedent(text).strip("\n")
    if not text.strip():
        return ""
    language = _detect_language(node, code_node if isinstance(code_node, Tag) else None)
    fence = _code_fence(text)
    if language:
        return f"{fence}{language}\n{text}\n{fence}"
    return f"{fence}\n{text}\n{fence}"


def _detect_language(node: Tag, code_node: Tag | None) -> str:
    """Extract a language hint from common code-block class names."""

    candidates = []
    for tag in (code_node, node):
        if tag is None:
            continue
        classes = tag.get("class") or ()
        if not isinstance(classes, (list, tuple)):
            classes = (str(classes),)
        candidates.extend(str(value).lower() for value in classes)
    for candidate in candidates:
        match = re.search(r"(?:language|lang|highlight-source)-([a-z0-9_+-]+)", candidate)
        if match:
            return match.group(1)
    return ""


def _code_fence(text: str) -> str:
    """Choose a safe fenced code delimiter for the rendered block."""

    longest = max((len(match.group(0)) for match in re.finditer(r"`+", text)), default=0)
    return "`" * max(3, longest + 1)
