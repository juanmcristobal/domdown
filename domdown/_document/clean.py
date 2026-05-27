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
            if _looks_like_hero_chrome(node):
                node.decompose()
                continue
            if _looks_like_metadata_bar(node):
                node.decompose()
                continue
            if _looks_like_decorative_image_block(node):
                node.decompose()
                continue
            if _looks_like_cta_block(node):
                node.decompose()
                continue
            if _looks_like_author_card_block(node):
                node.decompose()
                continue
            if _looks_like_article_feed_block(node):
                node.decompose()
                continue
            if _looks_like_promo_banner_block(node):
                node.decompose()
                continue
            if _looks_like_hidden_block(node):
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
    link_count = len(node.find_all("a"))
    word_count = len(text.split())
    if "enter search term" in text and word_count <= 20:
        return True
    marker_text = _marker_text(node)
    if any(marker in marker_text for marker in ("sticky-nav", "page-section-blog-head", "search-overlay")):
        return True
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
        if _looks_like_date_kicker(node):
            node.decompose()
            continue
        if _looks_like_footer_block(node):
            node.decompose()
            continue
        if _is_small_structural_block(node) and (
            _looks_like_header_block(node)
            or _looks_like_related_block(node)
            or _looks_like_category_block(node)
            or _looks_like_navigation_block(node)
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


def _looks_like_metadata_bar(node: Tag) -> bool:
    """Detect compact author/date/share bars near article headers."""

    text = node.get_text(" ", strip=True).lower()
    if not text:
        return False
    text_words = len(text.split())
    if text_words > 24:
        return False
    if "published on" in text and ("written by" in text or "author" in text or "share:" in text):
        return True
    if "last updated on" in text or "updated on" in text:
        return True
    if text.startswith("written by ") and ("published on" in text or "share:" in text):
        return True
    marker_text = _marker_text(node)
    if not any(token in marker_text for token in ("byline", "author", "date", "meta")):
        return False
    return bool(node.find("time")) and ("published" in text or "updated" in text)


def _looks_like_hero_chrome(node: Tag) -> bool:
    """Detect compact article hero wrappers with a back link plus metadata."""

    text = node.get_text(" ", strip=True).lower()
    if not text or len(text.split()) > 60:
        return False
    if not any(marker in text for marker in ("back to ", "return to ", "go back to ")):
        return False
    has_title = bool(node.find(["h1", "h2"]))
    has_metadata = bool(node.find("time")) or any(token in text for token in ("author", "read", "min", "date", "category"))
    has_back_link = bool(
        node.find(
            lambda child: isinstance(child, Tag)
            and child.name == "a"
            and child.get_text(" ", strip=True).lower().startswith("back to ")
        )
    )
    return has_title and has_metadata and has_back_link


def _looks_like_related_block(node: Tag) -> bool:
    """Detect related-link sections that sit between the header and body."""

    text = node.get_text(" ", strip=True).lower()
    word_count = len(text.split())
    link_count = len(node.find_all("a"))
    if any(phrase in text for phrase in RELATED_PHRASES) and (word_count <= 18 or link_count >= 2):
        return True
    marker_text = _marker_text(node)
    return any(marker in marker_text for marker in ("related", "recommend"))


def _looks_like_category_block(node: Tag) -> bool:
    """Detect compact article category blocks that only label link lists."""

    text = node.get_text(" ", strip=True).lower()
    if "categories" not in text:
        return False
    link_count = len(node.find_all("a"))
    word_count = len(text.split())
    if link_count < 2 or word_count > 24:
        return False
    return True


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


def _looks_like_cta_block(node: Tag) -> bool:
    """Detect compact call-to-action cards that are not part of article prose."""

    marker_text = _marker_text(node)
    if not any(marker in marker_text for marker in ("cta", "banner", "promo", "callout")):
        return False
    heading_count = len(node.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]))
    paragraph_count = len(node.find_all("p"))
    link_count = len(node.find_all("a"))
    button_count = len(node.find_all("button"))
    text_words = len(node.get_text(" ", strip=True).split())
    has_heading_like_descendant = bool(
        node.find(
            lambda child: isinstance(child, Tag)
            and (
                child.name in {"h1", "h2", "h3", "h4", "h5", "h6"}
                or any(token in _marker_text(child) for token in ("heading", "title", "top-heading"))
            )
        )
    )
    has_button_like_descendant = bool(
        node.find(
            lambda child: isinstance(child, Tag)
            and (
                child.name == "button"
                or "btn-wrapper" in (child.get("class") or ())
                or any(
                    token in _marker_text(child)
                    for token in ("primary-btn", "secondary-btn", "button", "btn")
                )
            )
        )
    )
    if not has_heading_like_descendant and heading_count < 1:
        return False
    if text_words > 60:
        return False
    if paragraph_count > 2:
        return False
    return has_button_like_descendant


