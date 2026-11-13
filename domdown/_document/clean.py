from __future__ import annotations

import re
from collections.abc import Callable

from bs4 import Comment, NavigableString, Tag

from .._constants import BOILERPLATE_PHRASES, DEFAULT_REMOVE_SELECTORS, HEADER_MARKERS, NOISE_MARKERS, RELATED_PHRASES

_DEFAULT_REMOVE_CLASSES = frozenset(selector[1:] for selector in DEFAULT_REMOVE_SELECTORS if selector.startswith("."))
_DEFAULT_REMOVE_IDS = frozenset(selector[1:] for selector in DEFAULT_REMOVE_SELECTORS if selector.startswith("#"))
_DEFAULT_REMOVE_CLASS_SUBSTRINGS = tuple(
    selector[len("[class*='") : -2] for selector in DEFAULT_REMOVE_SELECTORS if selector.startswith("[class*='")
)
_DEFAULT_REMOVE_ID_SUBSTRINGS = tuple(
    selector[len("[id*='") : -2] for selector in DEFAULT_REMOVE_SELECTORS if selector.startswith("[id*='")
)
_DEFAULT_REMOVE_REL_SUBSTRINGS = tuple(
    selector[len("[rel*='") : -2] for selector in DEFAULT_REMOVE_SELECTORS if selector.startswith("[rel*='")
)
_DEFAULT_REMOVE_LINK_HREFS = frozenset(
    selector[len("a[href='") : -2] for selector in DEFAULT_REMOVE_SELECTORS if selector.startswith("a[href='")
)


def clean_root(
    root: Tag,
    remove_selectors: tuple[str, ...],
    skip_tags: set[str],
    preserve_chrome: bool = False,
    *,
    apply_extraction_heuristics: bool = True,
) -> Tag:
    """Remove obvious noise and normalize lazy-loaded images in place."""

    if apply_extraction_heuristics:
        for comment in root.find_all(string=lambda value: isinstance(value, Comment)):
            comment.extract()

    for text_node in list(root.find_all(string=True)) if apply_extraction_heuristics else ():
        if (
            isinstance(text_node, NavigableString)
            and _looks_like_template_placeholder(str(text_node))
            and not _is_within_code_block(text_node)
        ):
            text_node.extract()

    if remove_selectors == DEFAULT_REMOVE_SELECTORS:
        # These selectors only match tag names and attributes, so one DOM pass
        # can find every match before removals without changing selector results.
        matches = _default_remove_matches(root)
        for node in reversed(matches):
            node.decompose()
    else:
        for selector in remove_selectors:
            for node in root.select(selector):
                node.decompose()

    _promote_image_fallbacks(root)
    if not preserve_chrome and apply_extraction_heuristics:
        _mark_detached_article_title(root)
        for node in list(root.find_all(True)):
            if not isinstance(node, Tag) or getattr(node, "attrs", None) is None:
                continue
            if _is_within_preserved_block(node):
                continue
            if node.get("data-domdown-primary-title") == "true":
                if node.parent is root:
                    _remove_pre_title_navigation(node, root)
                continue
            if node.name in skip_tags:
                node.decompose()
                continue
            text_getter = _cached_text_getter(node)
            if _looks_like_hidden_block(node):
                node.decompose()
                continue
            if _looks_like_cta_block(node, text_getter):
                node.decompose()
                continue
            if _looks_like_author_profile_block(node, text_getter):
                node.decompose()
                continue
            if _looks_like_testimonial_block(node, text_getter):
                node.decompose()
                continue
            if _looks_like_decorative_image_block(node, text_getter):
                node.decompose()
                continue
            if _looks_like_hero_chrome(node, text_getter):
                node.decompose()
                continue
            if _looks_like_metadata_bar(node, text_getter):
                node.decompose()
                continue
            if _looks_like_form_module(node, text_getter):
                node.decompose()
                continue
            if _looks_like_author_card_block(node, text_getter):
                node.decompose()
                continue
            if _looks_like_article_feed_block(node, text_getter):
                node.decompose()
                continue
            if _looks_like_promo_banner_block(node, text_getter):
                node.decompose()
                continue
            if _looks_like_noise(node, text_getter) and not _has_substantive_body_content(node, text_getter):
                node.decompose()

        _remove_structural_chrome(root)

    for node in root.find_all(attrs={"data-domdown-primary-title": "true"}):
        node.attrs.pop("data-domdown-primary-title", None)

    for node in list(root.find_all(skip_tags)):
        node.decompose()
    for img in root.find_all("img"):
        data_src = img.get("data-src") or img.get("data-original") or img.get("data-lazy-src")
        if data_src and (not img.get("src") or str(img.get("src", "")).startswith("data:")):
            img["src"] = data_src
    return root


