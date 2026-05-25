from __future__ import annotations

from bs4 import Comment, NavigableString, Tag
import re

from .._constants import BOILERPLATE_PHRASES, HEADER_MARKERS, NOISE_MARKERS, RELATED_PHRASES


def clean_root(root: Tag, remove_selectors: tuple[str, ...], skip_tags: set[str], preserve_chrome: bool = False) -> Tag:
    """Remove obvious noise and normalize lazy-loaded images in place."""

    for comment in root.find_all(string=lambda value: isinstance(value, Comment)):
        comment.extract()

    for text_node in list(root.find_all(string=True)):
        if isinstance(text_node, NavigableString) and _looks_like_template_placeholder(str(text_node)) and not _is_within_code_block(text_node):
            text_node.extract()

    for selector in remove_selectors:
        for node in root.select(selector):
            node.decompose()

    if not preserve_chrome:
        for node in list(root.find_all(True)):
            if not isinstance(node, Tag) or getattr(node, "attrs", None) is None:
                continue
            if _is_within_preserved_block(node):
                continue
            if _looks_like_decorative_image_block(node):
                node.decompose()
                continue
            if node.name in skip_tags:
                node.decompose()
                continue
            if _looks_like_noise(node) and not _has_substantive_body_content(node):
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
    if node.name == "a" and node.find("img") is not None:
        return False
    classes = node.get("class") or ()
    if not isinstance(classes, (list, tuple)):
        classes = (str(classes),)
    identifier = str(node.get("id", "")).lower()
    tokens = _noise_tokens(classes, identifier)
    if tokens & set(NOISE_MARKERS):
        return True
    text = node.get_text(" ", strip=True).lower()
    if _looks_like_link_chrome(node):
        return True
    return text == "more" and bool(tokens & {"more", "share"})


def _remove_structural_chrome(root: Tag) -> None:
    """Remove small header and related-link chrome blocks from the chosen root."""

    for node in reversed(list(root.find_all(True))):
        if not isinstance(node, Tag) or node is root:
            continue
        if _is_within_preserved_block(node):
            continue
        if _is_small_structural_block(node) and (
            _looks_like_header_block(node)
            or _looks_like_related_block(node)
            or _looks_like_navigation_block(node)
            or _looks_like_footer_block(node)
            or _looks_like_tag_block(node)
            or _looks_like_boilerplate(node)
            or _looks_like_about_block(node)
        ):
            if _has_substantive_body_content(node):
                continue
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
    word_count = len(text.split())
    link_count = len(node.find_all("a"))
    if any(phrase in text for phrase in RELATED_PHRASES) and (word_count <= 18 or link_count >= 2):
        return True
    marker_text = _marker_text(node)
    return any(marker in marker_text for marker in ("related", "recommend"))


def _looks_like_boilerplate(node: Tag) -> bool:
    """Detect compact documentation or feedback boilerplate blocks."""

    text = node.get_text(" ", strip=True).lower()
    return any(phrase in text for phrase in BOILERPLATE_PHRASES)


def _looks_like_about_block(node: Tag) -> bool:
    """Detect compact company/about blocks with a heading and CTA links."""

    heading = node.find(["h1", "h2", "h3", "h4"], recursive=False)
    if not isinstance(heading, Tag):
        return False
    heading_text = heading.get_text(" ", strip=True).lower()
    if not heading_text.startswith("about "):
        return False
    link_count = len(node.find_all("a"))
    button_count = len(node.find_all("button"))
    text_words = len(node.get_text(" ", strip=True).split())
    return text_words <= 120 and (link_count >= 1 or button_count >= 1)


def _looks_like_navigation_block(node: Tag) -> bool:
    """Detect compact navigation, breadcrumb, and language-picker blocks."""

    text = node.get_text(" ", strip=True).lower()
    if not text:
        return False
    marker_text = _marker_text(node)
    if any(marker in marker_text for marker in ("breadcrumb", "breadcrumbs", "translation", "translations", "menu", "nav", "toc", "socials")):
        return True
    if "other languages available" in text or "on this page" in text:
        return True
    if node.name.lower() == "nav":
        link_count = len(node.find_all("a"))
        text_words = len(text.split())
        return link_count >= 2 and text_words <= 40
    return False


def _looks_like_footer_block(node: Tag) -> bool:
    """Detect compact footer/legal blocks that should not appear in article output."""

    text = node.get_text(" ", strip=True).lower()
    if not text:
        return False
    marker_text = _marker_text(node)
    if any(marker in marker_text for marker in ("footer", "legal", "copyright")):
        return True
    if any(phrase in text for phrase in ("all rights reserved", "privacy settings", "modern slavery act statement")):
        return True
    return "©" in text and len(node.find_all("a")) >= 1


