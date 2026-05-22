from __future__ import annotations

from bs4 import Comment, Tag

from .._constants import BOILERPLATE_PHRASES, HEADER_MARKERS, NOISE_MARKERS, RELATED_PHRASES


def clean_root(root: Tag, remove_selectors: tuple[str, ...], skip_tags: set[str], preserve_chrome: bool = False) -> Tag:
    """Remove obvious noise and normalize lazy-loaded images in place."""

    for comment in root.find_all(string=lambda value: isinstance(value, Comment)):
        comment.extract()

    for selector in remove_selectors:
        for node in root.select(selector):
            node.decompose()

    if not preserve_chrome:
        for node in list(root.find_all(True)):
            if not isinstance(node, Tag) or getattr(node, "attrs", None) is None:
                continue
            if node.name in skip_tags or _looks_like_noise(node):
                node.decompose()

        _remove_structural_chrome(root)

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


def _remove_structural_chrome(root: Tag) -> None:
    """Remove small header and related-link chrome blocks from the chosen root."""

    for node in reversed(list(root.find_all(True))):
        if not isinstance(node, Tag) or node is root:
            continue
        if _is_small_structural_block(node) and (
            _looks_like_header_block(node) or _looks_like_related_block(node) or _looks_like_boilerplate(node)
        ):
            node.decompose()


def _looks_like_header_block(node: Tag) -> bool:
    """Detect top-of-article blocks that repeat title, byline, or date metadata."""

    marker_text = _marker_text(node)
    if any(marker in marker_text for marker in HEADER_MARKERS):
        return True
    has_title_like_heading = bool(node.find(["h1", "h2"], recursive=False))
    has_metadata = bool(node.find("time", recursive=False)) or any(token in marker_text for token in ("byline", "author", "date", "time", "meta"))
    text_words = len(node.get_text(" ", strip=True).split())
    paragraph_count = len(node.find_all("p"))
    return has_title_like_heading and has_metadata and text_words <= 80 and paragraph_count <= 2


def _looks_like_related_block(node: Tag) -> bool:
    """Detect related-link sections that sit between the header and body."""

    text = node.get_text(" ", strip=True).lower()
    if any(phrase in text for phrase in RELATED_PHRASES):
        return True
    marker_text = _marker_text(node)
    return any(marker in marker_text for marker in ("related", "recommend"))


def _looks_like_boilerplate(node: Tag) -> bool:
    """Detect compact documentation or feedback boilerplate blocks."""

    text = node.get_text(" ", strip=True).lower()
    return any(phrase in text for phrase in BOILERPLATE_PHRASES)


def _is_small_structural_block(node: Tag) -> bool:
    """Limit structural cleanup to compact blocks so wrappers with body text survive."""

    text_words = len(node.get_text(" ", strip=True).split())
    direct_blocks = sum(1 for child in node.find_all(recursive=False) if isinstance(child, Tag) and child.name in {"p", "ul", "ol", "li", "figure", "div", "section", "article"})
    return text_words <= 120 and direct_blocks <= 4


def _marker_text(node: Tag) -> str:
    """Join class and id markers into a single lowercase string."""

    classes = node.get("class") or ()
    if not isinstance(classes, (list, tuple)):
        classes = (str(classes),)
    identifier = str(node.get("id", "")).lower()
    return " ".join([str(token).lower() for token in classes] + [identifier])
