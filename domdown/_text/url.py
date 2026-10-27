from __future__ import annotations

import re
from urllib.parse import urljoin, urlparse

# Schemes that cannot execute script when a rendered Markdown link or image is followed.
SAFE_URL_SCHEMES = frozenset({"", "http", "https", "mailto", "tel", "ftp"})


def safe_url(url: str | None) -> str:
    """Return the URL unless its scheme could run script (javascript:, vbscript:, data:, ...)."""

    if not url:
        return ""
    # Browsers ignore ASCII whitespace/control characters when parsing the scheme.
    probe = re.sub(r"[\x00-\x20\x7f]", "", str(url))
    match = re.match(r"([A-Za-z][A-Za-z0-9+.-]*):", probe)
    scheme = match.group(1).lower() if match else ""
    if scheme in SAFE_URL_SCHEMES or (scheme == "data" and probe[5:].lower().startswith("image/")):
        return str(url)
    return ""


def resolve_url(url: str | None, base_url: str | None) -> str:
    """Resolve a possibly relative URL against an optional base URL, dropping unsafe schemes."""

    url = safe_url(url)
    if not url:
        return ""
    if base_url:
        try:
            return urljoin(base_url, url)
        except ValueError:
            return url
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
