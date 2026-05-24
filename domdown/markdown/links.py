from __future__ import annotations

from bs4 import Tag

from .._core import DomdownOptions
from .._text import resolve_url


def render_link(node: Tag, options: DomdownOptions) -> str:
    """Render an anchor tag while preserving linked images when present."""

    href = resolve_url(node.get("href"), options.base_url)
    content = node.get_text(" ", strip=True)
    if not content:
        image = node.find("img")
        if image is not None:
            from .images import _best_image_src, render_image

            if _looks_like_image_popup(node):
                alt_text = str(image.get("alt") or image.get("title") or "").strip()
                if alt_text:
                    return resolve_url(_best_image_src(image), options.base_url)
                rendered_image = render_image(image, options)
                return f"[{rendered_image}]({href})" if rendered_image and href else rendered_image or href or ""
            rendered_image = render_image(image, options)
            if rendered_image and href:
                return f"[{rendered_image}]({href})"
            return rendered_image or ""
        return ""
    if content.startswith("![") and href:
        return f"[{content}]({href})"
    if href:
        return f"[{content}]({href})"
    return content


def _looks_like_image_popup(node: Tag) -> bool:
    """Detect anchors that only serve as zoom or lightbox wrappers around an image."""

    classes = node.get("class", []) if isinstance(node.get("class"), list) else [str(node.get("class", ""))]
    marker_text = " ".join(str(token).lower() for token in classes)
    return any(marker in marker_text for marker in ("popup", "img-link", "cursor-zoom-in", "pswp", "zoom"))
