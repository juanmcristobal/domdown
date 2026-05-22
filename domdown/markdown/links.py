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
            from .images import render_image

            rendered_image = render_image(image, options)
            if rendered_image and href:
                return f"[{rendered_image}]({href})"
            return rendered_image or href or ""
        return href or ""
    if content.startswith("![") and href:
        return f"[{content}]({href})"
    if href:
        return f"[{content}]({href})"
    return content
