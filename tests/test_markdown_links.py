from __future__ import annotations

from bs4 import BeautifulSoup

from domdown._core import DomdownOptions
from domdown.markdown.links import render_link


def test_render_link_formats_normal_and_image_links() -> None:
    """Link rendering should preserve content and linked images."""

    soup = BeautifulSoup(
        "<div><a href='https://example.com'>Example</a><a href='https://example.com'><img alt='Alt' src='https://example.com/image.png' /></a></div>",
        "lxml",
    )

    links = soup.find_all("a")

    assert render_link(links[0], DomdownOptions()) == "[Example](https://example.com)"
    assert render_link(links[1], DomdownOptions()) == "[![Alt](https://example.com/image.png)](https://example.com)"
