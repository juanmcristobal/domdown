from __future__ import annotations

import re
from typing import List, Optional
from urllib.parse import urlparse

from bs4 import Tag

from domdown.constants import CONTENT_ELEMENT_SELECTOR
from domdown.types import DebugRemoval
from domdown.utils import count_words, normalize_text, text_preview
from domdown.utils.dom import closest

CONTENT_DATE_PATTERN = re.compile(
    r"(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}"
    r"|\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*"
    r"|\d{4}[-/]\d{1,2}[-/]\d{1,2})",
    re.IGNORECASE,
)
RELATIVE_TIME_PATTERN = re.compile(
    r"\b\d+\s+(?:second|minute|hour|day|week|month|year)s?\s+ago\b",
    re.IGNORECASE,
)
CONTENT_READ_TIME_PATTERN = re.compile(
    r"\d+\s*min(?:ute)?s?\s+read\b|(?:read(?:ing)?\s+time)\s*:?\s*\d+\s*min(?:ute)?s?\b",
    re.IGNORECASE,
)
BYLINE_UPPERCASE_PATTERN = re.compile(r"^[A-Z]")
STARTS_WITH_BY_PATTERN = re.compile(r"^(?:posted\s+)?by\s+\S", re.IGNORECASE)

BOILERPLATE_PATTERNS = [
    re.compile(r"^This (?:article|story|piece) (?:appeared|was published|originally appeared) in\b", re.IGNORECASE),
    re.compile(r"^A version of this (?:article|story) (?:appeared|was published) in\b", re.IGNORECASE),
    re.compile(r"^Originally (?:published|appeared) (?:in|on|at)\b", re.IGNORECASE),
    re.compile(r"^Any re-?use permitted\b", re.IGNORECASE),
    re.compile(r"^©\s*(?:Copyright\s+)?\d{4}", re.IGNORECASE),
    re.compile(r"^Comments?$", re.IGNORECASE),
    re.compile(r"^Leave a (?:comment|reply)$", re.IGNORECASE),
    re.compile(r"^Loading\.{3}$"),
    re.compile(r"^Affiliate links\b.*\b(?:earn|commission)", re.IGNORECASE),
    re.compile(r"\bRead our Comment Policy\b", re.IGNORECASE),
    re.compile(r"^Thank you for (?:being part of|joining) our community\b", re.IGNORECASE),
]

NEWSLETTER_PATTERN = re.compile(
    r"\bsubscribe\b[\s\S]{0,40}\bnewsletter\b|\bnewsletter\b[\s\S]{0,40}\bsubscribe\b"
    r"|\bsign[- ]up\b[\s\S]{0,80}\b(?:newsletter|email alert)"
    r"|\b(?:don[\u2019\']?t (?:want to )?miss|never miss)\b[\s\S]{0,80}\b(?:latest|best|exclusive|reports?|updates?|source)",
    re.IGNORECASE,
)
SOCIAL_COUNTER_PATTERN = re.compile(
    r"^\d+\s+(?:Likes?|Comments?|Shares?|Retweets?|Reposts?|Restacks?)$",
    re.IGNORECASE,
)
TIMEZONE_WIDGET_PATTERN = re.compile(r"^current time in$", re.IGNORECASE)
PINNED_LABEL_PATTERN = re.compile(r"^pinned$", re.IGNORECASE)
AUTHOR_CONTACT_LABEL_PATTERN = re.compile(
    r"^(?:written by|(?:author|contact|reporter|correspondent)s?)$",
    re.IGNORECASE,
)
SHARE_AUTHOR_LABEL = re.compile(
    r"^(?:share|follow|authors?|written\s+by)$",
    re.IGNORECASE,
)

CONTENT_ELEMENT_NO_IMG_SELECTOR = CONTENT_ELEMENT_SELECTOR.replace("img, picture, ", "")

EMAIL_PATTERN = re.compile(r"[\w.-]+@[\w.-]+\.\w+")
PHONE_PATTERN = re.compile(r"\(?\d{3}\)?[\s.\u2011\u2013\-]?\d{3}[\s.\u2011\u2013\-]?\d{4}")

HEADING_TAG_PATTERN = re.compile(r"^H[1-6]$")
HEADING_SELECTOR = "h1, h2, h3, h4, h5, h6"

METADATA_STRIP_BASE = [
    re.compile(
        r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\b",
        re.IGNORECASE,
    ),
    re.compile(r"\b\d+(?:st|nd|rd|th)?\b"),
    re.compile(r"\d{4}[-/]\d{1,2}[-/]\d{1,2}"),
]

READ_TIME_STRIP_PATTERNS = METADATA_STRIP_BASE + [
    re.compile(r"\bmin(?:ute)?s?\b", re.IGNORECASE),
    re.compile(r"\bread(?:ing)?\b", re.IGNORECASE),
    re.compile(r"\btime\b", re.IGNORECASE),
    re.compile(r"\bestimated\b", re.IGNORECASE),
    re.compile(r"[/|·•—–\-,:.\s]+"),
]

BYLINE_STRIP_PATTERNS = METADATA_STRIP_BASE + [
    re.compile(r"\bby\b", re.IGNORECASE),
    re.compile(r"[/|·•—–\-,]+"),
]