def _default_remove_matches(root: Tag) -> list[Tag]:
    """Find nodes matching the fixed default selectors in one traversal."""

    matches: list[Tag] = []
    for node in root.descendants:
        if not isinstance(node, Tag):
            continue
        raw_classes = node.get("class") or ()
        classes = raw_classes if isinstance(raw_classes, (list, tuple)) else str(raw_classes).split()
        class_value = " ".join(str(value) for value in classes)
        identifier = str(node.get("id") or "")
        rel = node.get("rel") or ()
        rel_value = " ".join(str(value) for value in rel) if isinstance(rel, (list, tuple)) else str(rel)
        href = node.get("href")
        if (
            _DEFAULT_REMOVE_CLASSES.intersection(classes)
            or identifier in _DEFAULT_REMOVE_IDS
            or any(value in class_value for value in _DEFAULT_REMOVE_CLASS_SUBSTRINGS)
            or any(value in identifier for value in _DEFAULT_REMOVE_ID_SUBSTRINGS)
            or any(value in rel_value for value in _DEFAULT_REMOVE_REL_SUBSTRINGS)
            or (node.name == "a" and href in _DEFAULT_REMOVE_LINK_HREFS)
        ):
            matches.append(node)
    return matches


def _looks_like_noise(node: Tag, text_getter: Callable[[], str] | None = None) -> bool:
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
    text = _get_node_text(node, text_getter).lower()
    word_count = len(text.split())
    if "enter search term" in text and word_count <= 20:
        return True
    marker_text = _marker_text(node)
    if any(marker in marker_text for marker in ("sticky-nav", "page-section-blog-head", "search-overlay")):
        return True
    if _looks_like_link_chrome(node, text_getter):
        return True
    return text == "more" and bool(tokens & {"more", "share"})


def _remove_structural_chrome(root: Tag) -> None:
    """Remove small header and related-link chrome blocks from the chosen root."""

    _remove_article_header_cluster(root)

    for node in reversed(list(root.find_all(True))):
        if not isinstance(node, Tag) or node is root:
            continue
        if _is_within_preserved_block(node):
            continue
        text_getter = _cached_text_getter(node)
        if _looks_like_date_kicker(node, text_getter):
            node.decompose()
            continue
        if _looks_like_footer_block(node, text_getter):
            node.decompose()
            continue
        if _is_small_structural_block(node, text_getter) and (
            _looks_like_header_block(node, text_getter)
            or _looks_like_related_block(node, text_getter)
            or _looks_like_category_block(node, text_getter)
            or _looks_like_navigation_block(node, text_getter)
            or _looks_like_tag_block(node, text_getter)
            or _looks_like_boilerplate(node, text_getter)
            or _looks_like_about_block(node, text_getter)
        ):
            if _has_substantive_body_content(node, text_getter):
                continue
            node.decompose()


def _remove_article_header_cluster(root: Tag) -> None:
    """Remove blog header controls when their labels occur as one cluster."""

    headings = [node for node in root.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]) if isinstance(node, Tag)]
    labels = {node.get_text(" ", strip=True).lower().rstrip(":") for node in headings}
    if not ({"topics", "share"} <= labels):
        return

    removable = {"topics", "table of contents", "share"}
    for heading in headings:
        label = heading.get_text(" ", strip=True).lower().rstrip(":")
        if label not in removable:
            continue
        for sibling in list(heading.next_siblings):
            if isinstance(sibling, Tag) and sibling.name.lower() in {"h1", "h2", "h3", "h4", "h5", "h6"}:
                break
            if isinstance(sibling, Tag):
                sibling.decompose()
        heading.decompose()