def _looks_like_tag_block(node: Tag) -> bool:
    """Detect compact tag lists made of tag permalink links only."""

    links = [child for child in node.find_all("a") if isinstance(child, Tag)]
    if len(links) < 2:
        return False
    if any(child.name in {"p", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "table", "blockquote"} for child in node.find_all(recursive=False)):
        return False
    texts = [link.get_text(" ", strip=True).lower() for link in links]
    hrefs = [str(link.get("href") or "").strip().lower() for link in links]
    if not all(texts):
        return False
    if not all(_is_tag_href(href) for href in hrefs):
        return False
    text = node.get_text(" ", strip=True).lower()
    word_count = len(text.split())
    return word_count <= 40 or text.startswith("tags:") or text.startswith("tag:")


def _looks_like_decorative_image_block(node: Tag) -> bool:
    """Detect image-only hero or background wrappers that should not render as content."""

    if node.name in {"img", "picture"}:
        return False
    marker_text = _marker_text(node)
    if not any(marker in marker_text for marker in ("background", "parallax", "top-bg")):
        return False
    if node.find(["p", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "table", "blockquote"]):
        return False
    image_count = len(node.find_all("img"))
    picture_count = len(node.find_all("picture"))
    text_words = len(node.get_text(" ", strip=True).split())
    return (image_count + picture_count) >= 1 and text_words <= 8


def _looks_like_link_chrome(node: Tag) -> bool:
    """Detect dense menu or footer blocks dominated by links rather than prose."""

    link_count = len(node.find_all("a"))
    paragraph_count = len(node.find_all("p"))
    heading_count = len(node.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]))
    word_count = len(node.get_text(" ", strip=True).split())
    if link_count >= 20 and paragraph_count <= 1 and heading_count <= 1 and word_count <= 160:
        return True
    if link_count >= 40 and paragraph_count <= 5 and word_count <= 260:
        return True
    if link_count >= 15 and paragraph_count == 0 and heading_count == 0 and word_count <= 120:
        return True
    return False


def _is_small_structural_block(node: Tag) -> bool:
    """Limit structural cleanup to compact blocks so wrappers with body text survive."""

    text_words = len(node.get_text(" ", strip=True).split())
    direct_blocks = sum(1 for child in node.find_all(recursive=False) if isinstance(child, Tag) and child.name in {"p", "ul", "ol", "li", "figure", "div", "section", "article"})
    return text_words <= 120 and direct_blocks <= 4


def _has_substantive_body_content(node: Tag) -> bool:
    """Keep compact wrappers that still contain real article paragraphs."""

    paragraph_count = len(node.find_all("p"))
    text_words = len(node.get_text(" ", strip=True).split())
    return paragraph_count >= 2 and text_words >= 15


def _marker_text(node: Tag) -> str:
    """Join class and id markers into a single lowercase string."""

    classes = node.get("class") or ()
    if not isinstance(classes, (list, tuple)):
        classes = (str(classes),)
    identifier = str(node.get("id", "")).lower()
    return " ".join([str(token).lower() for token in classes] + [identifier])


def _noise_tokens(classes: tuple[str, ...] | list[str] | tuple[object, ...], identifier: str) -> set[str]:
    """Split class and id markers into stable tokens for noise matching."""

    tokens: set[str] = set()
    for raw_token in classes:
        token = str(raw_token).lower()
        if not token:
            continue
        tokens.add(token)
        tokens.update(part for part in re.split(r"[^a-z0-9]+", token) if part)
    if identifier:
        tokens.add(identifier)
        tokens.update(part for part in re.split(r"[^a-z0-9]+", identifier) if part)
    return tokens


def _is_within_preserved_block(node: Tag) -> bool:
    """Keep nodes that live inside explicitly preserved content blocks."""

    current: Tag | None = node
    while isinstance(current, Tag):
        if current.get("data-domdown-keep-assets") == "true":
            return True
        current = current.parent if isinstance(current.parent, Tag) else None
    return False


def _is_within_code_block(node: NavigableString) -> bool:
    """Avoid stripping template placeholders from literal code samples."""

    current = node.parent
    while isinstance(current, Tag):
        if current.name in {"code", "pre", "textarea"}:
            return True
        current = current.parent if isinstance(current.parent, Tag) else None
    return False


def _is_tag_href(href: str) -> bool:
    """Return True for link targets that look like tag pages or tag anchors."""

    if not href:
        return False
    if href.startswith("#"):
        return True
    return "/tag/" in href or "/tags/" in href


def _looks_like_template_placeholder(text: str) -> bool:
    """Detect standalone template placeholders such as {{cta}}."""

    return bool(re.fullmatch(r"\s*\{\{\s*[a-z0-9_-]+\s*\}\}\s*", text.strip(), re.IGNORECASE))