RELATED_HEADING_PATTERN = re.compile(
    r"^(?:related (?:posts?|articles?|content|stories|reads?|reading)"
    r"|you (?:might|may|could) (?:also )?(?:like|enjoy|be interested in)"
    r"|read (?:next|more|also)|further reading|see also"
    r"|more (?:from .*|from|articles?|posts?|like this)"
    r"|more to (?:read|explore)|explore more"
    r"|about (?:the )?author"
    r"|latest (?:news|events?|posts?|articles?|stories)(?:\s*[&+]\s*(?:news|events?|posts?|articles?|stories))?)$",
    re.IGNORECASE,
)

CTA_HEADING_PATTERN = re.compile(
    r"^(?:subscribe|sign up|follow us|share this|stay (?:updated|connected)"
    r"|join (?:us|our)|search (?:the |our )?(?:site|blog|archives?|newsroom|website|catalog|store|shop|database))$",
    re.IGNORECASE,
)

RELATED_INTRO_PATTERN = re.compile(r"^for more (?:on|about)\b", re.IGNORECASE)


def _is_or_contains_heading(el: Tag) -> bool:
    return bool(HEADING_TAG_PATTERN.match(el.name.upper())) or bool(el.select_one(HEADING_SELECTOR))


def _is_newsletter_element(el: Tag, max_words: int) -> bool:
    text = (el.get_text() or "").strip()
    words = count_words(text)
    if words < 2 or words > max_words:
        return False
    if el.select_one(CONTENT_ELEMENT_SELECTOR):
        return False
    normalized_text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text).replace("\u2018", "'").replace("\u2019", "'")
    return bool(NEWSLETTER_PATTERN.search(normalized_text))


def _walk_up_to_wrapper(el: Tag, text: str, main_content: Tag) -> Tag:
    target = el
    while target.parent is not None and target.parent is not main_content:
        parent_text = (target.parent.get_text() or "").strip()
        if parent_text != text:
            break
        target = target.parent
    return target


def _remove_trailing_siblings(
    element: Tag,
    remove_self: bool,
    debug: bool,
    debug_removals: Optional[List[DebugRemoval]] = None,
) -> None:
    sibling = element.next_sibling
    while sibling is not None:
        next_sib = sibling.next_sibling
        if isinstance(sibling, Tag):
            if sibling.get("id") == "footnotes":
                sibling = next_sib
                continue
            if debug and debug_removals is not None:
                debug_removals.append(
                    DebugRemoval(
                        step="removeByContentPattern",
                        reason="trailing non-content",
                        text=text_preview(sibling),
                    )
                )
            sibling.decompose()
        sibling = next_sib

    if remove_self:
        if debug and debug_removals is not None:
            debug_removals.append(
                DebugRemoval(
                    step="removeByContentPattern",
                    reason="boilerplate text",
                    text=text_preview(element),
                )
            )
        element.decompose()


def _remove_trailing_with_cascade(
    target: Tag,
    main_content: Tag,
    debug: bool,
    debug_removals: Optional[List[DebugRemoval]] = None,
) -> None:
    ancestors: list = []
    anc = target.parent
    while anc is not None and anc is not main_content:
        ancestors.append(anc)
        anc = anc.parent

    _remove_trailing_siblings(target, True, debug, debug_removals)
    for ancestor in ancestors:
        _remove_trailing_siblings(ancestor, False, debug, debug_removals)


def _walk_up_isolated(el: Tag, main_content: Tag) -> Tag:
    target = el
    while target.parent is not None and target.parent is not main_content:
        preceding_words = 0
        sib = target.previous_sibling
        while sib is not None:
            if isinstance(sib, Tag):
                preceding_words += count_words(sib.get_text() or "")
                if preceding_words > 10:
                    break
            sib = sib.previous_sibling
        if preceding_words > 10:
            break
        target = target.parent
    return target


def _remove_thin_preceding_section(
    target: Tag,
    debug: bool,
    debug_removals: Optional[List[DebugRemoval]] = None,
) -> None:
    prev_sib = _prev_element_sibling(target)
    if not prev_sib:
        return
    if count_words(prev_sib.get_text() or "") >= 50:
        return
    if prev_sib.select_one(CONTENT_ELEMENT_SELECTOR):
        return

    before_prev = _prev_element_sibling(prev_sib)
    if before_prev and _is_or_contains_heading(before_prev):
        return

    if debug and debug_removals is not None:
        debug_removals.append(
            DebugRemoval(
                step="removeByContentPattern",
                reason="thin CTA section",
                text=text_preview(prev_sib),
            )
        )
    prev_sib.decompose()


def _prev_element_sibling(el: Tag) -> Optional[Tag]:
    sib = el.previous_sibling
    while sib is not None:
        if isinstance(sib, Tag):
            return sib
        sib = sib.previous_sibling
    return None


def _next_element_sibling(el) -> Optional[Tag]:
    sib = el.next_sibling
    while sib is not None:
        if isinstance(sib, Tag):
            return sib
        sib = sib.next_sibling
    return None