def _looks_like_header_block(node: Tag, text_getter: Callable[[], str] | None = None) -> bool:
    """Detect top-of-article blocks that repeat title, byline, or date metadata."""

    if node.get("data-domdown-primary-title") == "true":
        return False

    marker_text = _marker_text(node)
    if any(marker in marker_text for marker in HEADER_MARKERS):
        return True
    has_title_like_heading = bool(node.find(["h1", "h2"], recursive=False))
    has_metadata = bool(node.find("time", recursive=False)) or any(
        token in marker_text for token in ("byline", "author", "date", "time", "meta")
    )
    if not has_title_like_heading or not has_metadata:
        return False
    text_words = len(_get_node_text(node, text_getter).split())
    if text_words > 80:
        return False
    return len(node.find_all("p", limit=3)) <= 2


def _mark_detached_article_title(root: Tag) -> None:
    """Protect a compact detached H1 when its sibling carries the editorial body."""

    headings = root.find_all("h1")
    for heading in headings:
        title_branch: Tag = heading
        while isinstance(title_branch.parent, Tag) and title_branch.parent is not root:
            title_branch = title_branch.parent
        if title_branch.parent is not root or len(title_branch.get_text(" ", strip=True).split()) > 160:
            continue

        has_substantial_sibling = False
        for sibling in root.find_all(recursive=False):
            if not isinstance(sibling, Tag) or sibling is title_branch or heading in sibling.descendants:
                continue
            words = len(sibling.get_text(" ", strip=True).split())
            structured_blocks = len(sibling.find_all(["table", "pre", "blockquote", "ul", "ol"]))
            if words >= 250 and (len(sibling.find_all("p")) >= 4 or structured_blocks >= 2):
                has_substantial_sibling = True
                break
        if not has_substantial_sibling:
            continue

        current: Tag | None = heading
        while current is not None and current is not root:
            current["data-domdown-primary-title"] = "true"
            current = current.parent if isinstance(current.parent, Tag) else None
        return


def _remove_pre_title_navigation(header: Tag, root: Tag) -> None:
    """Remove small link-only breadcrumbs before a preserved article title."""

    heading = header.find("h1")
    if not isinstance(heading, Tag):
        return
    current: Tag = heading
    while current is not root:
        for sibling in list(current.previous_siblings):
            if not isinstance(sibling, Tag):
                continue
            links = len(sibling.find_all("a")) + int(sibling.name == "a")
            words = len(sibling.get_text(" ", strip=True).split())
            has_editorial_structure = sibling.find(["p", "h1", "h2", "h3", "table", "pre", "blockquote"]) is not None
            if links and links <= 5 and words <= 35 and not has_editorial_structure:
                sibling.decompose()
        if not isinstance(current.parent, Tag):
            break
        current = current.parent


def _promote_image_fallbacks(root: Tag) -> None:
    """Use a non-inline image source from noscript fallbacks before removing them."""

    for image in root.find_all("img"):
        if image.find_parent("noscript") is not None:
            continue
        source = str(image.get("src") or "")
        if source and not source.lower().startswith("data:image/"):
            continue
        figure = image.find_parent("figure")
        if not isinstance(figure, Tag):
            continue
        fallback = next(
            (
                item
                for item in figure.select("noscript img")
                if (item.get("src") or "") and not str(item.get("src")).lower().startswith("data:image/")
            ),
            None,
        )
        if isinstance(fallback, Tag):
            image["src"] = fallback["src"]
            if not image.get("alt") and fallback.get("alt"):
                image["alt"] = fallback["alt"]


