from __future__ import annotations

import re

from bs4 import BeautifulSoup, Tag

from .._text.normalize import normalize_inline_text


def meta_content(soup: BeautifulSoup, selector: str) -> str | None:
    """Return a metadata value from a tag matching the selector."""

    tag = soup.select_one(selector)
    if not isinstance(tag, Tag):
        return None
    if tag.name == "link":
        return tag.get("href")
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
    for value in values:
        for part in value.replace(",", "/").split("/"):
            part = part.strip()
            if part:
                tags.append(part)
    return tuple(tags)


def looks_like_date(value: str) -> bool:
    """Heuristically detect whether a string looks like a short date."""

    return bool(re.match(r"^\w{3}\s+\d{1,2},\s+\d{4}$", value))


def first_image_src(soup: BeautifulSoup) -> str | None:
    """Return the first image source found in the document."""

    img = soup.find("img")
    if not isinstance(img, Tag):
        return None
    src = img.get("data-src") or img.get("data-original") or img.get("src")
    return src or None
