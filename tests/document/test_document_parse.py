from __future__ import annotations

from domdown._document import parse_html


def test_parse_html_returns_a_soup_document() -> None:
    """Parsing should produce a BeautifulSoup document tree."""

    soup = parse_html("<html><body><p>hello</p></body></html>")

    assert soup.body is not None
    assert soup.body.p.get_text(strip=True) == "hello"
