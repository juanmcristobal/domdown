from __future__ import annotations

from bs4 import BeautifulSoup

from domdown._core import DomdownOptions
from domdown.markdown.tables import render_table


def test_render_table_outputs_gfm_table() -> None:
    """Table rendering should produce a GitHub-flavored Markdown table."""

    soup = BeautifulSoup(
        "<table><thead><tr><th>A</th><th>B</th></tr></thead><tbody><tr><td>1</td><td>2</td></tr></tbody></table>",
        "lxml",
    )

    assert render_table(soup.table, DomdownOptions()) == "| A | B |\n| --- | --- |\n| 1 | 2 |"


def test_render_table_normalizes_spans_and_uneven_rows() -> None:
    """Advisory tables with merged cells should remain valid GFM tables."""

    soup = BeautifulSoup(
        """
        <table>
          <thead><tr><th>Product</th><th>Version</th><th>Notes</th></tr></thead>
          <tbody>
            <tr><td rowspan="2">Remote Support</td><td>25.3.2</td><td>Fixed | patch</td></tr>
            <tr><td colspan="2">25.3.3 and above</td></tr>
          </tbody>
        </table>
        """,
        "lxml",
    )

    assert render_table(soup.table, DomdownOptions()) == (
        "| Product | Version | Notes |\n"
        "| --- | --- | --- |\n"
        "| Remote Support | 25.3.2 | Fixed \\| patch |\n"
        "| Remote Support | 25.3.3 and above |  |"
    )
