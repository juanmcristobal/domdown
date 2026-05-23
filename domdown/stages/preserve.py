"""Stage interface for preserving useful semantic blocks."""

from __future__ import annotations

from dataclasses import dataclass

from .._core import PipelineContext
from .._text import origin_url, resolve_url


@dataclass(slots=True)
class PreserveStage:
    """Mark or normalize content that must survive Markdown conversion."""

    name: str = "preserve"

    def run(self, context: PipelineContext) -> PipelineContext:
        """Resolve image and link URLs before Markdown rendering."""

        if context.document is None:
            return context
        base_url = context.options.base_url or origin_url(context.metadata.canonical_url or context.metadata.source)
        explicit_base_url = context.options.base_url is not None
        for img in context.document.find_all("img"):
            src = img.get("src")
            data_src = img.get("data-src") or img.get("data-original") or img.get("data-lazy-src")
            srcset = img.get("srcset") or img.get("data-srcset")
            if srcset:
                img["srcset"] = _resolve_srcset(srcset, base_url, explicit_base_url)
            if data_src and (not src or str(src).startswith("data:")):
                img["src"] = _resolve_url(data_src, base_url, explicit_base_url)
                src = img.get("src")
            if src and not str(src).startswith("data:"):
                img["src"] = _resolve_url(src, base_url, explicit_base_url)
        for anchor in context.document.find_all("a"):
            href = anchor.get("href")
            if href:
                anchor["href"] = _resolve_url(href, base_url, explicit_base_url)
        return context


def _resolve_url(url: str | None, base_url: str | None, explicit_base_url: bool) -> str:
    """Resolve a URL conservatively when the base URL is inferred from metadata."""

    if not url:
        return ""
    if not base_url:
        return url
    if not explicit_base_url and not str(url).startswith("/"):
        return url
    return resolve_url(url, base_url)


def _resolve_srcset(srcset: str | None, base_url: str | None, explicit_base_url: bool) -> str:
    """Resolve each URL in a srcset while preserving site-relative paths when needed."""

    if not srcset:
        return ""
    entries: list[str] = []
    for candidate in srcset.split(","):
        parts = candidate.strip().split()
        if not parts:
            continue
        url = _resolve_url(parts[0], base_url, explicit_base_url)
        descriptor = " ".join(parts[1:])
        entries.append(f"{url} {descriptor}".strip())
    return ", ".join(entries)
