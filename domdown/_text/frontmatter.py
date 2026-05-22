from __future__ import annotations

import re


def quote_string(value: str) -> str:
    """Quote a string for YAML-like frontmatter output."""

    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def format_scalar(value: str) -> str:
    """Format a scalar value for frontmatter emission."""

    if not value:
        return '""'
    if re.search(r"[:#\[\]{}&,*!?|>'\"\\]", value) or value.strip() != value or "\n" in value:
        return quote_string(value)
    return value


def format_tag(value: str) -> str:
    """Format a tag value for frontmatter emission."""

    if not value:
        return '""'
    if re.search(r"[:#\[\]{}&,*!?|>'\"\\]", value) or "\n" in value:
        return quote_string(value)
    return value