def _looks_like_metadata_bar(node: Tag, text_getter: Callable[[], str] | None = None) -> bool:
    """Detect compact author/date/share bars near article headers."""

    text = _get_node_text(node, text_getter).lower()
    if not text:
        return False
    text_words = len(text.split())
    if text_words > 24:
        return False
    if "published on" in text and ("written by" in text or "author" in text or "share:" in text):
        return True
    if text.startswith("contributor:"):
        return True
    if "time to read:" in text and len(text_words := text.split()) <= 16:
        return True
    marker_text = _marker_text(node)
    if any(marker in marker_text for marker in ("published", "publish-date", "read-time", "reading-time")):
        return True
    if "last updated on" in text or "updated on" in text:
        return True
    if text.startswith("written by ") and ("published on" in text or "share:" in text):
        return True
    if not any(token in marker_text for token in ("byline", "author", "date", "meta")):
        return False
    return bool(node.find("time")) and ("published" in text or "updated" in text)


def _looks_like_hero_chrome(node: Tag, text_getter: Callable[[], str] | None = None) -> bool:
    """Detect compact article hero wrappers with a back link plus metadata."""

    text = _get_node_text(node, text_getter).lower()
    if not text or len(text.split()) > 60:
        return False
    if not any(marker in text for marker in ("back to ", "return to ", "go back to ")):
        return False
    has_title = bool(node.find(["h1", "h2"]))
    has_metadata = bool(node.find("time")) or any(
        token in text for token in ("author", "read", "min", "date", "category")
    )
    has_back_link = bool(
        node.find(
            lambda child: isinstance(child, Tag)
            and child.name == "a"
            and child.get_text(" ", strip=True).lower().startswith("back to ")
        )
    )
    return has_title and has_metadata and has_back_link


def _looks_like_related_block(node: Tag, text_getter: Callable[[], str] | None = None) -> bool:
    """Detect related-link sections that sit between the header and body."""

    marker_text = _marker_text(node)
    if any(marker in marker_text for marker in ("related", "recommend")):
        return True
    text = _get_node_text(node, text_getter).lower()
    word_count = len(text.split())
    if any(phrase in text for phrase in RELATED_PHRASES):
        return word_count <= 18 or len(node.find_all("a", limit=2)) >= 2
    return False


def _looks_like_category_block(node: Tag, text_getter: Callable[[], str] | None = None) -> bool:
    """Detect compact article category blocks that only label link lists."""

    text = _get_node_text(node, text_getter).lower()
    if "categories" not in text:
        return False
    link_count = len(node.find_all("a"))
    word_count = len(text.split())
    if link_count < 2 or word_count > 24:
        return False
    return True


def _looks_like_boilerplate(node: Tag, text_getter: Callable[[], str] | None = None) -> bool:
    """Detect compact documentation or feedback boilerplate blocks."""

    text = _get_node_text(node, text_getter).lower()
    return any(phrase in text for phrase in BOILERPLATE_PHRASES)


def _looks_like_about_block(node: Tag, text_getter: Callable[[], str] | None = None) -> bool:
    """Detect compact company/about blocks with a heading and CTA links."""

    heading = node.find(["h1", "h2", "h3", "h4"], recursive=False)
    if not isinstance(heading, Tag):
        return False
    heading_text = heading.get_text(" ", strip=True).lower()
    if not heading_text.startswith("about "):
        return False
    has_link_or_button = node.find(["a", "button"]) is not None
    text_words = len(_get_node_text(node, text_getter).split())
    return text_words <= 120 and has_link_or_button


def _looks_like_cta_block(node: Tag, text_getter: Callable[[], str] | None = None) -> bool:
    """Detect compact call-to-action cards that are not part of article prose."""

    marker_text = _marker_text(node)
    if not any(marker in marker_text for marker in ("cta", "banner", "promo", "callout")):
        return False
    text_words = len(_get_node_text(node, text_getter).split())
    if text_words > 60:
        return False
    paragraph_count = len(node.find_all("p", limit=3))
    if paragraph_count > 2:
        return False
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
                or any(token in _marker_text(child) for token in ("primary-btn", "secondary-btn", "button", "btn"))
            )
        )
    )
    if not has_heading_like_descendant:
        return False
    if not has_button_like_descendant:
        return False
    return True


def _looks_like_author_card_block(node: Tag, text_getter: Callable[[], str] | None = None) -> bool:
    """Detect compact author/share cards that belong to page chrome."""

    text = _get_node_text(node, text_getter).lower()
    if not text or "share" not in text:
        return False
    if not text.startswith("author "):
        return False
    if len(text.split()) > 10:
        return False
    return node.find(["button", "a"]) is not None


