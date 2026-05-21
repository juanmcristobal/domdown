from __future__ import annotations

import re
from typing import Any, Dict, Union

from bs4 import Comment, NavigableString, Tag

CJK_CHAR_RANGES = "\u3040-\u309f\u30a0-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uac00-\ud7af"

_RESPONSIVE_SHOW_RE = re.compile(r"^(sm|md|lg|xl|2xl|min-\[|max-\[):(?:block|flex|grid|inline|table|contents)")

_B64_DATA_URL_RE = re.compile(r"^data:image/([^;]+);base64,")


def is_element(node: Any) -> bool:
    return isinstance(node, Tag)


def is_text_node(node: Any) -> bool:
    return isinstance(node, NavigableString) and not isinstance(node, Comment)


def is_comment_node(node: Any) -> bool:
    return isinstance(node, Comment)


def is_svg_element(el: Tag) -> bool:
    current = el
    while current is not None:
        if isinstance(current, Tag) and current.name == "svg":
            return True
        current = current.parent
    return False


def get_computed_style(el: Tag) -> Dict[str, str]:
    style_attr = el.get("style", "")
    if not style_attr or not isinstance(style_attr, str):
        return {}
    result: Dict[str, str] = {}
    for part in style_attr.split(";"):
        part = part.strip()
        if ":" in part:
            key, _, value = part.partition(":")
            result[key.strip()] = value.strip()
    return result


def text_preview(el_or_text: Union[Tag, str], max_length: int = 200) -> str:
    if isinstance(el_or_text, str):
        text = el_or_text
    else:
        text = el_or_text.get_text()
    return text.strip()[:max_length]


def log_debug(debug: bool, *args: Any, **kwargs: Any) -> None:
    if debug:
        parts = ["Domdown:"]
        for a in args:
            parts.append(str(a))
        for k, v in kwargs.items():
            parts.append(f"{k}={v!r}")
        print(" ".join(parts))


def normalize_text(text: str) -> str:
    return (
        text.replace("\u00a0", " ")
        .replace("\u2018", "'")
        .replace("\u2019", "'")
        .replace("\u201a", "'")
        .replace("\u201b", "'")
        .replace("\u2012", "-")
        .replace("\u2013", "-")
        .replace("\u2014", "-")
        .replace("\u2015", "-")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u201e", '"')
        .replace("\u201f", '"')
        .replace("\u2026", "...")
    )


def count_words(text: str) -> int:
    if not text:
        return 0

    cjk_count = 0
    word_count = 0
    in_word = False

    for ch in text:
        code = ord(ch)

        if (
            (0x3040 <= code <= 0x309F)
            or (0x30A0 <= code <= 0x30FF)
            or (0x3400 <= code <= 0x4DBF)
            or (0x4E00 <= code <= 0x9FFF)
            or (0xF900 <= code <= 0xFAFF)
            or (0xAC00 <= code <= 0xD7AF)
        ):
            cjk_count += 1
            in_word = False
        elif code <= 32:
            in_word = False
        elif not in_word:
            word_count += 1
            in_word = True

    return cjk_count + word_count


def get_class_name(el: Tag) -> str:
    cls = el.get("class")
    if cls is None:
        return ""
    if isinstance(cls, list):
        return " ".join(cls)
    return str(cls)


def has_responsive_show_class(class_name: str) -> bool:
    return any(_RESPONSIVE_SHOW_RE.match(t) for t in class_name.split())


def is_base64_placeholder(src: str) -> bool:
    match = _B64_DATA_URL_RE.match(src)
    if not match:
        return False
    if match.group(1) == "svg+xml":
        return False
    b64_starts = match.end()
    b64_length = len(src) - b64_starts
    return b64_length < 133
