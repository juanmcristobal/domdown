from __future__ import annotations

import re


def quote_string(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def format_scalar(value: str) -> str:
    if not value:
        return '""'
    if re.search(r"[:#\[\]{}&,*!?|>'\"\\]", value) or value.strip() != value or "\n" in value:
        return quote_string(value)
    return value


def format_tag(value: str) -> str:
    if not value:
        return '""'
    if re.search(r"[:#\[\]{}&,*!?|>'\"\\]", value) or "\n" in value:
        return quote_string(value)
    return value
