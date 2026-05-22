"""Stage interface for preserving useful semantic blocks."""

from __future__ import annotations

from dataclasses import dataclass

from ..rendering import _resolve_url
from ..types import PipelineContext


@dataclass(slots=True)
class PreserveStage:
    """Mark or normalize content that must survive Markdown conversion."""

    name: str = "preserve"

    def run(self, context: PipelineContext) -> PipelineContext:
        if context.document is None:
            return context
        for img in context.document.find_all("img"):
            data_src = img.get("data-src") or img.get("data-original") or img.get("data-lazy-src")
            if data_src and (not img.get("src") or str(img.get("src", "")).startswith("data:")):
                img["src"] = _resolve_url(data_src, context.options.base_url)
        for anchor in context.document.find_all("a"):
            href = anchor.get("href")
            if href:
                anchor["href"] = _resolve_url(href, context.options.base_url)
        return context