def _looks_like_author_profile_block(node: Tag, text_getter: Callable[[], str] | None = None) -> bool:
    """Remove author biographies and profile cards while preserving short bylines."""

    marker_tokens = _noise_tokens(node.get("class") or (), str(node.get("id") or ""))
    if not marker_tokens & {"author", "bio", "profile", "contributor"}:
        return False
    if node.find(["table", "pre", "code", "blockquote"]):
        return False
    text = _get_node_text(node, text_getter).lower()
    if len(text.split()) > 350:
        return False
    has_profile_signals = (
        node.find("img") is not None
        or len(node.find_all("p", limit=2)) >= 2
        or any(phrase in text for phrase in ("about the author", "author bio", "biography", "follow "))
        or (len(node.find_all("a", limit=3)) >= 3 and len(text.split()) > 35)
    )
    return has_profile_signals and len(text.split()) > 16


def _looks_like_testimonial_block(node: Tag, text_getter: Callable[[], str] | None = None) -> bool:
    """Remove customer testimonial modules without treating editorial quotes as boilerplate."""

    marker_text = _marker_text(node)
    if not any(marker in marker_text for marker in ("testimonial", "customer-quote", "customer_quote")):
        return False
    return len(_get_node_text(node, text_getter).split()) <= 500 and node.find(["table", "pre", "code"]) is None


def _looks_like_form_module(node: Tag, text_getter: Callable[[], str] | None = None) -> bool:
    """Drop compact wrappers around interactive forms, keeping editorial prose intact."""

    if node.name in {"article", "main"} or node.find("form") is None:
        return False
    if node.find(["table", "pre", "code", "blockquote"]) is not None:
        return False
    return len(_get_node_text(node, text_getter).split()) <= 180 and len(node.find_all("p", limit=2)) <= 1


def _count_card_like_children(node: Tag, headings: list[Tag], limit: int = 2) -> int:
    """Count card-marked descendants of node that contain a heading, stopping at limit.

    Walks upward from each heading once (visited ancestors are skipped), so the cost is
    linear in the subtree instead of re-scanning every card's subtree.
    """

    seen: set[int] = set()
    count = 0
    for heading in headings:
        parent = heading.parent
        while isinstance(parent, Tag) and parent is not node and id(parent) not in seen:
            seen.add(id(parent))
            if any(token in _marker_text(parent) for token in ("card", "dyn-item")):
                count += 1
                if count >= limit:
                    return count
            parent = parent.parent
    return count


def _looks_like_article_feed_block(node: Tag, text_getter: Callable[[], str] | None = None) -> bool:
    """Detect compact blog-feed or related-article strips rendered as cards."""

    text = _get_node_text(node, text_getter).lower()
    if not text:
        return False
    text_words = len(text.split())
    if text_words > 260:
        return False
    heading_count = len(headings := node.find_all(["h1", "h2", "h3"]))
    image_count = len(node.find_all("img", limit=2))
    marker_text = _marker_text(node)
    card_like_children = _count_card_like_children(node, headings)
    if "similar posts" in text and heading_count >= 2 and image_count >= 2 and text_words <= 260:
        return True
    if card_like_children >= 2 and heading_count >= 2 and image_count >= 2 and text_words <= 260:
        return True
    article_count = len(node.find_all("article", limit=2))
    if article_count >= 2:
        return (
            any(
                phrase in text
                for phrase in (
                    "latest",
                    "related",
                    "continue reading",
                    "similar posts",
                    "more from",
                    "you may also like",
                    "recommended",
                    "blogs",
                )
            )
            and text_words <= 220
        )
    if any(
        phrase in text
        for phrase in (
            "the latest from",
            "latest from",
            "related articles",
            "similar posts",
            "more from",
            "you may also like",
            "recommended",
            "continue reading",
            "more stories",
            "read next",
        )
    ):
        return text_words <= 30
    if (
        any(token in marker_text for token in ("blog", "card", "posts", "feed", "related", "recommend", "category"))
        and card_like_children >= 2
    ):
        return text_words <= 220 and heading_count >= 2
    return False


