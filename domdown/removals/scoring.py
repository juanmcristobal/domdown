from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional

import soupsieve as sv
from bs4 import Tag

from domdown.constants import BLOCK_ELEMENTS_SELECTOR, FOOTNOTE_INLINE_REFERENCES, FOOTNOTE_LIST_SELECTORS
from domdown.types import DebugRemoval
from domdown.utils import count_words, get_class_name, log_debug, text_preview
from domdown.utils.dom import closest, contains

CONTENT_INDICATORS = [
    "admonition",
    "article",
    "content",
    "entry",
    "image",
    "img",
    "font",
    "figure",
    "figcaption",
    "pre",
    "main",
    "post",
    "story",
    "table",
]

NAVIGATION_INDICATORS = [
    "advertisement",
    "all rights reserved",
    "banner",
    "cookie",
    "comments",
    "copyright",
    "follow me",
    "follow us",
    "footer",
    "header",
    "homepage",
    "login",
    "menu",
    "more articles",
    "more like this",
    "most read",
    "nav",
    "navigation",
    "newsletter",
    "popular",
    "privacy",
    "recommended",
    "register",
    "related",
    "responses",
    "share",
    "sidebar",
    "sign in",
    "sign up",
    "signup",
    "social",
    "sponsored",
    "subscribe",
    "terms",
    "trending",
]

SOCIAL_PROFILE_PATTERN = re.compile(
    r"\b(linkedin\.com/(in|company)/|twitter\.com/(?!intent\b)\w|x\.com/(?!intent\b)\w"
    r"|facebook\.com/(?!share\b)\w|instagram\.com/\w|threads\.net/\w|mastodon\.\w)",
    re.IGNORECASE,
)

DATE_PATTERN = re.compile(
    r"(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}"
    r"|\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*)",
    re.IGNORECASE,
)

BYLINE_PATTERN = re.compile(r"\bBy\s+[A-Z]")

NAVIGATION_INDICATOR_REGEXES = [
    re.compile(r"\b" + re.sub(r"\s+", r"\\s+", indicator) + r"\b") for indicator in NAVIGATION_INDICATORS
]

NAVIGATION_HEADING_PATTERN = re.compile(
    "|".join(re.sub(r"\s+", r"\\s+", i) for i in NAVIGATION_INDICATORS),
    re.IGNORECASE,
)

TOC_HEADING_PATTERN = re.compile(
    r"^(?:table of )?contents$|^on this page$|^in this (?:article|guide|post)$",
    re.IGNORECASE,
)

CONTENT_DATE_PATTERN = re.compile(
    r"\b(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}"
    r"|\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*,?\s+\d{4})\b",
    re.IGNORECASE,
)

CONTENT_AUTHOR_PATTERN = re.compile(
    r"\b(?:by|written by|author:)\s+[A-Za-z\s]+\b",
    re.IGNORECASE,
)

NON_CONTENT_PATTERNS = [
    "advert",
    "ad-",
    "ads",
    "banner",
    "cookie",
    "copyright",
    "footer",
    "header",
    "homepage",
    "menu",
    "nav",
    "newsletter",
    "popular",
    "privacy",
    "recommended",
    "related",
    "rights",
    "share",
    "sidebar",
    "social",
    "sponsored",
    "subscribe",
    "terms",
    "trending",
    "widget",
]


@dataclass
class ContentScore:
    score: float
    element: Tag


