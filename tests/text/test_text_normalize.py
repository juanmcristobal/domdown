from __future__ import annotations

from domdown._text import normalize_inline_text, normalize_markdown_text


def test_normalize_inline_text_collapses_html_entities_and_whitespace() -> None:
    """Inline normalization should unescape entities and collapse spacing."""

    assert normalize_inline_text("  A &amp;\nB  ") == "A & B"


def test_normalize_markdown_text_normalizes_blank_lines() -> None:
    """Markdown normalization should keep paragraphs but collapse excess breaks."""

    assert normalize_markdown_text("A  \n\n\nB") == "A\n\nB"
