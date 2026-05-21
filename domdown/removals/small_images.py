from __future__ import annotations

import re
from typing import Optional, Set

from bs4 import Tag

from domdown.utils import get_class_name, is_base64_placeholder, log_debug
from domdown.utils.dom import closest

STYLE_WIDTH_PATTERN = re.compile(r"width\s*:\s*(\d+)")
STYLE_HEIGHT_PATTERN = re.compile(r"height\s*:\s*(\d+)")
URL_WIDTH_PATTERN = re.compile(r"(?:width[=:/]|[/,?&]w[_:=])(\d+)")
LOOKS_LIKE_LATEX_RE = re.compile(r"\\[a-zA-Z]{2,}")


def get_element_identifier(element: Tag) -> Optional[str]:
    if element.name == "img":
        data_src = element.get("data-src")
        if data_src:
            return f"src:{data_src}"

        src = element.get("src", "") or ""
        srcset = element.get("srcset", "") or ""
        data_srcset = element.get("data-srcset")

        if src:
            return f"src:{src}"
        if srcset:
            return f"srcset:{srcset}"
        if data_srcset:
            return f"srcset:{data_srcset}"

    el_id = element.get("id", "") or ""
    class_name = get_class_name(element)
    view_box = element.get("viewBox", "") if element.name == "svg" else ""

    if el_id:
        return f"id:{el_id}"
    if view_box:
        return f"viewBox:{view_box}"
    if class_name:
        return f"class:{class_name}"

    return None


def _parse_dimension(value) -> int:
    if value is None:
        return 0
    s = str(value).strip()
    m = re.match(r"^(\d+)", s)
    return int(m.group(1)) if m else 0


def find_small_images(doc: Tag, debug: bool) -> Set[str]:
    MIN_DIMENSION = 33
    small_images: Set[str] = set()
    processed_count = 0

    elements = doc.select("img, svg")

    for element in elements:
        attr_width = _parse_dimension(element.get("width", "0"))
        attr_height = _parse_dimension(element.get("height", "0"))

        view_box_width = 0.0
        view_box_height = 0.0
        if element.name == "svg":
            view_box = element.get("viewBox")
            if view_box:
                parts = re.split(r"[\s,]+", view_box)
                if len(parts) == 4:
                    view_box_width = float(parts[2]) or 0
                    view_box_height = float(parts[3]) or 0

        style = element.get("style", "") or ""
        style_width_match = STYLE_WIDTH_PATTERN.search(style)
        style_height_match = STYLE_HEIGHT_PATTERN.search(style)
        style_width = int(style_width_match.group(1)) if style_width_match else 0
        style_height = int(style_height_match.group(1)) if style_height_match else 0

        widths = [d for d in [attr_width, style_width, view_box_width] if d > 0]
        heights = [d for d in [attr_height, style_height, view_box_height] if d > 0]

        if not widths and not heights and element.name == "img":
            srcset = element.get("srcset", "") or ""
            one_x_match = re.search(r"(\S+)\s+1x", srcset)
            if one_x_match:
                url_width_match = URL_WIDTH_PATTERN.search(one_x_match.group(1))
                if url_width_match:
                    widths.append(int(url_width_match.group(1)))

        if widths or heights:
            effective_width = min(widths) if widths else float("inf")
            effective_height = min(heights) if heights else float("inf")

            if effective_width < MIN_DIMENSION or effective_height < MIN_DIMENSION:
                if element.name == "img":
                    alt = element.get("alt", "") or ""
                    if LOOKS_LIKE_LATEX_RE.search(alt):
                        continue
                    classes = element.get("class", [])
                    if isinstance(classes, list) and ("latex" in classes or "tex" in classes):
                        continue
                    if element.get("data-latex") or element.get("data-math"):
                        continue

                identifier = get_element_identifier(element)
                if identifier:
                    small_images.add(identifier)
                    processed_count += 1

    log_debug(debug, "Found small elements:", count=processed_count)
    return small_images


def remove_small_images(doc: Tag, small_images: Set[str], debug: bool) -> None:
    removed_count = 0

    for tag_name in ("img", "svg"):
        elements = list(doc.select(tag_name))
        for element in elements:
            if tag_name == "img":
                src = element.get("src", "") or ""
                has_alt_src = (
                    element.get("srcset")
                    or element.get("data-src")
                    or element.get("data-srcset")
                    or element.get("data-lazy-src")
                    or element.get("data-original")
                )
                if not src and not has_alt_src:
                    element.decompose()
                    removed_count += 1
                    continue
                if not has_alt_src and not closest(element, "picture") and is_base64_placeholder(src):
                    element.decompose()
                    removed_count += 1
                    continue

            identifier = get_element_identifier(element)
            if identifier and identifier in small_images:
                element.decompose()
                removed_count += 1

    log_debug(debug, "Removed small elements:", count=removed_count)
