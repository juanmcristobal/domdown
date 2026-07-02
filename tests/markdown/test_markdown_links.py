from __future__ import annotations

from bs4 import BeautifulSoup

from domdown._core import DomdownOptions
from domdown.markdown.links import _looks_like_image_popup, render_link


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


def test_render_link_and_popup_detection_cover_edge_cases() -> None:
    """Image popups without alt text should render as linked images and expose the popup heuristic."""

    soup = BeautifulSoup(
        "<a class='pswp cursor-zoom-in' href='https://example.com/gallery'><img src='https://example.com/gallery.png' /></a>",
        "lxml",
    )

    assert _looks_like_image_popup(soup.a)
    assert (
        render_link(soup.a, DomdownOptions()) == "[![](https://example.com/gallery.png)](https://example.com/gallery)"
    )


def test_render_link_handles_unlinked_text_and_inline_image_markdown() -> None:
    """Unlinked content should be preserved even without a destination URL."""

    soup = BeautifulSoup("<div><a>Visible</a><a>![Alt](image)</a></div>", "lxml")

    assert render_link(soup.find_all("a")[0], DomdownOptions()) == "Visible"
    assert render_link(soup.find_all("a")[1], DomdownOptions()) == "![Alt](image)"


def test_render_link_uses_popup_alt_text_when_present() -> None:
    """Image popups with alt text should resolve directly to the image URL."""

    soup = BeautifulSoup(
        "<a class='popup' href='https://example.com/gallery'><img alt='Zoomed' src='/zoom.png' /></a>",
        "lxml",
    )

    assert render_link(soup.a, DomdownOptions(base_url="https://example.com")) == "https://example.com/zoom.png"
