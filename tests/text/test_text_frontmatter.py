from __future__ import annotations

from domdown._text import format_scalar, format_tag, quote_string


def test_quote_string_escapes_quotes_and_backslashes() -> None:
    """Frontmatter string quoting should escape special characters."""

    assert quote_string('a"b\\c') == '"a\\"b\\\\c"'


def test_format_scalar_quotes_when_needed() -> None:
    """Scalar formatting should preserve plain values and quote risky ones."""

    assert format_scalar("simple") == "simple"
    assert format_scalar("needs: quoting") == '"needs: quoting"'


def test_format_tag_quotes_when_needed() -> None:
    """Tag formatting should follow the same quoting rules as scalar values."""

    assert format_tag("Threat Intel") == "Threat Intel"
    assert format_tag("Cloud:Security") == '"Cloud:Security"'
