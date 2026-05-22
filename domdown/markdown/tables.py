from __future__ import annotations

from bs4 import Tag

from ..text_utils import normalize_inline_text
from ..types import DomdownOptions
from .inline import render_inline_children


def render_table(node: Tag, options: DomdownOptions) -> str:
    rows = []
    for tr in node.find_all("tr", recursive=True):
        cells = []
        for cell in tr.find_all(["th", "td"], recursive=False):
            cells.append(normalize_inline_text(render_inline_children(cell, options)))
        if cells:
            rows.append(cells)
    if not rows:
        return ""
    header = rows[0]
    divider = ["---" for _ in header]
    body = rows[1:]
    lines = ["| " + " | ".join(header) + " |", "| " + " | ".join(divider) + " |"]
    for row in body:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)
