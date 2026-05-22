from __future__ import annotations

from .._core.metadata import HtmlMetadata
from .._text.frontmatter import format_scalar, format_tag, quote_string


def render_frontmatter(metadata: HtmlMetadata) -> str:
    """Serialize article metadata as YAML-like frontmatter."""

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
