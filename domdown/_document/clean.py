from __future__ import annotations

from bs4 import Comment, Tag

from .._constants import NOISE_MARKERS


def clean_root(root: Tag, remove_selectors: tuple[str, ...], skip_tags: set[str]) -> Tag:
    """Remove obvious noise and normalize lazy-loaded images in place."""

    for comment in root.find_all(string=lambda value: isinstance(value, Comment)):
        comment.extract()

    for selector in remove_selectors:
        for node in root.select(selector):
            node.decompose()

    for node in list(root.find_all(True)):
        if not isinstance(node, Tag) or getattr(node, "attrs", None) is None:
            continue
        if node.name in skip_tags or _looks_like_noise(node):
            node.decompose()

    for node in list(root.find_all(skip_tags)):
        node.decompose()
    for img in root.find_all("img"):
        data_src = img.get("data-src") or img.get("data-original") or img.get("data-lazy-src")
        if data_src and (not img.get("src") or str(img.get("src", "")).startswith("data:")):
            img["src"] = data_src
    return root


def _looks_like_noise(node: Tag) -> bool:
    """Heuristically detect non-content wrappers by class or id tokens."""

    if getattr(node, "attrs", None) is None:
        return False
    classes = node.get("class") or ()
    if not isinstance(classes, (list, tuple)):
        classes = (str(classes),)
    identifier = str(node.get("id", "")).lower()
    tokens = " ".join([str(token).lower() for token in classes] + [identifier])
    if any(marker in tokens for marker in NOISE_MARKERS):
        return True
    text = node.get_text(" ", strip=True).lower()
    return text == "more" and any(marker in tokens for marker in ("more", "share"))
