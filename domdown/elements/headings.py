from __future__ import annotations

import re
from typing import List

from bs4 import Tag

from domdown.constants import ALLOWED_ATTRIBUTES

_PERMALINK_SYMBOL_RE = re.compile(r"^[#¶§🔗\uFEFF]$")


def remove_permalink_anchors(element: Tag) -> None:
    for link in element.select("h1 a, h2 a, h3 a, h4 a, h5 a, h6 a, a.permalink, a.anchor-link, a.heading-anchor"):
        if is_permalink_anchor(link):
            link.decompose()


def is_permalink_anchor(node: Tag) -> bool:
    if node.name != "a":
        return False
    href = node.get("href", "") or ""
    title = (node.get("title", "") or "").lower()
    class_name = node.get("class", [])
    if isinstance(class_name, list):
        class_str = " ".join(class_name).lower()
    else:
        class_str = str(class_name).lower()
    text = node.get_text().strip()
    if href.startswith("#"):
        return True
    if "permalink" in title:
        return True
    if "permalink" in class_str or "heading-anchor" in class_str or "anchor-link" in class_str:
        return True
    if _PERMALINK_SYMBOL_RE.match(text):
        return True
    return False


def is_heading_nav_element(node: Tag) -> bool:
    tag = node.name
    if tag == "button":
        return True
    if tag == "a" and is_permalink_anchor(node):
        return True
    class_name = node.get("class", [])
    if isinstance(class_name, list):
        class_str = " ".join(class_name)
    else:
        class_str = str(class_name)
    if "anchor" in class_str or "permalink-widget" in class_str:
        return True
    if tag in ("span", "div"):
        for a in node.select("a"):
            if is_permalink_anchor(a):
                return True
    return False


def _transform_heading(el: Tag, doc: Tag) -> Tag:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup("", "lxml")
    new_heading = soup.new_tag(el.name)
    for attr_name, attr_val in el.attrs.items():
        if attr_name in ALLOWED_ATTRIBUTES:
            new_heading[attr_name] = attr_val

    element_children = [c for c in el.children if isinstance(c, Tag)]
    if not element_children:
        new_heading.string = el.get_text().strip() or ""
        return new_heading

    clone_soup = BeautifulSoup(str(el), "lxml")
    clone = clone_soup.body if clone_soup.body else clone_soup

    navigation_text = {}
    to_remove = []

    for child in clone.find_all(True):
        if not is_heading_nav_element(child):
            continue
        nav_key = id(child)
        navigation_text[nav_key] = child.get_text().strip() or ""
        parent = child.parent
        if parent is not None and parent is not clone and isinstance(parent, Tag):
            parent_text = parent.get_text().strip()
            child_text = child.get_text().strip()
            if parent_text == child_text:
                navigation_text[id(parent)] = child_text
        to_remove.append(child)

    for elem in to_remove:
        if elem.parent is not None:
            elem.decompose()

    text_content = clone.get_text().strip() or ""

    if not text_content and navigation_text:
        first_val = next(iter(navigation_text.values()), "")
        text_content = first_val

    new_heading.string = text_content or ""
    return new_heading


heading_rules: List[dict] = [
    {
        "selector": "h1, h2, h3, h4, h5, h6",
        "element": "keep",
        "transform": _transform_heading,
    }
]
