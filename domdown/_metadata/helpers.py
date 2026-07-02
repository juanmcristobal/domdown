from __future__ import annotations

import re
from urllib.parse import unquote, urljoin, urlsplit

from bs4 import BeautifulSoup, Tag

from .._text.normalize import normalize_inline_text


def meta_content(soup: BeautifulSoup, selector: str) -> str | None:
    """Return a metadata value from a tag matching the selector."""

    tag = soup.select_one(selector)
    if not isinstance(tag, Tag):
        return None
    if tag.name == "link":
        return tag.get("href")
    if tag.name == "time":
        return tag.get("datetime") or normalize_inline_text(tag.get_text(" ", strip=True))
    return tag.get("content")


def tag_text(tag: Tag | None) -> str | None:
    """Return normalized text from a tag when it exists."""

    if not isinstance(tag, Tag):
        return None
    return normalize_inline_text(tag.get_text(" ", strip=True))


def select_texts(soup: BeautifulSoup, selector: str) -> tuple[str, ...]:
    """Collect normalized text values from all matching tags."""

    values = []
    for tag in soup.select(selector):
        if isinstance(tag, Tag):
            value = normalize_inline_text(tag.get_text(" ", strip=True))
            if value:
                values.append(value)
    return tuple(values)


def collect_texts(soup: BeautifulSoup, selectors: tuple[str, ...]) -> tuple[str, ...]:
    """Collect normalized text from a sequence of selectors without duplicates."""

    values: list[str] = []
    seen: set[str] = set()
    for selector in selectors:
        for value in select_texts(soup, selector):
            if value and value not in seen:
                seen.add(value)
                values.append(value)
    return tuple(values)


def collect_meta_contents(soup: BeautifulSoup, selectors: tuple[str, ...]) -> tuple[str, ...]:
    """Collect metadata contents from a sequence of selectors without duplicates."""

    values: list[str] = []
    seen: set[str] = set()
    for selector in selectors:
        value = meta_content(soup, selector)
        if value and value not in seen:
            seen.add(value)
            values.append(value)
    return tuple(values)


def first_text(*values: object) -> str:
    """Return the first non-empty string-like value from a sequence."""

    for value in values:
        if isinstance(value, tuple):
            if value:
                return value[0]
        elif isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def first_list(*values: object) -> tuple[str, ...]:
    """Return the first non-empty sequence of strings from a sequence."""

    for value in values:
        if isinstance(value, tuple) and value:
            return value
        if isinstance(value, str) and value.strip():
            return (value.strip(),)
    return ()


def split_tags(values: tuple[str, ...]) -> tuple[str, ...]:
    """Split tag strings into normalized tag tokens."""

    tags: list[str] = []
    seen: set[str] = set()
    for value in values:
        for part in value.replace(",", "/").split("/"):
            part = part.strip()
            if part and part not in seen:
                seen.add(part)
                tags.append(part)
    return tuple(tags)


def normalize_title(value: str, site_name: str | None = None) -> str:
    """Strip common site-name suffixes from a document title when present."""

    title = normalize_inline_text(value)
    if not title:
        return ""
    site_tokens = _site_name_tokens(site_name)
    if not site_tokens:
        return title
    while True:
        stripped = _strip_title_suffix(title, site_tokens)
        if stripped == title:
            return title
        title = stripped


def normalize_source(value: str | None, base_url: str | None = None) -> str:
    """Normalize a source URL and resolve relative paths when possible."""

    source = (value or "").strip()
    if not source:
        return ""
    if base_url and source.startswith("/"):
        return urljoin(base_url, source)
    if base_url and source.startswith("//"):
        return urljoin(base_url, source)
    if source.startswith("//"):
        return f"https:{source}"
    return source


def derive_title_from_url(value: str | None) -> str:
    """Derive a readable fallback title from a URL when no title metadata exists."""

    if not value:
        return ""
    parsed = urlsplit(value)
    segments = [segment for segment in parsed.path.split("/") if segment]
    if not segments:
        host = parsed.hostname or ""
        return host[4:] if host.startswith("www.") else host

    chosen = segments[-1]
    if chosen.isdigit() and len(segments) > 1:
        chosen = segments[-2]
        return f"{_titleize_path_segment(chosen)} {segments[-1]}"
    return _titleize_path_segment(chosen)


def looks_like_date(value: str) -> bool:
    """Heuristically detect whether a string looks like a short date."""

    return bool(re.match(r"^\w{3}\s+\d{1,2},\s+\d{4}$", value))


def looks_like_url(value: str) -> bool:
    """Heuristically detect whether a string is a URL."""

    parsed = urlsplit(value)
    return bool(parsed.scheme and parsed.netloc)


def first_image_src(soup: BeautifulSoup) -> str | None:
    """Return the first image source found in the document."""

    img = soup.find("img")
    if not isinstance(img, Tag):
        return None
    src = img.get("data-src") or img.get("data-original") or img.get("src")
    return src or None


def _site_name_tokens(site_name: str | None) -> set[str]:
    """Break a site name into lowercase tokens used for suffix stripping."""

    if not site_name:
        return set()
    return {token for token in re.split(r"[^a-z0-9]+", site_name.lower()) if token}


def _strip_title_suffix(title: str, site_tokens: set[str]) -> str:
    """Remove a single trailing title suffix when it matches a site marker."""

    for separator in (" | ", " · ", " — ", " - "):
        if separator not in title:
            continue
        head, tail = title.rsplit(separator, 1)
        tail = tail.strip()
        if not tail:
            continue
        tail_tokens = {token for token in re.split(r"[^a-z0-9]+", tail.lower()) if token}
        if tail_tokens & site_tokens:
            return head.strip()
        if "github" in site_tokens and "/" in tail and " " not in tail:
            return head.strip()
    return title


def _titleize_path_segment(segment: str) -> str:
    """Turn a URL path segment into a human-readable title fragment."""

    text = unquote(segment).replace("-", " ").replace("_", " ").strip()
    if not text:
        return ""
    tokens = [token for token in text.split() if token]
    if len(tokens) > 1 and tokens[0].isdigit():
        tokens = tokens[1:]
    normalized: list[str] = []
    for token in tokens:
        if token.islower():
            normalized.append(token.capitalize())
        elif token.isupper() and len(token) <= 4:
            normalized.append(token)
        else:
            normalized.append(token)
    return " ".join(normalized).strip()
