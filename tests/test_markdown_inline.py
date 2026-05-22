from __future__ import annotations

from bs4 import BeautifulSoup

from domdown._core import DomdownOptions
from domdown.markdown.inline import render_inline, render_inline_children


def test_render_inline_children_normalizes_inline_content() -> None:
    """Inline rendering should preserve text while collapsing whitespace."""

    soup = BeautifulSoup("<p>Hello <strong>world</strong></p>", "lxml")

    assert render_inline_children(soup.p, DomdownOptions()) == "Hello world"


def test_render_inline_handles_html_br_and_script_nodes() -> None:
    """Inline rendering should keep line breaks and skip scripts."""

    soup = BeautifulSoup("<div><br/><script>bad()</script></div>", "lxml")

    assert render_inline(soup.br, DomdownOptions()) == "\n"
    assert render_inline(soup.script, DomdownOptions()) == ""
