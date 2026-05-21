from __future__ import annotations

import re
import time
from typing import List, Optional

import soupsieve as sv
from bs4 import Tag

from domdown.constants import (
    EXACT_SELECTORS_JOINED,
    FOOTNOTE_LIST_SELECTORS,
    HIDDEN_EXACT_SELECTOR,
    HIDDEN_EXACT_SKIP_SELECTOR,
    PARTIAL_SELECTORS,
    PARTIAL_SELECTORS_REGEX,
    TEST_ATTRIBUTES_SELECTOR,
)
from domdown.types import DebugRemoval
from domdown.utils import get_class_name, log_debug, text_preview
from domdown.utils.dom import closest, has_responsive_show_class


def remove_by_selector(
    doc: Tag,
    debug: bool,
    remove_exact: bool = True,
    remove_partial: bool = True,
    main_content: Optional[Tag] = None,
    debug_removals: Optional[List[DebugRemoval]] = None,
    skip_hidden_exact_selectors: bool = False,
) -> None:
    start_time = time.time()
    exact_selector_count = 0
    partial_selector_count = 0

    elements_to_remove: dict = {}

    if remove_exact:
        exact_elements = doc.select(EXACT_SELECTORS_JOINED)
        for el in exact_elements:
            if el.parent is None:
                continue
            if skip_hidden_exact_selectors:
                hidden_ancestor = closest(el, HIDDEN_EXACT_SKIP_SELECTOR)
                role = (el.get("role", "") or "").lower()
                if sv.match(HIDDEN_EXACT_SELECTOR, el) or (hidden_ancestor and role == "dialog"):
                    continue
            if closest(el, "pre, code"):
                continue
            if sv.match(HIDDEN_EXACT_SELECTOR, el) and has_responsive_show_class(get_class_name(el)):
                continue
            elements_to_remove[id(el)] = {"el": el, "type": "exact", "selector": None}
            exact_selector_count += 1

    if remove_partial:
        individual_regexes = None
        if debug:
            individual_regexes = [{"pattern": p, "regex": re.compile(p, re.IGNORECASE)} for p in PARTIAL_SELECTORS]

        doc_elements = doc.select(TEST_ATTRIBUTES_SELECTOR)
        main_elements = main_content.select(TEST_ATTRIBUTES_SELECTOR) if main_content else []
        all_elements_set = list(set(list(doc_elements) + list(main_elements)))

        for el in all_elements_set:
            if id(el) in elements_to_remove:
                continue

            if closest(el, "[data-domdown]"):
                continue

            tag = el.name.upper() if el.name else ""
            if tag in ("CODE", "PRE") or el.select_one("pre") or closest(el, "code, pre"):
                continue

            is_heading = bool(re.match(r"^H[1-6]$", tag))
            if is_heading:
                attrs_str = get_class_name(el)
            else:
                parts = [
                    get_class_name(el),
                    el.get("id", "") or "",
                    el.get("data-component", "") or "",
                    el.get("data-test", "") or "",
                    el.get("data-testid", "") or "",
                    el.get("data-test-id", "") or "",
                    el.get("data-qa", "") or "",
                    el.get("data-cy", "") or "",
                ]
                attrs_str = " ".join(parts)

            attrs_lower = attrs_str.lower()
            if not attrs_lower.strip():
                continue

            if PARTIAL_SELECTORS_REGEX.search(attrs_lower):
                matched_pattern = None
                if individual_regexes:
                    for r in individual_regexes:
                        if r["regex"].search(attrs_lower):
                            matched_pattern = r["pattern"]
                            break
                elements_to_remove[id(el)] = {"el": el, "type": "partial", "selector": matched_pattern}
                partial_selector_count += 1

    for entry in elements_to_remove.values():
        el = entry["el"]
        rtype = entry["type"]
        selector = entry["selector"]

        if main_content and _element_contains(el, main_content):
            continue

        if el.name == "a" and closest(el, "h1, h2, h3, h4, h5, h6"):
            continue

        try:
            if sv.match(FOOTNOTE_LIST_SELECTORS, el) or el.select_one(FOOTNOTE_LIST_SELECTORS):
                continue
            parent = el.parent
            if parent and isinstance(parent, Tag) and sv.match(FOOTNOTE_LIST_SELECTORS, parent):
                continue
            classes = el.get("class", [])
            if isinstance(classes, list) and "footnote-backref" in classes and closest(el, "#footnotes"):
                continue
        except Exception:
            pass

        if el.name == "button" and el.select_one("img, picture, video"):
            parent = el.parent
            if parent:
                for media in list(el.select("img, picture, video")):
                    el.insert_before(media)
                el.unwrap()
            continue

        if el.name == "button" and closest(el, "p, li, td, th, span, h1, h2, h3, h4, h5, h6"):
            _unwrap_element(el)
            continue

        if debug and debug_removals is not None:
            debug_removals.append(
                DebugRemoval(
                    step="removeBySelector",
                    selector="exact" if rtype == "exact" else selector,
                    reason="exact selector match" if rtype == "exact" else f"partial match: {selector}",
                    text=text_preview(el),
                )
            )
        el.decompose()

    end_time = time.time()
    log_debug(
        debug,
        "Removed clutter elements:",
        exact_selectors=exact_selector_count,
        partial_selectors=partial_selector_count,
        total=len(elements_to_remove),
        processing_time=f"{(end_time - start_time) * 1000:.2f}ms",
    )


def _element_contains(parent: Tag, child: Tag) -> bool:
    current = child.parent
    while current is not None:
        if current is parent:
            return True
        current = current.parent
    return False


def _unwrap_element(el: Tag) -> None:
    parent = el.parent
    if parent is None:
        return
    children = list(el.children)
    prev = el
    for child in children:
        child.extract()
        prev.insert_after(child)
        prev = child
    el.decompose()
