from __future__ import annotations

import html
import re
from typing import Optional

import soupsieve as sv
from bs4 import BeautifulSoup, Tag

_SURROGATE_PAIR_RE = re.compile(r"[\uD800-\uDBFF][\uDC00-\uDFFF]")
_CROSS_TAG_SURROGATE_RE = re.compile(r"([\uD800-\uDBFF])((?:<[^>]+>\s*)+)([\uDC00-\uDFFF])", re.DOTALL)
_LONE_SURROGATE_RE = re.compile(r"[\uD800-\uDFFF]")
_JSON_LD_OPEN_RE = re.compile(
    r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>',
    re.IGNORECASE,
)


def _repair_surrogates(html_str: str) -> str:
    def pair_to_char(match: re.Match) -> str:
        pair = match.group(0)
        codepoint = 0x10000 + ((ord(pair[0]) - 0xD800) << 10) + (ord(pair[1]) - 0xDC00)
        return chr(codepoint)

    def cross_tag_pair_to_char(match: re.Match) -> str:
        high = match.group(1)
        middle = match.group(2)
        low = match.group(3)
        codepoint = 0x10000 + ((ord(high) - 0xD800) << 10) + (ord(low) - 0xDC00)
        return chr(codepoint) + middle

    html_str = _CROSS_TAG_SURROGATE_RE.sub(cross_tag_pair_to_char, html_str)
    html_str = _SURROGATE_PAIR_RE.sub(pair_to_char, html_str)
    return _LONE_SURROGATE_RE.sub("\ufffd", html_str)


def _protect_json_ld(html_str: str) -> str:
    result = []
    cursor = 0
    while True:
        open_match = _JSON_LD_OPEN_RE.search(html_str, cursor)
        if not open_match:
            result.append(html_str[cursor:])
            break

        result.append(html_str[cursor : open_match.end()])
        scan_start = open_match.end()
        in_string = False
        escape = False
        close_idx = -1
        i = scan_start
        while i < len(html_str):
            if not in_string and html_str[i : i + 9].lower() == "</script>":
                close_idx = i
                break

            ch = html_str[i]
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = not in_string
            i += 1

        if close_idx == -1:
            result.append(html_str[scan_start:])
            break

        segment = html_str[scan_start:close_idx]
        segment_parts = []
        seg_cursor = 0
        in_string = False
        escape = False
        while seg_cursor < len(segment):
            if in_string and segment[seg_cursor : seg_cursor + 9].lower() == "</script>":
                segment_parts.append("<\\/script>")
                seg_cursor += 9
                continue

            ch = segment[seg_cursor]
            segment_parts.append(ch)
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = not in_string
            seg_cursor += 1

        result.append("".join(segment_parts))
        result.append("</script>")
        cursor = close_idx + 9

    return "".join(result)


def parse_html(html_str: str) -> Tag:
    if not html_str:
        soup = BeautifulSoup("", "lxml")
        return soup
    html_str = _protect_json_ld(html_str)
    html_str = _repair_surrogates(html_str)
    return BeautifulSoup(html_str, "lxml")


def serialize_html(el: Tag) -> str:
    return el.decode_contents()


def decode_html_entities(text: str) -> str:
    return html.unescape(text)


def escape_html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def get_class_name(el: Tag) -> str:
    cls = el.get("class")
    if cls is None:
        return ""
    if isinstance(cls, list):
        return " ".join(cls)
    return str(cls)


_RESPONSIVE_SHOW_RE = re.compile(r"^(sm|md|lg|xl|2xl|min-\[|max-\[):(?:block|flex|grid|inline|table|contents)")


def has_responsive_show_class(class_name: str) -> bool:
    return any(_RESPONSIVE_SHOW_RE.match(t) for t in class_name.split())


def is_dangerous_url(url: str) -> bool:
    normalized = re.sub(r"[\s\u0000-\u001F]+", "", url).lower()
    return normalized.startswith("javascript:") or normalized.startswith("data:text/html")


def is_direct_table_child(el: Tag, ancestor: Tag) -> bool:
    parent = el.parent
    while parent is not None and parent is not ancestor:
        if isinstance(parent, Tag) and parent.name == "table":
            return False
        parent = parent.parent
    return parent is ancestor


def transfer_content(source: Tag, target: Tag) -> None:
    target.clear()
    children = list(source.children)
    for child in children:
        target.append(child.extract())


def closest(el: Tag, selector: str) -> Optional[Tag]:
    current: Optional[Tag] = el
    while current is not None:
        if isinstance(current, Tag):
            try:
                if sv.match(selector, current):
                    return current
            except Exception:
                pass
        current = current.parent if hasattr(current, "parent") else None
    return None


def contains(parent: Tag, child: Tag) -> bool:
    current = child.parent
    while current is not None:
        if current is parent:
            return True
        current = current.parent
    return False
