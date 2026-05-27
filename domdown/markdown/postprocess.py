from __future__ import annotations

import re

from .._core.metadata import HtmlMetadata


def postprocess_markdown(markdown: str, metadata: HtmlMetadata | None = None) -> str:
    """Normalize Markdown spacing and strip outer whitespace."""

    text = markdown.replace("\r\n", "\n").replace("\r", "\n")
    text = _strip_empty_headings(text)
    text = _strip_leading_branding(text, metadata)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _strip_empty_headings(text: str) -> str:
    """Remove heading markers that do not carry text."""

    lines = []
    for line in text.splitlines():
        if re.match(r"^#{1,6}\s*$", line.strip()):
            continue
        lines.append(line)
    return "\n".join(lines)


def _strip_leading_branding(text: str, metadata: HtmlMetadata | None) -> str:
    """Drop a short leading brand line when the site name is duplicated in the body."""

    if metadata is None or not metadata.site_name:
        return text
    site_name = metadata.site_name.strip()
    if not site_name:
        return text
    lines = text.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    if lines and lines[0].strip() == site_name:
        lines.pop(0)
    return "\n".join(lines)
