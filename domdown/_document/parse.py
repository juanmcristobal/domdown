from __future__ import annotations

from bs4 import BeautifulSoup


def parse_html(html: str) -> BeautifulSoup:
    """Parse raw HTML into a BeautifulSoup document."""

    return BeautifulSoup(html, "lxml")
