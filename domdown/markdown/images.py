from __future__ import annotations

import re

from bs4 import Tag

from .._core import DomdownOptions
from .._text import resolve_url


def render_image(node: Tag, options: DomdownOptions) -> str:
    """Render an image node as Markdown image syntax."""

    src = _best_image_src(node)
    src = resolve_url(src, options.base_url)
    alt = node.get("alt") or node.get("title") or ""
    return f"![{alt}]({src})" if src else ""


def _best_image_src(node: Tag) -> str:
    """Choose the most useful image source, preferring srcset when available."""

    for attr in ("srcset", "data-srcset"):
        candidate = node.get(attr)
        best = _best_srcset_candidate(candidate)
        if best:
            return best
    return node.get("src") or node.get("data-src") or node.get("data-original") or ""


def _best_srcset_candidate(srcset: str | None) -> str:
    """Choose the highest-resolution URL from a srcset attribute."""

    if not srcset:
        return ""
    best_url = ""
    best_score = -1.0
    for candidate in srcset.split(","):
        parts = candidate.strip().split()
        if not parts:
            continue
        url = parts[0]
        score = _srcset_score(parts[1:] if len(parts) > 1 else [])
        if score >= best_score:
            best_score = score
            best_url = url
    return best_url


def _srcset_score(descriptors: list[str]) -> float:
    """Score a srcset candidate based on width or density descriptors."""

    if not descriptors:
        return 0.0
    score = 0.0
    for descriptor in descriptors:
        match = re.match(r"^(?P<value>\d+(?:\.\d+)?)(?P<kind>w|x)$", descriptor)
        if not match:
            continue
        value = float(match.group("value"))
        if match.group("kind") == "w":
            return value
        score = max(score, value * 1000.0)
    return score