def _is_breadcrumb_list(list_el: Tag) -> bool:
    list_items = list_el.select("li")
    if len(list_items) < 2 or len(list_items) > 8:
        return False

    list_links = list(list_el.select("a"))
    if len(list_links) < 1 or len(list_links) >= len(list_items):
        return False
    if list_el.select_one("img, p, figure, blockquote"):
        return False

    for item in list_items:
        if count_words(item.get_text() or "") > 8:
            return False

    all_internal = True
    has_breadcrumb_link = False
    short_link_texts = True
    for a in list_links:
        href = a.get("href", "") or ""
        if href.startswith("http") or href.startswith("//"):
            all_internal = False
            break
        if href == "/" or re.match(r"^/[a-zA-Z0-9_-]+/?$", href):
            has_breadcrumb_link = True
        a_text = (a.get_text() or "").strip().split()
        a_words = [w for w in a_text if w]
        if len(a_words) > 5:
            short_link_texts = False

    return all_internal and has_breadcrumb_link and short_link_texts


def _compare_document_position(el1: Tag, el2: Tag) -> int:
    soup = el1.find_parent("[document]") or el2.find_parent("[document]")
    if soup is None:
        return 0

    all_tags = list(soup.descendants)
    pos1 = pos2 = -1
    for i, node in enumerate(all_tags):
        if node is el1:
            pos1 = i
        if node is el2:
            pos2 = i

    if pos1 < 0 or pos2 < 0:
        return 1
    if pos1 < pos2:
        return 4
    return 0


def _remove_hero_header(
    main_content: Tag,
    content_start: Optional[Tag],
    debug: bool,
    debug_removals: Optional[List[DebugRemoval]] = None,
) -> None:
    try:
        from ..content_boundary import is_above_content_start
    except ImportError:
        return

    time_elements = main_content.select("time")
    if not time_elements:
        return

    for time_el in time_elements:
        if not is_above_content_start(time_el, content_start):
            continue

        best_block = None
        current = time_el.parent

        while current is not None and current is not main_content:
            has_heading_and_time = current.select_one("h1, h2") is not None and current.select_one("time") is not None
            if has_heading_and_time:
                block_text = (current.get_text() or "").strip()
                total_words = count_words(block_text)

                metadata_els: set = set()
                for el in current.select("h1, h2, h3, time, [aria-label]"):
                    dominated = False
                    for existing in metadata_els:
                        if _element_contains(existing, el):
                            dominated = True
                            break
                    if not dominated:
                        metadata_els.add(el)

                metadata_words = sum(count_words(el.get_text() or "") for el in metadata_els)
                prose_words = total_words - metadata_words

                if prose_words < 30:
                    best_block = current
                else:
                    break

            current = current.parent

        if best_block:
            if debug and debug_removals is not None:
                debug_removals.append(
                    DebugRemoval(
                        step="removeByContentPattern",
                        reason="hero header block",
                        text=text_preview(best_block),
                    )
                )
            best_block.decompose()
            return


def _element_contains(parent: Tag, child: Tag) -> bool:
    current = child.parent
    while current is not None:
        if current is parent:
            return True
        current = current.parent
    return False


def remove_eyebrow_label(
    main_content: Tag,
    debug: bool,
    debug_removals: Optional[List[DebugRemoval]] = None,
) -> None:
    first_heading = main_content.select_one("h1") or main_content.select_one("h2")
    if not first_heading:
        return

    current = first_heading
    while current.parent is not None and current.parent is not main_content and _prev_element_sibling(current) is None:
        current = current.parent

    prev = _prev_element_sibling(current)
    if not prev:
        return

    text = (prev.get_text() or "").strip()
    words = count_words(text)
    if words < 1 or words > 6:
        return
    if len(text) > 40:
        return
    if re.search(r"[.!?]", text):
        return
    if CONTENT_DATE_PATTERN.search(text):
        return
    if prev.select_one(
        "img, picture, video, iframe, figure, table, pre, code, time, [datetime], "
        "h1, h2, h3, h4, h5, h6, ul, ol, blockquote"
    ):
        return

    if debug and debug_removals is not None:
        debug_removals.append(
            DebugRemoval(
                step="removeEyebrowLabel",
                reason="eyebrow label",
                text=text_preview(prev),
            )
        )
    prev.decompose()


