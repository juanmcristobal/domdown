from __future__ import annotations

from bs4 import BeautifulSoup, Tag

from .._constants import CONTENT_SELECTORS


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
        root = soup.select_one(selector)
        if isinstance(root, Tag):
            return _best_content_subtree(root)
    return soup.body if isinstance(soup.body, Tag) else soup


def _best_content_subtree(root: Tag) -> Tag:
    """Prefer the most content-dense subtree inside a shell element."""

    container_names = {"article", "body", "div", "main", "section"}
    candidates = []
    seen: set[int] = {id(root)}
    for selector in CONTENT_SELECTORS:
        for node in root.select(selector):
            if isinstance(node, Tag) and node.name in container_names and id(node) not in seen:
                candidates.append(node)
                seen.add(id(node))
    if candidates:
        return max(candidates, key=lambda tag: (_score_content(tag), _subtree_depth(root, tag), len(tag.get_text(" ", strip=True))))
    return root


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
