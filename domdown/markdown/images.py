from __future__ import annotations

import re

from bs4 import Tag

from .._core import DomdownOptions
from .._text import resolve_url


def render_image(node: Tag, options: DomdownOptions) -> str:
    """Render an image node as Markdown image syntax."""

    src = _best_image_src(node)
    alt = node.get("alt") or node.get("title") or ""
    if _is_unusable_image(node, src):
        return alt
    if not src:
        return alt
    src = resolve_url(src, options.base_url)
    figure = node.find_parent("figure")
    caption = figure.find("figcaption").get_text(" ", strip=True) if figure and figure.find("figcaption") else ""
    has_editorial_context = bool(
        figure
        or node.find_parent("a")
        or node.find_parent("article")
        or node.find_parent("main")
    )
    if not alt.strip() and not caption and not has_editorial_context:
        return ""
    return f"![{alt}]({src})"


def _best_image_src(node: Tag) -> str:
    """Choose the most useful image source, preferring srcset when available."""

    for attr in ("srcset", "data-srcset"):
        candidate = node.get(attr)
        best = _best_srcset_candidate(candidate)
        if best:
            return best
    for attr in ("src", "data-src", "data-original", "data-lazy-src"):
        candidate = str(node.get(attr) or "")
        if candidate and not candidate.lower().startswith("data:image/"):
            return candidate
    return ""


def _is_unusable_image(node: Tag, src: str) -> bool:
    """Reject inline payloads, tracking pixels, and obvious placeholders."""

    if src.lower().startswith("data:image/"):
        return True
    if not src:
        return False
    normalized = src.lower().split("?", 1)[0].rsplit("/", 1)[-1]
    if normalized in {
        "pixel.gif",
        "pixel.png",
        "spacer.gif",
        "blank.gif",
        "transparent.gif",
        "placeholder.png",
        "placeholder.gif",
    }:
        return True
    for dimension in ("width", "height"):
        value = str(node.get(dimension) or "").strip().lower().removesuffix("px")
        if value.isdigit() and int(value) <= 1:
            return True
    return False


def _best_srcset_candidate(srcset: str | None) -> str:
    """Choose the highest-resolution URL from a srcset attribute."""

    if not srcset:
        return ""
    best_url = ""
    best_score = -1.0
    skip_data_payload = False
    for candidate in srcset.split(","):
        if skip_data_payload:
            skip_data_payload = False
            continue
        parts = candidate.strip().split()
        if not parts:
            continue
        url = parts[0]
        if url.lower().startswith("data:image/"):
            skip_data_payload = True
            continue
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
