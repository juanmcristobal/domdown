from __future__ import annotations

from urllib.parse import urljoin, urlparse


def resolve_url(url: str | None, base_url: str | None) -> str:
    """Resolve a possibly relative URL against an optional base URL."""

    if not url:
        return ""
    if base_url:
        return urljoin(base_url, url)
    return url


def origin_url(url: str | None) -> str | None:
    """Return the scheme and host for an absolute URL."""

    if not url:
        return None
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    return f"{parsed.scheme}://{parsed.netloc}"


def resolve_srcset(srcset: str | None, base_url: str | None) -> str:
    """Resolve every URL in a srcset list against an optional base URL."""

    if not srcset:
        return ""
    resolved_entries: list[str] = []
    for candidate in srcset.split(","):
        parts = candidate.strip().split()
        if not parts:
            continue
        url = resolve_url(parts[0], base_url)
        descriptor = " ".join(parts[1:])
        resolved_entries.append(f"{url} {descriptor}".strip())
    return ", ".join(resolved_entries)