def _looks_like_promo_banner_block(node: Tag, text_getter: Callable[[], str] | None = None) -> bool:
    """Detect compact marketing banners with repeated CTA links or buttons."""

    if node.name.lower() == "main":
        return False
    text = _get_node_text(node, text_getter).lower()
    if not text:
        return False
    marker_text = _marker_text(node)
    specific_cta_phrases = (
        "book a demo",
        "get a demo",
        "request a demo",
        "schedule a demo",
        "contact us",
        "talk to sales",
        "ready to see",
    )
    cta_phrases = specific_cta_phrases + (
        "act now",
        "star on github",
        "start free",
        "get started",
        "learn more",
        "sign up",
        "try free",
        "view all blogs",
        "webinar",
        "register now",
        "search products",
    )
    if not any(phrase in text for phrase in cta_phrases):
        return False
    has_specific_cta = any(phrase in text for phrase in specific_cta_phrases)
    max_words = 90 if has_specific_cta else 40
    text_words = len(text.split())
    if text_words > max_words:
        return False
    if node.find(["a", "button"]) is None:
        return False
    has_button_like_link = any(
        any("button" in str(token).lower() or str(token).lower().endswith("btn") for token in (link.get("class") or ()))
        for link in node.find_all("a")
    )
    if (
        has_specific_cta
        and node.find(["h1", "h2", "h3", "h4", "h5", "h6"]) is None
        and node.find("button") is None
        and not has_button_like_link
    ):
        return False
    if "login" in text and any(phrase in text for phrase in ("act now", "sign up", "register now", "start free")):
        return True
    if "webinar" in text and ("register" in text or "login" in text):
        return True
    if "blog-next" in marker_text or "what's next" in text or "next step" in text:
        return True
    if any(marker in marker_text for marker in ("cta", "banner", "promo", "callout")):
        return True
    if "intro" in marker_text:
        return False
    heading_count = len(node.find_all(["h1", "h2", "h3", "h4", "h5", "h6"], limit=3))
    if heading_count > 2:
        return False
    paragraph_count = len(node.find_all("p", limit=4))
    return paragraph_count <= 3


def _looks_like_navigation_block(node: Tag, text_getter: Callable[[], str] | None = None) -> bool:
    """Detect compact navigation, breadcrumb, and language-picker blocks."""

    marker_text = _marker_text(node).replace("toc-visible", "tocvisible")
    if any(
        marker in marker_text
        for marker in ("breadcrumb", "breadcrumbs", "translation", "translations", "menu", "nav", "toc", "socials")
    ):
        return True
    text = _get_node_text(node, text_getter).lower()
    if not text:
        return False
    if "other languages available" in text or "on this page" in text:
        return True
    word_count = len(text.split())
    if node.name.lower() == "nav":
        return len(node.find_all("a", limit=2)) >= 2 and word_count <= 40
    return False


def _looks_like_date_kicker(node: Tag, text_getter: Callable[[], str] | None = None) -> bool:
    """Detect isolated article date lines in top-of-page headers."""

    text = _get_node_text(node, text_getter)
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


def _looks_like_footer_block(node: Tag, text_getter: Callable[[], str] | None = None) -> bool:
    """Detect compact footer/legal blocks that should not appear in article output."""

    if node.name.lower() == "footer":
        return True
    marker_text = _marker_text(node)
    if any(marker in marker_text for marker in ("footer", "legal", "copyright")):
        return True
    text = _get_node_text(node, text_getter).lower()
    if not text:
        return False
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


def _looks_like_tag_block(node: Tag, text_getter: Callable[[], str] | None = None) -> bool:
    """Detect compact tag lists made of tag permalink links only."""

    links = [child for child in node.find_all("a") if isinstance(child, Tag)]
    if len(links) < 2:
        return False
    if any(
        child.name in {"p", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "table", "blockquote"}
        for child in node.find_all(recursive=False)
    ):
        return False
    texts = [link.get_text(" ", strip=True).lower() for link in links]
    hrefs = [str(link.get("href") or "").strip().lower() for link in links]
    if not all(texts):
        return False
    if not all(_is_tag_href(href) for href in hrefs):
        return False
    text = _get_node_text(node, text_getter).lower()
    word_count = len(text.split())
    return word_count <= 40 or text.startswith("tags:") or text.startswith("tag:")


