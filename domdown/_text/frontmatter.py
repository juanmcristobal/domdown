from __future__ import annotations

import re

# Characters that end a YAML line or are unsafe inside a double-quoted scalar.
_YAML_ESCAPES = {"\n": "\\n", "\r": "\\r", "\t": "\\t", "\x85": "\\N", "\u2028": "\\L", "\u2029": "\\P"}
_YAML_CONTROL = re.compile(r"[\x00-\x1f\x7f-\x9f\u2028\u2029]")
_YAML_INDICATORS = re.compile(r"[:#\[\]{}&,*!?|>'\"\\]")
# Plain scalars that YAML loaders would turn into null/bool, or that start with a reserved indicator.
_YAML_RETYPED = re.compile(r"^(?:~|null|true|false|yes|no|on|off|y|n)$", re.IGNORECASE)
_YAML_BAD_START = re.compile(r"^(?:[%@`]|-(?:\s|$)|---|\.\.\.)")


def _escape_char(match: re.Match[str]) -> str:
    char = match.group(0)
    return _YAML_ESCAPES.get(char) or f"\\x{ord(char):02x}"


def quote_string(value: str) -> str:
    """Quote a string as a single-line YAML double-quoted scalar."""

    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    escaped = _YAML_CONTROL.sub(_escape_char, escaped)
    return f'"{escaped}"'


def _needs_quotes(value: str) -> bool:
    return bool(
        _YAML_INDICATORS.search(value)
        or _YAML_CONTROL.search(value)
        or _YAML_RETYPED.match(value)
        or _YAML_BAD_START.match(value)
    )


def format_scalar(value: str) -> str:
    """Format a scalar value for frontmatter emission."""

    if not value:
        return '""'
    if _needs_quotes(value) or value.strip() != value:
        return quote_string(value)
    return value


def format_tag(value: str) -> str:
    """Format a tag value for frontmatter emission."""

    if not value:
        return '""'
    if _needs_quotes(value):
        return quote_string(value)
    return value
