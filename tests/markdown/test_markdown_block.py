from __future__ import annotations

from bs4 import BeautifulSoup

from domdown._core import DomdownOptions
from domdown.markdown.block import render_block


def test_render_block_covers_headings_paragraphs_and_quotes() -> None:
    """Block rendering should handle common structural HTML elements."""

    soup = BeautifulSoup(
        "<div><h1>Title</h1><p>Body</p><blockquote><p>Quote</p></blockquote><script>skip()</script></div>",
        "lxml",
    )

    children = list(soup.div.children)

    assert render_block(children[0], DomdownOptions()) == "# Title"
    assert render_block(children[1], DomdownOptions()) == "Body"
    assert render_block(children[2], DomdownOptions()) == "> Quote"
    assert render_block(children[3], DomdownOptions()) == ""


def test_render_block_unwraps_self_linked_heading_titles() -> None:
    """Heading titles that wrap a single self-link should render as plain text."""

    soup = BeautifulSoup(
        '<h1><a href="https://example.com/article"><span>Example Title</span></a></h1>',
        "lxml",
    )

    assert render_block(soup.h1, DomdownOptions()) == "# Example Title"
