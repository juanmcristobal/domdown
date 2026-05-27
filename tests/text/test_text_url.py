from __future__ import annotations

from domdown._text import origin_url, resolve_srcset, resolve_url


def test_resolve_url_handles_relative_and_missing_urls() -> None:
    """URL resolution should support relative URLs and missing values."""

    assert resolve_url("/images/a.png", "https://example.com/articles/1") == "https://example.com/images/a.png"
    assert resolve_url(None, "https://example.com") == ""


def test_origin_url_and_srcset_resolution_cover_edge_cases() -> None:
    """URL helpers should keep absolute origins and resolve srcset entries consistently."""

    assert origin_url("https://example.com/path/to/article") == "https://example.com"
    assert origin_url("mailto:test@example.com") is None
    assert origin_url(None) is None
    assert resolve_srcset("/img/a.png 1x, /img/b.png 2x", "https://example.com/articles/1") == (
        "https://example.com/img/a.png 1x, https://example.com/img/b.png 2x"
    )
    assert resolve_srcset("", "https://example.com") == ""


def test_resolve_url_falls_back_for_malformed_urls() -> None:
    """Malformed URLs should not crash URL resolution."""

    assert resolve_url("https://[invalid-ipv6]/path", "https://example.com") == "https://[invalid-ipv6]/path"
