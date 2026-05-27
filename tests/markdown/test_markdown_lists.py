from __future__ import annotations

from bs4 import BeautifulSoup

from domdown._core import DomdownOptions
from domdown.markdown.lists import render_list, render_list_item


def test_render_list_and_nested_list_items() -> None:
    """List rendering should preserve hierarchy and list markers."""

    soup = BeautifulSoup(
        "<ul><li>one</li><li>two<ul><li>nested</li></ul></li></ul>",
        "lxml",
    )

    assert render_list(soup.ul, DomdownOptions(), ordered=False) == "- one\n- two\n  - nested"
    assert render_list_item(soup.ul.find("li"), DomdownOptions(), ordered=False, index=None) == "- one"


def test_render_list_item_omits_empty_items() -> None:
    """Empty list items should not emit placeholder bullets."""

    soup = BeautifulSoup("<ul><li><a href='https://example.com'></a></li></ul>", "lxml")

    assert render_list_item(soup.ul.find("li"), DomdownOptions(), ordered=False, index=None) == ""
