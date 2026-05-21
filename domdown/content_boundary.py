from __future__ import annotations

import re
from typing import Optional

from bs4 import Tag

from domdown.utils import count_words, normalize_text
from domdown.utils.dom import closest

DATE_PATTERN = re.compile(
    r"(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}"
    r"|\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*"
    r"|\d{4}[-/]\d{1,2}[-/]\d{1,2})",
    re.IGNORECASE,
)
BYLINE_PATTERN = re.compile(r"^by\s+\S", re.IGNORECASE)
SENTENCE_PUNCT = re.compile(r"[.!?]")
HIDDEN_CLASS_RE = re.compile(r"\b(?:isHidden(?:-[A-Za-z0-9_]+)?|is-hidden)\b")

CANDIDATE_TAGS = frozenset(["p", "div", "section", "article", "blockquote", "font"])
LEAF_CANDIDATE_TAGS = frozenset(["p", "blockquote", "font"])

DIALOG_SELECTOR = '[role="dialog"], [role="alertdialog"]'
SKIP_ANCESTOR_SELECTOR = f"aside, nav, header, footer, form, {DIALOG_SELECTOR}"
PROSE_MIN_WORDS = 7


def _find_title_element(main_content: Tag, title: str) -> Optional[Tag]:
    normalized_title = normalize_text(title)
    if not normalized_title:
        return None
    headings = main_content.select("h1, h2")
    for h in headings:
        if normalize_text(h.get_text()) == normalized_title:
            return h
    return None


def _link_text_length(el: Tag) -> int:
    total = 0
    for a in el.select("a"):
        total += len(a.get_text())
    return total


def _is_prose_block(el: Tag) -> bool:
    if not hasattr(el, "name") or el.name is None:
        return False
    if el.name not in CANDIDATE_TAGS:
        return False
    if closest(el, SKIP_ANCESTOR_SELECTOR):
        return False
    class_name = el.get("class", "")
    if isinstance(class_name, list):
        class_name = " ".join(class_name)
    if HIDDEN_CLASS_RE.search(class_name):
        return False
    if el.select_one(DIALOG_SELECTOR):
        return False
    if el.select_one("script, style"):
        return False

    text = el.get_text().strip()
    if not text:
        return False
    words = count_words(text)
    if words < PROSE_MIN_WORDS:
        return False
    if not SENTENCE_PUNCT.search(text):
        return False
    if BYLINE_PATTERN.search(text) and words < 15:
        return False
    if DATE_PATTERN.search(text) and words < 20:
        return False
    if _link_text_length(el) > len(text) * 0.7:
        return False
    if el.name == "div" and not el.select_one("p"):
        return False

    return True


def _walk_elements(root: Tag, start: Optional[Tag] = None):
    found_start = start is None
    stack = [root]
    while stack:
        node = stack.pop()
        if not isinstance(node, Tag):
            continue
        if not found_start:
            if node is start:
                found_start = True
            else:
                stack.extend(reversed(list(node.children)))
                continue
        yield node
        stack.extend(reversed(list(node.children)))


def find_content_boundary(element: Tag) -> Optional[Tag]:
    return find_content_start(element, "")


def find_content_start(main_content: Tag, title: str) -> Optional[Tag]:
    title_el = _find_title_element(main_content, title)
    start = title_el

    leaf_hit: Optional[Tag] = None
    container_hit: Optional[Tag] = None

    for el in _walk_elements(main_content, start):
        if _is_prose_block(el):
            if el.name in LEAF_CANDIDATE_TAGS:
                leaf_hit = el
                break
            if container_hit is None:
                container_hit = el

    if leaf_hit:
        return leaf_hit

    if container_hit:
        result = container_hit
        while True:
            qualifying_child: Optional[Tag] = None
            multiple = False
            for child in result.children:
                if not isinstance(child, Tag):
                    continue
                if _is_prose_block(child):
                    if qualifying_child is not None:
                        multiple = True
                        break
                    qualifying_child = child
            if qualifying_child and not multiple:
                result = qualifying_child
            else:
                break
        return result

    if start:
        return find_content_start(main_content, "")

    return None


def is_above_content_start(el: Tag, boundary: Optional[Tag]) -> bool:
    if boundary is None:
        return False
    if el is boundary:
        return False

    current = boundary.previous_element
    while current is not None:
        if current is el:
            return True
        current = current.previous_element

    return False
