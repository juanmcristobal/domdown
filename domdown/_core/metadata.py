from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class HtmlMetadata:
    """Normalized article metadata extracted from the source HTML."""

    title: str | None = None
    source: str | None = None
    author: tuple[str, ...] = ()
    published: str | None = None
    created: str | None = None
    description: str | None = None
    tags: tuple[str, ...] = ()
    language: str | None = None
    canonical_url: str | None = None
    image: str | None = None
