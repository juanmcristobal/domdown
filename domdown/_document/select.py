from __future__ import annotations

from bs4 import BeautifulSoup, Tag

from .._constants import CONTENT_SELECTORS_EXACT, CONTENT_SELECTORS_FALLBACK, NOISE_MARKERS


def choose_root(soup: BeautifulSoup, prefer_article_body: bool = True) -> Tag:
    """Choose the most relevant content root from a parsed document."""

    selectors = [".post-body", ".articlebody", "article", "main", "body"] if prefer_article_body else [
        ".articlebody",
        ".post-body",
        "article",
        "main",
        "body",
    ]
    for selector in selectors:
        for root in soup.select(selector):
            if isinstance(root, Tag) and not _looks_like_chrome(root):
                return _best_content_subtree(root)
    return soup.body if isinstance(soup.body, Tag) else soup


def _best_content_subtree(root: Tag) -> Tag:
    """Prefer the most content-dense subtree inside a shell element."""

    container_names = {"article", "body", "div", "main", "section"}
    exact = _collect_candidates(root, CONTENT_SELECTORS_EXACT, container_names)
    if exact:
        candidate = _pick_best_candidate(root, exact)
        if candidate is not None:
            return candidate

    fallback = _collect_candidates(root, CONTENT_SELECTORS_FALLBACK, container_names)
    if fallback:
        candidate = _pick_best_candidate(root, fallback)
        if candidate is not None:
            return candidate
    return root


def _collect_candidates(root: Tag, selectors: tuple[str, ...], container_names: set[str]) -> list[Tag]:
    """Collect unique content candidates for a given selector tier."""

    candidates: list[Tag] = []
    seen: set[int] = {id(root)}
    for selector in selectors:
        for node in root.select(selector):
            if isinstance(node, Tag) and node.name in container_names and id(node) not in seen:
                candidates.append(node)
                seen.add(id(node))
    return candidates


def _pick_best_candidate(root: Tag, candidates: list[Tag]) -> Tag | None:
    """Return the most plausible non-chrome candidate from a tier."""

    ranked = sorted(
        candidates,
        key=lambda tag: (_score_content(tag), _subtree_depth(root, tag), len(tag.get_text(" ", strip=True))),
        reverse=True,
    )
    for candidate in ranked:
        if not _looks_like_chrome(candidate):
            return candidate
    return None


def _score_content(tag: Tag) -> float:
    """Score a subtree by its likely article relevance."""

    text = tag.get_text(" ", strip=True)
    class_text = " ".join(tag.get("class", []) if isinstance(tag.get("class"), list) else [str(tag.get("class", ""))]).lower()
    id_text = str(tag.get("id", "")).lower()
    marker_text = f"{class_text} {id_text}"

    positive = 0.0
    positive += len(tag.find_all("p")) * 4.0
    positive += len(tag.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])) * 5.0
    positive += len(tag.find_all("li")) * 2.5
    positive += len(tag.find_all("blockquote")) * 3.0
    positive += len(tag.find_all("table")) * 6.0
    positive += len(tag.find_all("img")) * 3.0
    positive += len(tag.find_all(["pre", "code"])) * 2.0
    positive += min(len(text) / 400.0, 12.0)

    if any(marker in marker_text for marker in ("content", "body", "entry")):
        positive += 10.0
    elif "article" in marker_text:
        positive += 6.0
    elif "post" in marker_text:
        positive += 4.0

    noise = 0.0
    noise += len(tag.find_all(["a", "button", "form", "iframe", "input", "select", "textarea"])) * 0.3
    if any(marker in marker_text for marker in ("share", "social", "breadcrumb", "related", "recommend", "newsletter", "subscribe", "promo", "debug", "cta", "widget", "sidebar", "nav", "footer", "tags", "postmeta", "story-title", "post-head")):
        noise += 10.0
    noise += len(tag.find_all(True)) * 0.08

    return positive - noise


def _subtree_depth(root: Tag, tag: Tag) -> int:
    """Return how deeply nested a candidate is inside the chosen shell."""

    depth = 0
    current = tag
    while current is not root and current.parent is not None:
        depth += 1
        parent = current.parent
        if not isinstance(parent, Tag):
            break
        current = parent
    return depth


def _looks_like_chrome(tag: Tag) -> bool:
    """Identify obvious page chrome from class or id markers."""

    marker_text = " ".join([
        " ".join(tag.get("class", []) if isinstance(tag.get("class"), list) else [str(tag.get("class", ""))]),
        str(tag.get("id", "")),
    ]).lower()
    return any(marker in marker_text for marker in NOISE_MARKERS)
