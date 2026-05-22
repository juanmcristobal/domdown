from __future__ import annotations

from domdown._text import resolve_url


def test_resolve_url_handles_relative_and_missing_urls() -> None:
    """URL resolution should support relative URLs and missing values."""

    assert resolve_url("/images/a.png", "https://example.com/articles/1") == "https://example.com/images/a.png"
    assert resolve_url(None, "https://example.com") == ""