def _looks_like_decorative_image_block(node: Tag, text_getter: Callable[[], str] | None = None) -> bool:
    """Detect image-only hero or background wrappers that should not render as content."""

    if node.name in {"img", "picture"}:
        return False
    marker_text = _marker_text(node)
    if not any(marker in marker_text for marker in ("background", "parallax", "top-bg")):
        return False
    if node.find(["p", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "table", "blockquote"]):
        return False
    has_image = node.find(["img", "picture"]) is not None
    text_words = len(_get_node_text(node, text_getter).split())
    return has_image and text_words <= 8


def _looks_like_link_chrome(node: Tag, text_getter: Callable[[], str] | None = None) -> bool:
    """Detect dense menu or footer blocks dominated by links rather than prose."""

    link_count = len(node.find_all("a", limit=40))
    if link_count < 15:
        return False
    paragraph_count = len(node.find_all("p", limit=6))
    heading_count = len(node.find_all(["h1", "h2", "h3", "h4", "h5", "h6"], limit=2))
    word_count = len(_get_node_text(node, text_getter).split())
    if link_count >= 20 and paragraph_count <= 1 and heading_count <= 1 and word_count <= 160:
        return True
    if link_count >= 40 and paragraph_count <= 5 and word_count <= 260:
        return True
    if link_count >= 15 and paragraph_count == 0 and heading_count == 0 and word_count <= 120:
        return True
    return False


def _is_small_structural_block(node: Tag, text_getter: Callable[[], str] | None = None) -> bool:
    """Limit structural cleanup to compact blocks so wrappers with body text survive."""

    direct_blocks = sum(
        1
        for child in node.find_all(recursive=False)
        if isinstance(child, Tag) and child.name in {"p", "ul", "ol", "li", "figure", "div", "section", "article"}
    )
    if direct_blocks > 4:
        return False
    return len(_get_node_text(node, text_getter).split()) <= 120


def _has_substantive_body_content(node: Tag, text_getter: Callable[[], str] | None = None) -> bool:
    """Keep compact wrappers that still contain real article paragraphs."""

    paragraph_count = len(node.find_all("p", limit=2))
    text_words = len(_get_node_text(node, text_getter).split())
    return paragraph_count >= 2 and text_words >= 15


def _marker_text(node: Tag) -> str:
    """Join class and id markers into a single lowercase string."""

    classes = node.get("class") or ()
    if not isinstance(classes, (list, tuple)):
        classes = (str(classes),)
    identifier = str(node.get("id", "")).lower()
    return " ".join([str(token).lower() for token in classes] + [identifier])


def _cached_text_getter(node: Tag) -> Callable[[], str]:
    """Cache a node's text only for the current, non-mutating rule evaluation."""

    text: str | None = None

    def get_text() -> str:
        nonlocal text
        if text is None:
            text = node.get_text(" ", strip=True)
        return text

    return get_text


def _get_node_text(node: Tag, text_getter: Callable[[], str] | None) -> str:
    """Get node text, reusing a caller's local cache when provided."""

    if text_getter is not None:
        return text_getter()
    return node.get_text(" ", strip=True)


def _noise_tokens(classes: tuple[str, ...] | list[str] | tuple[object, ...], identifier: str) -> set[str]:
    """Split class and id markers into stable tokens for noise matching."""

    tokens: set[str] = set()
    for raw_token in classes:
        token = str(raw_token).lower()
        if not token:
            continue
        tokens.add(token)
        split_token = token.replace("toc-visible", "tocvisible")
        tokens.update(part for part in re.split(r"[^a-z0-9]+", split_token) if part)
    if identifier:
        identifier = identifier.lower()
        tokens.add(identifier)
        split_identifier = identifier.replace("toc-visible", "tocvisible")
        tokens.update(part for part in re.split(r"[^a-z0-9]+", split_identifier) if part)
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
