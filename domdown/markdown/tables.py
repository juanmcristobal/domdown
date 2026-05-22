from __future__ import annotations

from bs4 import Tag

from .._core import DomdownOptions
from .._text import normalize_inline_text
from .inline import render_inline_children


def render_table(node: Tag, options: DomdownOptions) -> str:
    """Render an HTML table as GitHub-flavored Markdown."""

    rows = list(_iter_rows(node, options))
    if not rows:
        return ""
    header_index = _header_row_index(rows)
    header = rows[header_index][0]
    body = [row for index, (row, _) in enumerate(rows) if index != header_index]
    divider = ["---" for _ in header]
    lines = ["| " + " | ".join(header) + " |", "| " + " | ".join(divider) + " |"]
    for row in body:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def _iter_rows(node: Tag, options: DomdownOptions) -> list[tuple[list[str], bool]]:
    """Collect the top-level rows from a table without recursing into nested tables."""

    rows: list[tuple[list[str], bool]] = []
    row_containers = [node]
    for section in node.find_all(["thead", "tbody", "tfoot"], recursive=False):
        row_containers.append(section)
    for container in row_containers:
        for tr in container.find_all("tr", recursive=False):
            cells = []
            has_header_cells = container.name == "thead"
            for cell in tr.find_all(["th", "td"], recursive=False):
                if cell.name == "th":
                    has_header_cells = True
                cells.append(normalize_inline_text(render_inline_children(cell, options)))
            if cells:
                rows.append((cells, has_header_cells))
    return rows


def _header_row_index(rows: list[tuple[list[str], bool]]) -> int:
    """Choose the row that should act as the table header."""

    for index, (_, is_header) in enumerate(rows):
        if is_header:
            return index
    return 0