def _looks_like_author_card_block(node: Tag) -> bool:
    """Detect compact author/share cards that belong to page chrome."""

    text = node.get_text(" ", strip=True).lower()
    if not text or "share" not in text:
        return False
    if not text.startswith("author "):
        return False
    if len(text.split()) > 10:
        return False
    return len(node.find_all("button")) >= 1 or len(node.find_all("a")) >= 1


def _looks_like_article_feed_block(node: Tag) -> bool:
    """Detect compact blog-feed or related-article strips rendered as cards."""

    text = node.get_text(" ", strip=True).lower()
    if not text:
        return False
    heading_count = len(node.find_all(["h1", "h2", "h3"]))
    image_count = len(node.find_all("img"))
    text_words = len(text.split())
    marker_text = _marker_text(node)
    card_like_children = sum(
        1
        for child in node.find_all(True)
        if isinstance(child, Tag)
        and child is not node
        and (
            any(
                token in _marker_text(child)
                for token in (
                    "card",
                    "dyn-item",
                )
            )
        )
        and len(child.find_all(["h1", "h2", "h3"])) >= 1
    )
    if "similar posts" in text and heading_count >= 2 and image_count >= 2 and text_words <= 260:
        return True
    if card_like_children >= 2 and heading_count >= 2 and image_count >= 2 and text_words <= 260:
        return True
    article_count = len(node.find_all("article"))
    if article_count >= 2:
        return any(phrase in text for phrase in ("latest", "related", "similar posts", "more from", "you may also like", "recommended", "blogs")) and text_words <= 220
    if any(phrase in text for phrase in ("the latest from", "latest from", "related articles", "similar posts", "more from", "you may also like", "recommended")):
        return text_words <= 30
    if any(token in marker_text for token in ("blog", "card", "posts", "feed", "related", "recommend", "category")) and card_like_children >= 2:
        return text_words <= 220 and heading_count >= 2
    return False


def _looks_like_promo_banner_block(node: Tag) -> bool:
    """Detect compact marketing banners with repeated CTA links or buttons."""

    text = node.get_text(" ", strip=True).lower()
    if not text:
        return False
    if node.name.lower() == "main":
        return False
    heading_count = len(node.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]))
    paragraph_count = len(node.find_all("p"))
    link_count = len(node.find_all("a"))
    button_count = len(node.find_all("button"))
    marker_text = _marker_text(node)
    if len(text.split()) > 80:
        return False
    cta_phrases = (
        "book a demo",
        "star on github",
        "start free",
        "get started",
        "learn more",
        "sign up",
        "try free",
        "view all blogs",
    )
    if not any(phrase in text for phrase in cta_phrases):
        return False
    if link_count + button_count < 1:
        return False
    if any(marker in marker_text for marker in ("cta", "banner", "promo", "callout")):
        return True
    if "intro" in marker_text:
        return False
    return heading_count <= 2 and paragraph_count <= 3


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
    link_count = len(node.find_all("a"))
    word_count = len(text.split())
    if node.name.lower() == "nav":
        return link_count >= 2 and word_count <= 40
    return False


def _looks_like_date_kicker(node: Tag) -> bool:
    """Detect isolated article date lines in top-of-page headers."""

    text = node.get_text(" ", strip=True)
    if not text:
        return False
    if len(text.split()) > 3:
        return False
    if not re.fullmatch(r"\d{2}/\d{2}/\d{4}", text):
        return False
    marker_text = _marker_text(node)
    if not any(token in marker_text for token in ("subtitle", "date", "time")):
        return False
    parent = node.parent if isinstance(node.parent, Tag) else None
    if parent is None:
        return False
    if parent.find(["h1", "h2"], recursive=False) is not None:
        return True
    return any(token in _marker_text(parent) for token in ("header", "article"))


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


def _looks_like_hidden_block(node: Tag) -> bool:
    """Detect blocks that are intentionally hidden from the rendered page."""

    if node.has_attr("hidden"):
        return True
    classes = node.get("class") or ()
    if not isinstance(classes, (list, tuple)):
        classes = (str(classes),)
    return any(str(token).lower() == "hidden" for token in classes)


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
