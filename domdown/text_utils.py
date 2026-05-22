from __future__ import annotations

import html as html_lib
import re
from urllib.parse import urljoin


def normalize_inline_text(text: str) -> str:
    text = html_lib.unescape(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_markdown_text(text: str) -> str:
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def resolve_url(url: str | None, base_url: str | None) -> str:
    if not url:
        return ""
    if base_url:
        return urljoin(base_url, url)
    return url


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

