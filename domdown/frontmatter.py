from __future__ import annotations

from .text_utils import format_scalar, format_tag, quote_string
from .types import HtmlMetadata


def render_frontmatter(metadata: HtmlMetadata) -> str:
    lines = ["---"]
    scalar_fields = [
        ("title", metadata.title),
        ("source", metadata.source),
    ]
    trailing_fields = [
        ("published", metadata.published),
        ("created", metadata.created),
        ("description", metadata.description),
    ]
    for key, value in scalar_fields:
        if value:
            lines.append(f"{key}: {format_scalar(value)}")
    if metadata.author:
        lines.append("author:")
        for value in metadata.author:
            lines.append(f"  - {quote_string(value)}")
    for key, value in trailing_fields:
        if value:
            lines.append(f"{key}: {format_scalar(value)}")
    if metadata.tags:
        lines.append("tags:")
        for value in metadata.tags:
            lines.append(f"  - {format_tag(value)}")
    lines.append("---")
    return "\n".join(lines)


def compose_document(frontmatter: str | None, markdown: str) -> str:
    if frontmatter:
        body = markdown.strip()
        return f"{frontmatter}\n{body}".strip()
    return markdown.strip()