class ContentScorer:
    @staticmethod
    def score_element(element: Tag) -> float:
        score = 0.0

        text = element.get_text() or ""
        words = count_words(text)
        score += words

        paragraphs = len(element.select("p"))
        score += paragraphs * 10

        commas = text.count(",")
        score += commas

        images = len(element.select("img"))
        image_density = images / (words or 1)
        score -= image_density * 3

        try:
            style = element.get("style", "") or ""
            align = element.get("align", "") or ""
            is_right_side = "float: right" in style or "text-align: right" in style or align == "right"
            if is_right_side:
                score += 5
        except Exception:
            pass

        has_date = CONTENT_DATE_PATTERN.search(text) is not None
        if has_date:
            score += 10

        has_author = CONTENT_AUTHOR_PATTERN.search(text) is not None
        if has_author:
            score += 10

        class_name = get_class_name(element).lower()
        if "content" in class_name or "article" in class_name or "post" in class_name:
            score += 15

        has_footnotes = element.select_one(FOOTNOTE_INLINE_REFERENCES)
        if has_footnotes:
            score += 10

        has_footnotes_list = element.select_one(FOOTNOTE_LIST_SELECTORS)
        if has_footnotes_list:
            score += 10

        nested_tables = len(element.select("table"))
        score -= nested_tables * 5

        if element.name == "td":
            parent_table = closest(element, "table")
            if parent_table:
                table_width = int(parent_table.get("width", "0") or "0")
                table_align = parent_table.get("align", "") or ""
                table_class = get_class_name(parent_table).lower()
                is_table_layout = (
                    table_width > 400 or table_align == "center" or "content" in table_class or "article" in table_class
                )

                if is_table_layout:
                    all_cells = parent_table.select("td")
                    try:
                        cell_index = all_cells.index(element)
                        is_center_cell = cell_index > 0 and cell_index < len(all_cells) - 1
                        if is_center_cell:
                            score += 10
                    except ValueError:
                        pass

        link_elements = element.select("a")
        link_text_length = sum(len(a.get_text() or "") for a in link_elements)
        text_length = len(text) or 1
        link_density = min(link_text_length / text_length, 0.5)
        score *= 1 - link_density

        return score

    @staticmethod
    def find_best_element(elements: list, min_score: float = 50) -> Optional[Tag]:
        best_element: Optional[Tag] = None
        best_score = 0.0

        for element in elements:
            score = ContentScorer.score_element(element)
            if score > best_score:
                best_score = score
                best_element = element

        return best_element if best_score > min_score else None

    @staticmethod
    def score_and_remove(
        doc: Tag,
        debug: bool = False,
        debug_removals: Optional[List[DebugRemoval]] = None,
        main_content: Optional[Tag] = None,
    ) -> None:
        import time

        start_time = time.time()

        elements_to_remove: Dict[Tag, float] = {}

        block_elements = doc.select(BLOCK_ELEMENTS_SELECTOR)

        for element in block_elements:
            if element in elements_to_remove:
                continue

            if main_content and contains(element, main_content):
                continue

            if closest(element, "pre"):
                continue

            if closest(element, "[data-domdown]"):
                continue

            if ContentScorer._is_likely_content(element):
                continue

            score = ContentScorer._score_non_content_block(element)

            if score < 0:
                elements_to_remove[element] = score

        for el, score in elements_to_remove.items():
            if debug and debug_removals is not None:
                debug_removals.append(
                    DebugRemoval(
                        step="scoreAndRemove",
                        reason=f"score: {score}",
                        text=text_preview(el),
                    )
                )
            el.decompose()

        end_time = time.time()
        log_debug(
            debug,
            "Removed non-content blocks:",
            count=len(elements_to_remove),
            processing_time=f"{(end_time - start_time) * 1000:.2f}ms",
        )

    @staticmethod
    def _is_likely_content(element: Tag) -> bool:
        role = element.get("role")
        if role and role in ("article", "main", "contentinfo"):
            return True

        class_name = get_class_name(element).lower()
        el_id = (element.get("id") or "").lower()

        for indicator in CONTENT_INDICATORS:
            if indicator in class_name or indicator in el_id:
                return True

        if element.select_one("pre, table, figure, picture"):
            return True

        text = element.get_text() or ""
        words = count_words(text)

        heading_child = element.select_one("h1, h2, h3, h4, h5, h6")
        if heading_child:
            heading_text = (heading_child.get_text() or "").strip()
            if heading_text and heading_text == text.strip():
                heading_lower = heading_text.lower()
                if not NAVIGATION_HEADING_PATTERN.search(heading_lower) and not TOC_HEADING_PATTERN.search(
                    heading_lower
                ):
                    return True

        if words < 1000:
            headings = element.select("h1, h2, h3, h4, h5, h6")
            has_navigation_heading = False
            for h in headings:
                heading_text = (h.get_text() or "").lower().strip()
                if NAVIGATION_HEADING_PATTERN.search(heading_text):
                    has_navigation_heading = True
                    break

            if has_navigation_heading:
                if words < 200:
                    return False
                link_count = len(element.select("a"))
                link_density = link_count / (words or 1)
                if link_density > 0.2:
                    return False

        if ContentScorer._is_card_grid(element, words):
            return False

        if words < 80:
            links = element.select("a")
            for link in links:
                href = (link.get("href", "") or "").lower()
                if SOCIAL_PROFILE_PATTERN.search(href):
                    return False

        paragraphs = len(element.select("p"))
        list_items = len(element.select("li"))
        content_blocks = paragraphs + list_items

        if words > 50 and content_blocks > 1:
            return True

        if words > 100:
            return True

        if words > 30 and content_blocks > 0:
            return True

        if words >= 10 and re.search(r"[.?!]", text):
            link_count = len(element.select("a"))
            link_density = link_count / words
            if link_density < 0.1:
                return True

        return False

    @staticmethod
    def _score_non_content_block(element: Tag) -> float:
        try:
            if (
                sv.match(FOOTNOTE_LIST_SELECTORS, element)
                or element.select_one(FOOTNOTE_LIST_SELECTORS)
                or closest(element, FOOTNOTE_LIST_SELECTORS)
            ):
                return 0
        except Exception:
            pass

        score = 0.0

        text = element.get_text() or ""
        words = count_words(text)

        if words < 3:
            return 0

        commas = text.count(",")
        score += commas

        text_lower = text.lower()
        indicator_matches = 0
        for regex in NAVIGATION_INDICATOR_REGEXES:
            if regex.search(text_lower):
                indicator_matches += 1
        score -= indicator_matches * 10

        link_elements = element.select("a")
        links = len(link_elements)
        link_density = links / (words or 1)
        if link_density > 0.5:
            score -= 15

        if links > 1 and words < 80:
            link_text_length = sum(len(a.get_text() or "") for a in link_elements)
            total_text_length = len(text)
            if total_text_length > 0 and link_text_length / total_text_length > 0.8:
                score -= 15

        lists = len(element.select("ul")) + len(element.select("ol"))
        if lists > 0 and links > lists * 3:
            score -= 10

        if words < 80:
            el_links = element.select("a")
            for a in el_links:
                href = (a.get("href", "") or "").lower()
                if SOCIAL_PROFILE_PATTERN.search(href):
                    score -= 15
                    break

        if words < 15:
            if BYLINE_PATTERN.search(text) and DATE_PATTERN.search(text):
                score -= 10

        if ContentScorer._is_card_grid(element, words):
            score -= 15

        class_name = get_class_name(element).lower()
        el_id = (element.get("id") or "").lower()

        for pattern in NON_CONTENT_PATTERNS:
            if pattern in class_name or pattern in el_id:
                score -= 8

        return score

    @staticmethod
    def _is_card_grid(element: Tag, words: int) -> bool:
        if words < 3 or words >= 500:
            return False
        headings = element.select("h2, h3, h4")
        if len(headings) < 3:
            return False
        images = element.select("img")
        if len(images) < 2:
            return False
        heading_word_count = sum(count_words(h.get_text() or "") for h in headings)
        prose_per_heading = (words - heading_word_count) / len(headings)
        return prose_per_heading < 20
