from __future__ import annotations

from collections.abc import Mapping

from .._constants import DOMDOWN_VERSION
from .._core.metadata import HtmlMetadata
from .._text.frontmatter import format_scalar, format_tag, quote_string


def render_frontmatter(metadata: HtmlMetadata, fallback_fields: Mapping[str, object] | None = None) -> str:
    """Serialize article metadata as YAML-like frontmatter."""

    fallbacks = dict(fallback_fields or {})
    lines = ["---"]
    scalar_fields = [
        ("title", _first_value(metadata.title, fallbacks.get("title"))),
        ("source", _first_value(metadata.source, fallbacks.get("source"))),
        ("site_name", _first_value(metadata.site_name, fallbacks.get("site_name"))),
        ("canonical_url", _first_value(metadata.canonical_url, fallbacks.get("canonical_url"))),
        ("language", _first_value(metadata.language, fallbacks.get("language"))),
        ("domdown_version", DOMDOWN_VERSION),
        ("image", _first_value(metadata.image, fallbacks.get("image"))),
    ]
    trailing_fields = [
        ("published", _first_value(metadata.published, fallbacks.get("published"))),
        ("created", _first_value(metadata.created, fallbacks.get("created"))),
        ("description", _first_value(metadata.description, fallbacks.get("description"))),
    ]
    for key, value in scalar_fields:
        if value:
            lines.append(f"{key}: {format_scalar(value)}")
    author = metadata.author or _as_string_tuple(fallbacks.get("author"))
    if author:
        lines.append("author:")
        for value in author:
            lines.append(f"  - {quote_string(value)}")
    for key, value in trailing_fields:
        if value:
            lines.append(f"{key}: {format_scalar(value)}")
    tags = metadata.tags or _as_string_tuple(fallbacks.get("tags"))
    if tags:
        lines.append("tags:")
        for value in tags:
            lines.append(f"  - {format_tag(value)}")
    lines.append("---")
    return "\n".join(lines)


def _first_value(*values: object) -> str:
    """Return the first non-empty string-like value from metadata or fallback fields."""

    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _as_string_tuple(value: object) -> tuple[str, ...]:
    """Normalize fallback sequences for frontmatter list fields."""

    if isinstance(value, tuple):
        return tuple(item for item in value if isinstance(item, str) and item.strip())
    if isinstance(value, list):
        return tuple(item for item in value if isinstance(item, str) and item.strip())
    if isinstance(value, str) and value.strip():
        return (value.strip(),)
    return ()