def remove_by_content_pattern(
    main_content: Tag,
    debug: bool,
    url: str,
    title: str,
    description: str,
    debug_removals: Optional[List[DebugRemoval]] = None,
) -> None:
    try:
        from ..content_boundary import find_content_start, is_above_content_start
    except ImportError:
        find_content_start = None
        is_above_content_start = None

    content_start = find_content_start(main_content, title) if find_content_start else None

    def is_pre_content(el: Tag) -> bool:
        if is_above_content_start is None:
            return False
        return is_above_content_start(el, content_start)

    normalized_title = normalize_text(title)
    normalized_desc = normalize_text(description)

    first_list = main_content.select_one("ul, ol")
    if first_list and _is_breadcrumb_list(first_list):
        target = first_list
        while (
            target.parent is not None and target.parent is not main_content and len(list(target.parent.children)) == 1
        ):
            target = target.parent
        if debug and debug_removals is not None:
            debug_removals.append(
                DebugRemoval(
                    step="removeByContentPattern",
                    reason="breadcrumb navigation list",
                    text=text_preview(target),
                )
            )
        target.decompose()

    first_h1 = main_content.select_one("h1")
    if first_h1:
        for link in main_content.select("a[href]"):
            if link.parent is None:
                continue
            if not (_compare_document_position(link, first_h1) & 4):
                continue
            if not link.select_one("div"):
                continue
            if link.select_one("img, picture, video"):
                continue
            text = (link.get_text() or "").strip()
            if count_words(text) > 25:
                continue
            if re.search(r"[.!?]\s", text):
                continue
            if debug and debug_removals is not None:
                debug_removals.append(
                    DebugRemoval(
                        step="removeByContentPattern",
                        reason="promotional banner link",
                        text=text_preview(link),
                    )
                )
            link.decompose()

    _remove_hero_header(main_content, content_start, debug, debug_removals)

    for media in main_content.select("audio, video"):
        if media.parent is None:
            continue
        if not media.get("src") and not media.select_one("source"):
            continue

        container = media
        while container.parent is not None and container.parent is not main_content:
            if count_words((container.parent.get_text() or "").strip()) > 25:
                break
            container = container.parent

        container_text = (container.get_text() or "").strip()
        is_listen_widget = bool(
            re.search(
                r"\blisten\s+to\s+(?:this\s+)?(?:article|story|post|episode|podcast)\b",
                container_text,
                re.IGNORECASE,
            )
        )
        is_pre_content_player = not is_listen_widget and is_pre_content(container) and count_words(container_text) <= 25

        if is_listen_widget or is_pre_content_player:
            if debug and debug_removals is not None:
                debug_removals.append(
                    DebugRemoval(
                        step="removeByContentPattern",
                        reason="audio player widget",
                        text=text_preview(container),
                    )
                )
            container.decompose()

    content_text = main_content.get_text() or ""

    parsed_page_url = None
    try:
        parsed_page_url = urlparse(url)
    except Exception:
        pass

    for list_el in main_content.select("ul, ol"):
        if list_el.parent is None:
            continue
        if closest(list_el, "#footnotes"):
            continue

        list_text = (list_el.get_text() or "").strip()
        list_pos = content_text.find(list_text[:60])
        if list_pos < 0 or list_pos > len(content_text) * 0.3:
            continue

        links = list(list_el.select("a[href]"))
        if len(links) < 3:
            continue

        if list_el.select_one(CONTENT_ELEMENT_SELECTOR):
            continue

        anchor_count = 0
        for link in links:
            href = link.get("href", "") or ""
            if href.startswith("#"):
                anchor_count += 1
            elif parsed_page_url and "#" in href:
                try:
                    from urllib.parse import urljoin

                    resolved = urlparse(urljoin(url, href))
                    if resolved.path == parsed_page_url.path and resolved.hostname == parsed_page_url.hostname:
                        anchor_count += 1
                except Exception:
                    pass

        if anchor_count < 3 or anchor_count / len(links) < 0.8:
            continue

        target = list_el
        while (
            target.parent is not None and target.parent is not main_content and len(list(target.parent.children)) == 1
        ):
            target = target.parent

        prev_el = _prev_element_sibling(target)
        if prev_el and HEADING_TAG_PATTERN.match(prev_el.name.upper()):
            h_text = (prev_el.get_text() or "").strip()
            if re.match(
                r"^(?:table of )?contents$|^on this page$|^in this (?:article|guide|post)$",
                h_text,
                re.IGNORECASE,
            ):
                if debug and debug_removals is not None:
                    debug_removals.append(
                        DebugRemoval(
                            step="removeByContentPattern",
                            reason="table of contents heading",
                            text=text_preview(prev_el),
                        )
                    )
                prev_el.decompose()

        prev_sib = _prev_element_sibling(target)
        next_sib = _next_element_sibling(target)

        if debug and debug_removals is not None:
            debug_removals.append(
                DebugRemoval(
                    step="removeByContentPattern",
                    reason="table of contents",
                    text=text_preview(target),
                )
            )
        target.decompose()

        if prev_sib and prev_sib.name == "hr":
            prev_sib.decompose()
        if next_sib and next_sib.name == "hr":
            next_sib.decompose()
        break

    candidates = main_content.select("p, span, div, time")

    byline_found = False
    author_date_found = False

    for el in candidates:
        if el.parent is None:
            continue

        text = (el.get_text() or "").strip()
        words = count_words(text)

        if words > 15 or words == 0:
            continue

        if closest(el, "pre, code"):
            continue

        tag = el.name.upper()
        has_date = bool(CONTENT_DATE_PATTERN.search(text))

        pos = -2

        def get_pos():
            nonlocal pos
            if pos == -2:
                pos = content_text.find(text)
            return pos

        if TIMEZONE_WIDGET_PATTERN.search(text) and get_pos() <= 300:
            target = el
            if target.parent is not None and target.parent is not main_content:
                target = target.parent
            if debug and debug_removals is not None:
                debug_removals.append(
                    DebugRemoval(
                        step="removeByContentPattern",
                        reason="timezone widget",
                        text=text_preview(target),
                    )
                )
            target.decompose()
            continue

        if words == 1 and PINNED_LABEL_PATTERN.search(text):
            if debug and debug_removals is not None:
                debug_removals.append(
                    DebugRemoval(
                        step="removeByContentPattern",
                        reason="pinned label",
                        text=text_preview(el),
                    )
                )
            el.decompose()
            continue

        removed = False
        for normalized, reason in [
            (normalized_title, "duplicate title"),
            (normalized_desc, "duplicate description"),
        ]:
            if normalized and words >= 3 and is_pre_content(el) and normalize_text(text) == normalized:
                if debug and debug_removals is not None:
                    debug_removals.append(
                        DebugRemoval(
                            step="removeByContentPattern",
                            reason=reason,
                            text=text_preview(el),
                        )
                    )
                el.decompose()
                removed = True
                break
        if removed:
            continue

        if el.parent is None:
            continue

        if (
            tag in ("DIV", "P")
            and 1 <= words <= 10
            and (has_date or RELATIVE_TIME_PATTERN.search(text))
            and not re.search(r"[.!?]", text)
            and is_pre_content(el)
        ):
            block_children = el.select("p, h1, h2, h3, h4, h5, h6")
            if not any(count_words(b.get_text() or "") > 8 for b in block_children):
                if debug and debug_removals is not None:
                    debug_removals.append(
                        DebugRemoval(
                            step="removeByContentPattern",
                            reason="article metadata header block",
                            text=text_preview(el),
                        )
                    )
                el.decompose()
                continue

        if (
            tag == "DIV"
            and 1 <= words <= 5
            and not re.search(r"[.!?]", text)
            and is_pre_content(el)
            and el.select_one("img")
        ):
            links = el.select("a[href]")
            if links:
                link_text_len = sum(len((a.get_text() or "").strip()) for a in links)
                if link_text_len / (len(text) or 1) >= 0.8:
                    if debug and debug_removals is not None:
                        debug_removals.append(
                            DebugRemoval(
                                step="removeByContentPattern",
                                reason="category badge",
                                text=text_preview(el),
                            )
                        )
                    el.decompose()
                    continue

        if (
            not byline_found
            and STARTS_WITH_BY_PATTERN.search(text)
            and words >= 2
            and not re.search(r"[.!?]$", text)
            and is_pre_content(el)
        ):
            target = _walk_up_to_wrapper(el, text, main_content)
            if debug and debug_removals is not None:
                debug_removals.append(
                    DebugRemoval(
                        step="removeByContentPattern",
                        reason="author byline",
                        text=text_preview(target),
                    )
                )
            target.decompose()
            byline_found = True
            continue

        if CONTENT_READ_TIME_PATTERN.search(text) and (
            has_date
            and len(el.select("p, div, section, article")) == 0
            or (not has_date and words <= 5 and is_pre_content(el))
        ):
            cleaned = text
            for pattern in READ_TIME_STRIP_PATTERNS:
                cleaned = pattern.sub("", cleaned)
            if cleaned.strip():
                continue
            target = el if has_date else _walk_up_to_wrapper(el, text, main_content)
            if debug and debug_removals is not None:
                debug_removals.append(
                    DebugRemoval(
                        step="removeByContentPattern",
                        reason="read time metadata",
                        text=text_preview(target),
                    )
                )
            target.decompose()
            continue

        if not author_date_found and 2 <= words <= 10 and has_date and is_pre_content(el):
            residual = text
            for pattern in BYLINE_STRIP_PATTERNS:
                residual = pattern.sub("", residual)
            residual = residual.strip()
            if residual:
                name_words = [w for w in residual.split() if w]
                if 1 <= len(name_words) <= 4 and all(BYLINE_UPPERCASE_PATTERN.match(w) for w in name_words):
                    target = _walk_up_to_wrapper(el, text, main_content)
                    if debug and debug_removals is not None:
                        debug_removals.append(
                            DebugRemoval(
                                step="removeByContentPattern",
                                reason="author date metadata",
                                text=text_preview(target),
                            )
                        )
                    target.decompose()
                    author_date_found = True
                    continue

        if has_date and words <= 5 and is_pre_content(el):
            residual = text
            for pattern in METADATA_STRIP_BASE:
                residual = pattern.sub("", residual)
            residual = re.sub(r"[,\s/\-]+", "", residual).strip()
            if len(residual) == 0:
                target = _walk_up_to_wrapper(el, text, main_content)
                if debug and debug_removals is not None:
                    debug_removals.append(
                        DebugRemoval(
                            step="removeByContentPattern",
                            reason="standalone date metadata",
                            text=text_preview(target),
                        )
                    )
                target.decompose()
                continue

    time_elements = main_content.select("time")
    for time_el in time_elements:
        if time_el.parent is None:
            continue

        target = time_el
        target_text = (target.get_text() or "").strip()
        while target.parent is not None and target.parent is not main_content:
            parent_tag = target.parent.name.lower() if isinstance(target.parent, Tag) else ""
            parent_text = (target.parent.get_text() or "").strip()
            if parent_tag == "p" and parent_text == target_text:
                target = target.parent
                break
            if parent_tag in ("i", "em", "span", "b", "strong", "small") and parent_text == target_text:
                target = target.parent
                target_text = parent_text
                continue
            break

        text = (target.get_text() or "").strip()
        words = count_words(text)
        if words > 10:
            continue

        pos = content_text.find(text)
        dist_from_end = len(content_text) - (pos + len(text))
        if pos > 200 and dist_from_end > 200:
            continue

        if debug and debug_removals is not None:
            debug_removals.append(
                DebugRemoval(
                    step="removeByContentPattern",
                    reason="boundary date element",
                    text=text_preview(target),
                )
            )
        target.decompose()

    metadata_lists = main_content.select("ul, ol, dl")
    for list_el in metadata_lists:
        if list_el.parent is None:
            continue
        if closest(list_el, "#footnotes"):
            continue

        is_dl = list_el.name == "dl"
        items = [
            el for el in list_el.children if isinstance(el, Tag) and (el.name == "dd" if is_dl else el.name == "li")
        ]
        min_items = 1 if is_dl else 2
        if len(items) < min_items or len(items) > 8:
            continue

        list_text = (list_el.get_text() or "").strip()
        list_pos = content_text.find(list_text)
        dist_from_end = len(content_text) - (list_pos + len(list_text))
        if list_pos > 500 and dist_from_end > 500:
            continue

        prev_sibling = _prev_element_sibling(list_el)
        if prev_sibling:
            if _is_or_contains_heading(prev_sibling):
                continue
            prev_text = (prev_sibling.get_text() or "").strip()
            if prev_text.endswith(":"):
                continue

        is_metadata = True
        for item in items:
            item_text = (item.get_text() or "").strip()
            item_words = count_words(item_text)
            if item_words > 8:
                is_metadata = False
                break
            if re.search(r"[.!?]$", item_text):
                is_metadata = False
                break
        if not is_metadata:
            continue

        if count_words(list_text) > 30:
            continue

        target = _walk_up_to_wrapper(list_el, list_text, main_content)

        if debug and debug_removals is not None:
            debug_removals.append(
                DebugRemoval(
                    step="removeByContentPattern",
                    reason="blog metadata list",
                    text=text_preview(target),
                )
            )
        target.decompose()

    url_path = parsed_page_url.path if parsed_page_url else ""
    page_host = parsed_page_url.hostname.replace("www.", "") if parsed_page_url and parsed_page_url.hostname else ""

    if url_path:
        short_elements = main_content.select("div, span, p, a[href]")
        first_heading = main_content.select_one("h1, h2, h3")
        for el in short_elements:
            if el.parent is None:
                continue
            text = (el.get_text() or "").strip()
            words = count_words(text)
            if words > 10:
                continue
            if el.select("p, div, section, article"):
                continue

            import soupsieve as sv

            if sv.match("a[href]", el) and el.parent is not None and el.parent is not main_content:
                parent_text = (el.parent.get_text() or "").strip()
                if parent_text != text:
                    if closest(el, "p"):
                        continue
                    if not first_heading:
                        continue
                    if not (_compare_document_position(el, first_heading) & 4):
                        continue

            link = el if sv.match("a[href]", el) else el.select_one("a[href]")
            if not link:
                continue
            try:
                from urllib.parse import urljoin

                link_path = urlparse(urljoin(url, link.get("href", "") or "")).path
                link_dir = re.sub(r"/[^/]*$", "/", link_path)
                is_parent_index = re.match(
                    r"^index\.(html?|php)$", link_path.split("/")[-1] or "", re.IGNORECASE
                ) and url_path.startswith(link_dir)
                if link_path != "/" and link_path != url_path and (url_path.startswith(link_path) or is_parent_index):
                    if debug and debug_removals is not None:
                        debug_removals.append(
                            DebugRemoval(
                                step="removeByContentPattern",
                                reason="section breadcrumb",
                                text=text_preview(el),
                            )
                        )
                    el.decompose()
            except Exception:
                pass

    if page_host:
        headings = main_content.select("h2, h3, h4, h5, h6")
        for heading in headings:
            if heading.parent is None:
                continue
            list_el = _next_element_sibling(heading)
            if not list_el or list_el.name not in ("ul", "ol"):
                continue
            items = [el for el in list_el.children if isinstance(el, Tag) and el.name == "li"]
            if len(items) < 2:
                continue

            trailing_content = False
            check_el = list_el
            while check_el is not None and check_el is not main_content:
                sibling = _next_element_sibling(check_el)
                while sibling is not None:
                    if (sibling.get_text() or "").strip():
                        trailing_content = True
                        break
                    sibling = _next_element_sibling(sibling)
                if trailing_content:
                    break
                check_el = check_el.parent
            if trailing_content:
                continue

            all_external_links = True
            for item in items:
                links = item.select("a[href]")
                if not links:
                    all_external_links = False
                    break
                item_text = (item.get_text() or "").strip()
                link_text_len = 0
                for link in links:
                    link_text_len += len((link.get_text() or "").strip())
                    try:
                        from urllib.parse import urljoin

                        link_host = urlparse(urljoin(url, link.get("href", "") or "")).hostname
                        if link_host:
                            link_host = link_host.replace("www.", "")
                        if link_host == page_host:
                            all_external_links = False
                            break
                    except Exception:
                        pass
                if not all_external_links:
                    break
                if link_text_len < len(item_text) * 0.6:
                    all_external_links = False
                    break
            if not all_external_links:
                continue

            if debug and debug_removals is not None:
                debug_removals.append(
                    DebugRemoval(
                        step="removeByContentPattern",
                        reason="trailing external link list",
                        text=text_preview(heading),
                    )
                )
                debug_removals.append(
                    DebugRemoval(
                        step="removeByContentPattern",
                        reason="trailing external link list",
                        text=text_preview(list_el),
                    )
                )
            list_el.decompose()
            heading.decompose()

    last_child = _last_element_child(main_content)
    while last_child and last_child.name.upper() in ("HR", "BR"):
        last_child = _prev_element_sibling(last_child)

    if last_child and last_child.name.upper() in ("SECTION", "DIV", "ASIDE"):
        paras: list = []
        has_non_para = False
        for child in last_child.children:
            if not isinstance(child, Tag):
                continue
            text = (child.get_text() or "").strip()
            if not text:
                continue
            if child.name == "p":
                paras.append(child)
            elif child.name != "br":
                has_non_para = True
                break

        if len(paras) >= 2 and not has_non_para:
            all_link_dense = True
            for p in paras:
                text = re.sub(r"\s+", " ", (p.get_text() or "").strip())
                links = p.select("a[href]")
                if not links:
                    all_link_dense = False
                    break
                link_text_len = sum(len((a.get_text() or "").strip()) for a in links)
                if link_text_len / (len(text) or 1) <= 0.6:
                    all_link_dense = False
                    break
                non_link_text = text
                for link in links:
                    link_text = (link.get_text() or "").strip()
                    non_link_text = non_link_text.replace(link_text, "")
                if re.search(r"[.!?]", non_link_text):
                    all_link_dense = False
                    break
            if all_link_dense:
                if debug and debug_removals is not None:
                    debug_removals.append(
                        DebugRemoval(
                            step="removeByContentPattern",
                            reason="trailing related posts block",
                            text=text_preview(last_child),
                        )
                    )
                last_child.decompose()

    total_words = count_words(main_content.get_text() or "")
    if total_words > 300:
        trailing_els: list = []
        trailing_words = 0
        child = _last_element_child(main_content)
        while child is not None:
            if isinstance(child, Tag):
                if child.get("id") == "footnotes":
                    child = _prev_element_sibling(child)
                    continue
                if child.name == "hr":
                    trailing_els.append(child)
                    break
                svg_words = 0
                for svg in child.select("svg"):
                    svg_words += count_words(svg.get_text() or "")
                words = count_words((child.get_text() or "").strip()) - svg_words
                if words > 25:
                    break
                trailing_words += words
                trailing_els.append(child)
            child = _prev_element_sibling(child)

        if len(trailing_els) >= 1 and trailing_words < total_words * 0.15:
            has_heading = any(_is_or_contains_heading(el) for el in trailing_els)
            has_content = any(el.select_one(CONTENT_ELEMENT_SELECTOR) for el in trailing_els)
            prose_paragraphs = 0
            for el in trailing_els:
                if el.name == "p" and count_words(el.get_text() or "") > 5:
                    prose_paragraphs += 1
            if has_heading and not has_content and prose_paragraphs < 2:
                for el in trailing_els:
                    if debug and debug_removals is not None:
                        debug_removals.append(
                            DebugRemoval(
                                step="removeByContentPattern",
                                reason="trailing thin section",
                                text=text_preview(el),
                            )
                        )
                    el.decompose()

    full_text = main_content.get_text() or ""
    boilerplate_elements = main_content.select("p, div, span, section")
    for el in boilerplate_elements:
        if el.parent is None:
            continue
        if closest(el, "pre, code"):
            continue
        text = (el.get_text() or "").strip()
        words = count_words(text)
        if words > 50 or words < 1:
            continue

        for pattern in BOILERPLATE_PATTERNS:
            if pattern.search(text):
                target = el
                while target.parent is not None and target.parent is not main_content:
                    if _next_element_sibling(target):
                        break
                    target = target.parent

                target_text = target.get_text() or ""
                target_pos = full_text.find(target_text)
                if target_pos < 200:
                    if target is not el and _next_element_sibling(el) is None:
                        if debug and debug_removals is not None:
                            debug_removals.append(
                                DebugRemoval(
                                    step="removeByContentPattern",
                                    reason="boilerplate text",
                                    text=text_preview(el),
                                )
                            )
                        el.decompose()
                    continue

                _remove_trailing_with_cascade(target, main_content, debug, debug_removals)
                break

    for heading in main_content.select("h2, h3, h4, h5, h6"):
        if heading.parent is None:
            continue
        heading_text = (heading.get_text() or "").strip()
        is_cta = bool(CTA_HEADING_PATTERN.search(heading_text))
        if not is_cta and not RELATED_HEADING_PATTERN.search(heading_text):
            continue

        if content_text.find(heading_text) < 500:
            continue

        target = _walk_up_isolated(heading, main_content)

        if target is heading:
            if not is_cta:
                continue
            _remove_trailing_siblings(heading, True, debug, debug_removals)
        else:
            _remove_thin_preceding_section(target, debug, debug_removals)
            if debug and debug_removals is not None:
                debug_removals.append(
                    DebugRemoval(
                        step="removeByContentPattern",
                        reason="related content section",
                        text=text_preview(target),
                    )
                )
            _remove_trailing_with_cascade(target, main_content, debug, debug_removals)
        break

    for el in main_content.select("p"):
        if el.parent is None:
            continue
        text = (el.get_text() or "").strip()
        if not RELATED_INTRO_PATTERN.search(text):
            continue
        if count_words(text) > 20:
            continue
        if el.select_one(CONTENT_ELEMENT_SELECTOR):
            continue
        if debug and debug_removals is not None:
            debug_removals.append(
                DebugRemoval(
                    step="removeByContentPattern",
                    reason="related content intro",
                    text=text_preview(el),
                )
            )
        el.decompose()

    content_word_count = count_words(content_text)
    for el in main_content.select("div"):
        if el.parent is None:
            continue
        children = [c for c in el.children if isinstance(c, Tag)]
        if len(children) < 2:
            continue

        card_count = sum(
            1
            for c in children
            if c.select_one("img, picture") and (c.select_one("h2, h3, h4") or c.select_one("a[href]"))
        )
        if card_count < 2 or card_count < len(children) * 0.7:
            continue

        first_text = (children[0].get_text() or "").strip()[:30]
        if len(first_text) < 5 or content_text.find(first_text) < 500:
            continue

        grid_words = count_words(el.get_text() or "")
        if content_word_count > 0 and grid_words / content_word_count > 0.3:
            continue

        target = _walk_up_isolated(el, main_content)
        if target is el:
            continue

        _remove_thin_preceding_section(target, debug, debug_removals)
        if debug and debug_removals is not None:
            debug_removals.append(
                DebugRemoval(
                    step="removeByContentPattern",
                    reason="related post cards",
                    text=text_preview(target),
                )
            )
        _remove_trailing_siblings(target, True, debug, debug_removals)
        break

    for el in main_content.select("div, section, aside"):
        if el.parent is None:
            continue
        if closest(el, "pre, code"):
            continue
        if not _is_newsletter_element(el, 60):
            continue

        el_words = count_words((el.get_text() or "").strip())
        target = el
        while target.parent is not None and target.parent is not main_content:
            parent_words = count_words((target.parent.get_text() or "").strip())
            if parent_words > el_words * 2 + 15:
                break
            target = target.parent

        if debug and debug_removals is not None:
            debug_removals.append(
                DebugRemoval(
                    step="removeByContentPattern",
                    reason="newsletter signup",
                    text=text_preview(target),
                )
            )
        target.decompose()
        break

    for el in main_content.select("ul"):
        if el.parent is None:
            continue
        if not _is_newsletter_element(el, 30):
            continue
        if debug and debug_removals is not None:
            debug_removals.append(
                DebugRemoval(
                    step="removeByContentPattern",
                    reason="newsletter signup list",
                    text=text_preview(el),
                )
            )
        el.decompose()
        break

    for el in main_content.select("div, section"):
        if el.parent is None:
            continue
        text = (el.get_text() or "").strip()
        words = count_words(text)
        if words < 2 or words > 40:
            continue

        pos = content_text.find(text[:60])
        if pos < 0:
            continue
        dist_from_end = len(content_text) - (pos + len(text))
        if dist_from_end > 300:
            continue

        children = el.select("div, span, p, dt, dd, li")
        has_label = False
        for child in children:
            child_text = (child.get_text() or "").strip()
            if AUTHOR_CONTACT_LABEL_PATTERN.search(child_text):
                has_label = True
                break
        if not has_label:
            continue

        has_contact_info = (
            EMAIL_PATTERN.search(text) or PHONE_PATTERN.search(text) or el.select_one('a[href^="mailto:"]')
        )
        if not has_contact_info:
            continue

        target = _walk_up_isolated(el, main_content)
        if debug and debug_removals is not None:
            debug_removals.append(
                DebugRemoval(
                    step="removeByContentPattern",
                    reason="author contact block",
                    text=text_preview(target),
                )
            )
        target.decompose()
        break

    for el in main_content.select("p, span, div"):
        if el.parent is None:
            continue
        el_text = (el.get_text() or "").strip()
        if not SHARE_AUTHOR_LABEL.search(el_text):
            continue

        container = el
        while container.parent is not None and container.parent is not main_content:
            parent = container.parent
            if count_words((parent.get_text() or "").strip()) > 15:
                break
            container = parent

        if container.select_one(CONTENT_ELEMENT_NO_IMG_SELECTOR):
            continue

        if debug and debug_removals is not None:
            debug_removals.append(
                DebugRemoval(
                    step="removeByContentPattern",
                    reason="author/share widget",
                    text=text_preview(container),
                )
            )
        container.decompose()

    for el in main_content.select("a, p, div, span"):
        if el.parent is None:
            continue
        text = (el.get_text() or "").strip()
        if not SOCIAL_COUNTER_PATTERN.search(text):
            continue
        if el.name == "a" and el.get("href"):
            continue
        if el.name != "a":
            pos = content_text.find(text)
            dist_from_end = len(content_text) - (pos + len(text))
            if dist_from_end > 200:
                continue
        target = _walk_up_to_wrapper(el, text, main_content)
        if debug and debug_removals is not None:
            debug_removals.append(
                DebugRemoval(
                    step="removeByContentPattern",
                    reason="social engagement counter",
                    text=text_preview(target),
                )
            )
        target.decompose()

    for el in main_content.select("div"):
        if el.parent is None:
            continue
        text = (el.get_text() or "").strip()
        words = count_words(text)
        if words < 1 or words > 10:
            continue
        if re.search(r"[.!?]", text):
            continue
        if el.select_one(CONTENT_ELEMENT_SELECTOR):
            continue

        pos = content_text.find(text)
        if pos < 0:
            continue
        dist_from_end = len(content_text) - (pos + len(text))
        if dist_from_end > 300:
            continue

        links = el.select("a[href]")
        if not links:
            continue
        link_text_len = sum(len((a.get_text() or "").strip()) for a in links)
        if link_text_len / (len(text) or 1) < 0.8:
            continue

        if debug and debug_removals is not None:
            debug_removals.append(
                DebugRemoval(
                    step="removeByContentPattern",
                    reason="trailing tag link block",
                    text=text_preview(el),
                )
            )
        el.decompose()


def _last_element_child(el: Tag) -> Optional[Tag]:
    for child in reversed(list(el.children)):
        if isinstance(child, Tag):
            return child
    return None
