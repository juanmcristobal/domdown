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
    width = max(len(row) for row, _ in rows)
    normalized_rows = [row + [""] * (width - len(row)) for row, _ in rows]
    header = normalized_rows[header_index]
    body = [row for index, row in enumerate(normalized_rows) if index != header_index]
    divider = ["---" for _ in header]
    lines = ["| " + " | ".join(header) + " |", "| " + " | ".join(divider) + " |"]
    for row in body:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def _iter_rows(node: Tag, options: DomdownOptions) -> list[tuple[list[str], bool]]:
    """Collect the top-level rows from a table without recursing into nested tables."""

    rows: list[tuple[list[str], bool]] = []
    pending_rowspans: dict[int, tuple[int, str]] = {}
    row_containers = [node]
    for section in node.find_all(["thead", "tbody", "tfoot"], recursive=False):
        row_containers.append(section)
    for container in row_containers:
        for tr in container.find_all("tr", recursive=False):
            cells: list[str] = []
            has_header_cells = container.name == "thead"
            column = 0

            def take_pending() -> None:
                nonlocal column
                while column in pending_rowspans:
                    remaining, value = pending_rowspans[column]
                    cells.append(value)
                    column += 1
                    if remaining <= 1:
                        del pending_rowspans[column - 1]
                    else:
                        pending_rowspans[column - 1] = (remaining - 1, value)

            for cell in tr.find_all(["th", "td"], recursive=False):
                take_pending()
                if cell.name == "th":
                    has_header_cells = True
                value = _escape_table_cell(normalize_inline_text(render_inline_children(cell, options)))
                colspan = _positive_span(cell.get("colspan"))
                rowspan = _positive_span(cell.get("rowspan"))
                cells.append(value)
                cells.extend([""] * (colspan - 1))
                if rowspan > 1:
                    for offset in range(colspan):
                        pending_rowspans[column + offset] = (rowspan - 1, value)
                column += colspan
            take_pending()
            if cells:
                rows.append((cells, has_header_cells))
    return rows


def _positive_span(value: object) -> int:
    """Return a valid HTML span value, falling back to one for malformed markup."""

    try:
        return max(int(str(value)), 1)
    except (TypeError, ValueError):
        return 1


def _escape_table_cell(value: str) -> str:
    """Keep cell content on one Markdown table row."""

    return value.replace("|", "\\|").replace("\n", "<br>")


def _header_row_index(rows: list[tuple[list[str], bool]]) -> int:
    """Choose the row that should act as the table header."""

    for index, (_, is_header) in enumerate(rows):
        if is_header:
            return index
    return 0
