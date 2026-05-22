from __future__ import annotations

from urllib.parse import urljoin


def resolve_url(url: str | None, base_url: str | None) -> str:
    """Resolve a possibly relative URL against an optional base URL."""

    if not url:
        return ""
    if base_url:
        return urljoin(base_url, url)
    return url
