from __future__ import annotations

from bs4 import BeautifulSoup

from domdown._core import DomdownOptions
from domdown.markdown.links import render_link


def test_render_link_formats_normal_and_image_links() -> None:
    """Link rendering should preserve content and linked images."""

    soup = BeautifulSoup(
        "<div><a href='https://example.com'>Example</a><a class='cursor-zoom-in' href='https://example.com'><img alt='Alt' src='https://example.com/image.png' /></a><a class='cursor-zoom-in' href='https://example.com/gallery'><img src='https://example.com/gallery.png' /></a><a href='https://example.com/gallery'><img alt='Gallery' src='https://example.com/gallery.png' /></a></div>",
        "lxml",
    )

    links = soup.find_all("a")

    assert render_link(links[0], DomdownOptions()) == "[Example](https://example.com)"
    assert render_link(links[1], DomdownOptions()) == "https://example.com/image.png"
    assert (
        render_link(links[2], DomdownOptions()) == "[![](https://example.com/gallery.png)](https://example.com/gallery)"
    )
    assert (
        render_link(links[3], DomdownOptions())
        == "[![Gallery](https://example.com/gallery.png)](https://example.com/gallery)"
    )


def test_render_link_omits_empty_anchor_chrome() -> None:
    """Empty links without visible text should not surface as bare URLs."""

    soup = BeautifulSoup("<a href='https://example.com'></a>", "lxml")

    assert render_link(soup.a, DomdownOptions()) == ""
