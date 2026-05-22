from __future__ import annotations

from bs4 import BeautifulSoup

from domdown._core import DomdownOptions
from domdown.markdown.tables import render_table


def test_render_table_outputs_gfm_table() -> None:
    """Table rendering should produce a GitHub-flavored Markdown table."""

    soup = BeautifulSoup(
        "<table><tr><th>A</th><th>B</th></tr><tr><td>1</td><td>2</td></tr></table>",
        "lxml",
    )

    assert render_table(soup.table, DomdownOptions()) == "| A | B |\n| --- | --- |\n| 1 | 2 |"
