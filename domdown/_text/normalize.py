from __future__ import annotations

import html as html_lib
import re


def normalize_inline_text(text: str) -> str:
    """Unescape HTML entities and collapse inline whitespace."""

    text = html_lib.unescape(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def collapse_inline_text(text: str) -> str:
    """Collapse inline whitespace without decoding entities in rendered Markdown."""

    return re.sub(r"\s+", " ", text).strip()


def escape_html_text(text: str) -> str:
    """Neutralize text that a Markdown renderer would parse as raw HTML."""

    return re.sub(r"<(?=[A-Za-z/!?])", "&lt;", text)


def normalize_markdown_text(text: str) -> str:
    """Normalize Markdown spacing without changing semantic blocks."""

    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
