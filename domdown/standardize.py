from __future__ import annotations

import re
import time
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from bs4 import BeautifulSoup, Comment, NavigableString, Tag

from domdown.constants import (
    ALLOWED_ATTRIBUTES,
    ALLOWED_ATTRIBUTES_DEBUG,
    ALLOWED_EMPTY_ELEMENTS,
    BLOCK_ELEMENTS_SELECTOR,
    BLOCK_ELEMENTS_SET,
    BLOCK_LEVEL_ELEMENTS,
    INLINE_ELEMENTS,
    PRESERVE_ELEMENTS,
    TAILWIND_COLORS,
    TAILWIND_SPECIAL,
    TW_ARBITRARY_RE,
    TW_COLOR_CLASS_RE,
    TW_SPECIAL_CLASS_RE,
)
from domdown.elements.code import code_block_rules
from domdown.elements.headings import heading_rules
from domdown.elements.images import image_rules
from domdown.elements.math import math_rules
from domdown.types import DomdownMetadata
from domdown.utils import get_computed_style, is_element, is_svg_element, is_text_node, log_debug, normalize_text
from domdown.utils.dom import closest, get_class_name, is_direct_table_child, transfer_content

_debug = False

DATA_AS_ALLOWED: Set[str] = {"p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "blockquote"}

TW_BLOCK_RE = re.compile(r"(?:^|\s)block(?:\s|$)")
DISPLAY_BLOCK_RE = re.compile(r"display\s*:\s*block", re.IGNORECASE)

LIGHT_DARK_RE = re.compile(r"light-dark\(\s*([^,]+?)\s*,\s*[^)]+?\)")
CSS_VAR_RE = re.compile(r"var\(--([^,)]+)(?:,\s*([^)]+))\)")
SVG_COLOR_ATTRS = ["fill", "stroke", "color", "stop-color", "flood-color", "lighting-color"]

SVG_FILLED_TAGS: Set[str] = {"path", "rect", "circle", "ellipse", "polygon"}
SVG_STROKE_TAGS: Set[str] = {"line", "polyline"}
SVG_TEXT_TAGS: Set[str] = {"text", "tspan"}
SVG_NON_RENDERED_ANCESTOR = "defs, clipPath, mask, pattern, marker"
GRIDLINE_STROKE_OPACITY = "0.2"


def _new_tag(name: str, soup: Optional[BeautifulSoup] = None) -> Tag:
    if soup is None:
        soup = BeautifulSoup("", "lxml")
    return soup.new_tag(name)


def _get_soup(tag: Tag) -> BeautifulSoup:
    current = tag
    while current.parent is not None:
        current = current.parent
    if isinstance(current, BeautifulSoup):
        return current
    return BeautifulSoup("", "lxml")


def unwrap_element(el: Tag) -> None:
    el.unwrap()


def standardize_content(
    element: Tag,
    metadata: DomdownMetadata,
    doc: Any,
    debug: bool = False,
    sub_profile: Optional[Dict[str, float]] = None,
) -> None:
    global _debug
    _debug = debug

    def step(name: str, fn: Callable) -> Any:
        if sub_profile is not None:
            t = time.perf_counter()
            r = fn()
            elapsed = (time.perf_counter() - t) * 1000
            sub_profile[name] = (sub_profile.get(name) or 0) + round(elapsed)
            return r
        else:
            return fn()

    step("standardizeDropCaps", lambda: standardize_drop_caps(element))
    step("standardizeSpaces", lambda: standardize_spaces(element))
    step("removeHtmlComments", lambda: remove_html_comments(element))
    step("standardizeHeadings", lambda: standardize_headings(element, metadata.title, doc))
    step("wrapPreformattedCode", lambda: wrap_preformatted_code(element, doc))
    step("standardizeElements", lambda: standardize_elements(element, doc, sub_profile))
    step("resolveSvgColors", lambda: resolve_svg_colors(element, doc))

    if not debug:
        step("replaceCustomElements", lambda: replace_custom_elements(element, doc))
        step("convertDataAsSpans", lambda: convert_data_as_spans(element, doc))
        step("convertBlockSpans", lambda: convert_block_spans(element, doc))
        step("unwrapLayoutTables", lambda: unwrap_layout_tables(element))
        step("flattenWrapperElements[1]", lambda: flatten_wrapper_elements(element, doc))
        step("removePermalinkAnchors", lambda: remove_permalink_anchors(element))
        step("stripUnwantedAttributes", lambda: strip_unwanted_attributes(element, debug))
        step("unwrapBareSpans", lambda: unwrap_bare_spans(element))

        def _unwrap_special_links() -> None:
            for code_el in element.select("code a"):
                unwrap_element(code_el)
            for link in element.select('a[href^="javascript:"]'):
                unwrap_element(link)
            for link in list(element.select("a")):
                href = link.get("href", "")
                if not href or href.startswith("#"):
                    continue
                heading = None
                for child in list(link.children):
                    if is_element(child) and child.name and re.match(r"^h[1-6]$", child.name, re.IGNORECASE):
                        heading = child
                        break
                if not heading:
                    continue
                soup = _get_soup(link)
                inner_link = soup.new_tag("a", attrs={"href": href})
                heading_children = list(heading.children)
                for hc in heading_children:
                    inner_link.append(hc.extract())
                heading.append(inner_link)
                unwrap_element(link)
            for link in list(element.select('a[href^="#"]')):
                if link.select_one("h1, h2, h3, h4, h5, h6"):
                    unwrap_element(link)

        step("unwrapSpecialLinks", _unwrap_special_links)
        step("removeObsoleteElements", lambda: _remove_obsolete(element))
        step("removeEmptyElements", lambda: remove_empty_elements(element))
        step("removeTrailingHeadings", lambda: remove_trailing_headings(element))
        step("removeOrphanedDividers[1]", lambda: remove_orphaned_dividers(element))
        step("flattenWrapperElements[2]", lambda: flatten_wrapper_elements(element, doc))
        step("removeOrphanedDividers[2]", lambda: remove_orphaned_dividers(element))
        step("stripExtraBrElements", lambda: strip_extra_br_elements(element))
        step("removeEmptyLines", lambda: remove_empty_lines(element, doc))
    else:
        step("stripUnwantedAttributes", lambda: strip_unwanted_attributes(element, debug))
        step("removeTrailingHeadings", lambda: remove_trailing_headings(element))
        step("stripExtraBrElements", lambda: strip_extra_br_elements(element))
        log_debug(_debug, "Debug mode: Skipping div flattening to preserve structure")


def _remove_obsolete(element: Tag) -> None:
    for el in element.select("object, embed, applet"):
        el.decompose()


def wrap_preformatted_code(element: Tag, doc: Any) -> None:
    for code in list(element.select("code")):
        if closest(code, "pre"):
            continue
        style = code.get("style", "")
        if not style or not re.search(r"white-space\s*:\s*pre", style):
            continue
        soup = _get_soup(code)
        pre = soup.new_tag("pre")
        code_parent = code.parent
        if code_parent:
            code_parent.insert_before(pre, code)
        pre.append(code.extract())


def standardize_spaces(element: Tag) -> None:
    def _process(node: Any) -> None:
        if is_element(node):
            tag = node.name.lower() if node.name else ""
            if tag in ("pre", "code") or is_svg_element(node):
                return
        if is_text_node(node):
            text = str(node)
            new_text = text.replace("\xa0", " ")
            if new_text != text:
                node.replace_with(NavigableString(new_text))
        if hasattr(node, "children"):
            for child in list(node.children):
                _process(child)

    _process(element)


def remove_trailing_headings(element: Tag) -> None:
    removed_count = 0

    def _has_content_after(el: Tag) -> bool:
        next_content = ""
        sibling = el.next_sibling
        while sibling is not None:
            if is_text_node(sibling):
                next_content += str(sibling)
            elif is_element(sibling):
                next_content += sibling.get_text()
            sibling = sibling.next_sibling
        if next_content.strip():
            return True
        parent = el.parent
        if parent is not None and parent is not element:
            return _has_content_after(parent)
        return False

    headings = list(element.select("h1, h2, h3, h4, h5, h6"))
    headings.reverse()
    for heading in headings:
        if not _has_content_after(heading):
            heading.decompose()
            removed_count += 1
        else:
            break

    if removed_count > 0:
        log_debug(_debug, "Removed trailing headings:", removed_count)


def remove_orphaned_dividers(element: Tag) -> None:
    while True:
        node = element.contents[0] if element.contents else None
        while node is not None and is_text_node(node) and not str(node).strip():
            node = node.next_sibling
        if node is not None and is_element(node) and node.name and node.name.lower() == "hr":
            node.decompose()
        else:
            break

    while True:
        node = element.contents[-1] if element.contents else None
        while node is not None and is_text_node(node) and not str(node).strip():
            node = node.previous_sibling
        if node is not None and is_element(node) and node.name and node.name.lower() == "hr":
            node.decompose()
        else:
            break

    for hr in list(element.select("hr")):
        if hr.parent is None:
            continue
        node = hr.next_sibling
        while node is not None:
            if is_text_node(node) and not str(node).strip():
                node = node.next_sibling
                continue
            if is_element(node) and node.name and node.name.lower() == "hr":
                next_node = node.next_sibling
                node.decompose()
                node = next_node
                continue
            break


def standardize_headings(element: Tag, title: str, doc: Any) -> None:
    h1s = list(element.select("h1"))
    for h1 in h1s:
        soup = _get_soup(h1)
        h2 = soup.new_tag("h2")
        transfer_content(h1, h2)
        for attr_name, attr_value in list(h1.attrs.items()):
            if attr_name in ALLOWED_ATTRIBUTES:
                h2[attr_name] = attr_value
        h1.replace_with(h2)

    h2s = list(element.select("h2"))
    if h2s:
        first_h2 = h2s[0]
        permalink_text = ""
        for a in first_h2.select("a"):
            if _is_permalink_anchor(a):
                permalink_text += a.get_text()
        first_h2_text = normalize_text(first_h2.get_text().replace(permalink_text, ""))
        normalized_title = normalize_text(title)
        if normalized_title and normalized_title == first_h2_text:
            first_h2.decompose()


def _is_permalink_anchor(node: Tag) -> bool:
    if not is_element(node) or node.name != "a":
        return False
    href = node.get("href", "")
    title_attr = (node.get("title", "") or "").lower()
    class_attr = node.get("class", "") or ""
    if isinstance(class_attr, list):
        class_attr = " ".join(class_attr)
    class_attr = class_attr.lower()
    text = node.get_text().strip()
    if href.startswith("#"):
        return True
    if "permalink" in title_attr:
        return True
    if "permalink" in class_attr or "heading-anchor" in class_attr or "anchor-link" in class_attr:
        return True
    if re.match(r"^[#¶§🔗\ufeff]$", text):
        return True
    return False


def remove_permalink_anchors(element: Tag) -> None:
    for link in list(
        element.select("h1 a, h2 a, h3 a, h4 a, h5 a, h6 a, a.permalink, a.anchor-link, a.heading-anchor")
    ):
        if _is_permalink_anchor(link):
            link.decompose()


def remove_html_comments(element: Tag) -> None:
    removed_count = 0
    comments = element.find_all(string=lambda text: isinstance(text, Comment))
    for comment in comments:
        comment.extract()
        removed_count += 1
    log_debug(_debug, "Removed HTML comments:", removed_count)


def strip_unwanted_attributes(element: Tag, debug: bool) -> None:
    attribute_count = 0

    def _process(el: Tag) -> None:
        nonlocal attribute_count
        if is_svg_element(el):
            if not debug and el.get("class"):
                del el["class"]
                attribute_count += 1
            return

        tag = el.name.lower() if el.name else ""
        attrs_to_remove = []
        for attr_name, attr_value in list(el.attrs.items()):
            attr_name_lower = attr_name.lower()
            if isinstance(attr_value, list):
                attr_value_str = " ".join(attr_value)
            else:
                attr_value_str = str(attr_value)

            if (
                attr_name_lower == "id"
                and (
                    attr_value_str.startswith("fnref:")
                    or attr_value_str.startswith("fn:")
                    or attr_value_str == "footnotes"
                )
            ) or (
                attr_name_lower == "class"
                and (
                    (tag == "code" and attr_value_str.startswith("language-"))
                    or attr_value_str == "footnote-backref"
                    or bool(re.match(r"^callout(?:-|$)", attr_value_str))
                )
            ):
                continue

            if debug:
                if (
                    attr_name_lower not in ALLOWED_ATTRIBUTES
                    and attr_name_lower not in ALLOWED_ATTRIBUTES_DEBUG
                    and not attr_name_lower.startswith("data-")
                ):
                    attrs_to_remove.append(attr_name)
                    attribute_count += 1
            else:
                if attr_name_lower not in ALLOWED_ATTRIBUTES:
                    attrs_to_remove.append(attr_name)
                    attribute_count += 1

        for attr_name in attrs_to_remove:
            del el[attr_name]

    _process(element)
    for el in element.select("*"):
        _process(el)

    log_debug(_debug, "Stripped attributes:", attribute_count)


def unwrap_layout_tables(element: Tag) -> None:
    tables = list(element.select("table"))
    count = 0

    for table in tables:
        if table.parent is None:
            continue
        if table.select_one("thead, tfoot, th, caption"):
            continue

        cells_direct = []
        for tbody in table.select(":scope > tbody"):
            for tr in tbody.select(":scope > tr"):
                for td in tr.select(":scope > td"):
                    cells_direct.append(td)
        for tr in table.select(":scope > tr"):
            for td in tr.select(":scope > td"):
                cells_direct.append(td)
        non_empty = [td for td in cells_direct if td.get_text().strip()]
        if len(non_empty) != 1:
            continue
        cell = non_empty[0]
        children = [c for c in cell.children if is_element(c) and c.get_text().strip()]
        if len(children) == 1 and children[0].name and children[0].name.lower() in BLOCK_LEVEL_ELEMENTS:
            table.replace_with(children[0].extract())
            count += 1

    log_debug(_debug, "Unwrapped layout tables:", count)


def replace_custom_elements(element: Tag, doc: Any) -> None:
    custom_elements = []
    for el in element.select("*"):
        if el.name and "-" in el.name:
            if el.name.lower() not in INLINE_ELEMENTS and not is_svg_element(el):
                custom_elements.append(el)
    custom_elements.reverse()

    replaced_count = 0
    soup = _get_soup(element)
    for el in custom_elements:
        if el.parent is None:
            continue
        div = soup.new_tag("div")
        children = list(el.children)
        for child in children:
            div.append(child.extract())
        el.replace_with(div)
        replaced_count += 1
    log_debug(_debug, "Replaced custom elements with divs:", replaced_count)


def standardize_drop_caps(element: Tag) -> None:
    caps = list(element.select('span[data-caps="initial"]'))
    count = 0

    for span in caps:
        if span.parent is None:
            continue
        next_el = span.next_sibling
        while next_el is not None and is_text_node(next_el):
            next_el = next_el.next_sibling
        if next_el is not None and is_element(next_el) and next_el.name == "small":
            initial = span.get_text()
            rest = next_el.get_text()
            merged = NavigableString(initial + rest)
            span.parent.insert_before(merged, span)
            next_el.decompose()
            span.decompose()
        else:
            unwrap_element(span)
        count += 1

    if count > 0:
        _normalize(element)
    log_debug(_debug, "Standardized drop caps:", count)


def convert_data_as_spans(element: Tag, doc: Any) -> None:
    converted_count = 0
    spans = list(element.select("span[data-as]"))
    soup = _get_soup(element)
    for span in spans:
        if span.parent is None:
            continue
        target = (span.get("data-as") or "").lower()
        if target not in DATA_AS_ALLOWED:
            continue
        replacement = soup.new_tag(target)
        transfer_content(span, replacement)
        span.replace_with(replacement)
        converted_count += 1
    log_debug(_debug, "Converted data-as spans:", converted_count)


def convert_block_spans(element: Tag, doc: Any) -> None:
    converted_count = 0
    spans = list(element.select('span[class*="block"], span[style*="block"]'))
    soup = _get_soup(element)
    for span in spans:
        if span.parent is None:
            continue
        class_name = get_class_name(span)
        is_block = TW_BLOCK_RE.search(class_name) if class_name else False
        if not is_block:
            style = span.get("style", "") or ""
            if not DISPLAY_BLOCK_RE.search(style):
                continue
        if not span.get_text().strip():
            continue
        p = soup.new_tag("p")
        transfer_content(span, p)
        span.replace_with(p)
        converted_count += 1
    log_debug(_debug, "Converted block spans to paragraphs:", converted_count)


def unwrap_bare_spans(element: Tag) -> None:
    spans = list(element.select("span"))
    spans.reverse()
    unwrapped_count = 0

    for span in spans:
        if span.parent is None:
            continue
        if span.attrs:
            continue
        parent = span.parent
        if parent is None:
            continue
        children = list(span.children)
        for child in reversed(children):
            span.insert_before(child.extract())
        span.decompose()
        unwrapped_count += 1

    if unwrapped_count > 0:
        _normalize(element)

    log_debug(_debug, "Unwrapped bare spans:", unwrapped_count)


def resolve_svg_colors(element: Tag, doc: Any) -> None:
    svgs = element.select("svg")
    if not svgs:
        return

    is_browser = False
    resolve_cache: Dict[str, str] = {}

    def _resolve_var(value: str, svg_parent: Optional[Tag] = None) -> str:
        value = LIGHT_DARK_RE.sub(lambda m: m.group(1).strip(), value)
        if "var(" not in value:
            return value

        if is_browser:
            cached = resolve_cache.get(value)
            if cached:
                return cached

        var_match = CSS_VAR_RE.search(value)
        if var_match:
            fallback = (var_match.group(2) or "").strip()
            if fallback and "var(" not in fallback:
                return fallback

            name = var_match.group(1).lower()
            tw_match = re.search(r"(?:^|-)([a-z]+)-(\d{2,3})$", name)
            if tw_match:
                color_map = TAILWIND_COLORS.get(tw_match.group(1), {})
                hex_val = color_map.get(tw_match.group(2))
                if hex_val:
                    return hex_val
            if name.endswith("-black"):
                return "#000"
            if name.endswith("-white"):
                return "#fff"
            if any(kw in name for kw in ["background", "card", "surface", "bg"]):
                return "Canvas"
            if any(kw in name for kw in ["border", "divider", "separator"]):
                return "#ccc"
            if any(kw in name for kw in ["muted", "subtle", "secondary", "placeholder"]):
                return "#888"

        return "currentColor"

    for svg in list(svgs):
        svg_parent = svg.parent
        all_els = [svg] + list(svg.select("*"))
        for el in all_els:
            if not is_element(el):
                continue
            for attr_name in SVG_COLOR_ATTRS:
                val = el.get(attr_name)
                if not val or not isinstance(val, str):
                    continue
                if "var(" not in val and "light-dark(" not in val:
                    continue
                el[attr_name] = _resolve_var(val, svg_parent)
            style = el.get("style")
            if style and isinstance(style, str) and ("var(" in style or "light-dark(" in style):
                resolved = LIGHT_DARK_RE.sub(lambda m: m.group(1).strip(), style)
                resolved = re.sub(
                    r"var\(--[^,)]+(?:,\s*[^)]+)?\)",
                    lambda m: _resolve_var(m.group(0), svg_parent),
                    resolved,
                )
                el["style"] = resolved
            _resolve_tailwind_classes(el)
        _apply_svg_fallback_styles(svg)


def _has_style_prop(el: Tag, prop: str) -> bool:
    style = el.get("style", "")
    if not style or not isinstance(style, str):
        return False
    return bool(re.search(r"(?:^|;)\s*" + re.escape(prop) + r"\s*:", style))


def _apply_svg_fallback_styles(svg: Tag) -> None:
    if svg.select_one("style"):
        return

    all_els = list(svg.select("*"))

    has_unstyled = False
    for el in all_els:
        if not is_element(el):
            continue
        tag = el.name.lower() if el.name else ""
        if tag not in SVG_FILLED_TAGS:
            continue
        if not el.get("class"):
            continue
        if closest(el, SVG_NON_RENDERED_ANCESTOR):
            continue
        if el.get("fill") or _has_style_prop(el, "fill"):
            continue
        has_unstyled = True
        break

    if not has_unstyled:
        return

    for el in all_els:
        if not is_element(el):
            continue
        tag = el.name.lower() if el.name else ""
        is_filled = tag in SVG_FILLED_TAGS
        is_stroke = tag in SVG_STROKE_TAGS
        is_text = tag in SVG_TEXT_TAGS
        if not is_filled and not is_stroke and not is_text:
            continue
        if not el.get("class"):
            continue
        if closest(el, SVG_NON_RENDERED_ANCESTOR):
            continue

        if is_text:
            if not el.get("fill") and not _has_style_prop(el, "fill"):
                el["fill"] = "currentColor"
            continue

        has_fill = el.get("fill") and el.get("fill") != "none"
        has_stroke_attr = el.get("stroke") or _has_style_prop(el, "stroke")

        if is_filled and not el.get("fill") and not _has_style_prop(el, "fill"):
            el["fill"] = "none"

        if not has_stroke_attr:
            if is_stroke:
                el["stroke"] = "currentColor"
                if not el.get("stroke-opacity"):
                    el["stroke-opacity"] = GRIDLINE_STROKE_OPACITY
            elif is_filled and not has_fill:
                d = el.get("d", "")
                if d:
                    is_closed = bool(re.search(r"Z\s*$", d.strip(), re.IGNORECASE))
                else:
                    is_closed = False
                if not is_closed:
                    el["stroke"] = "currentColor"


def _resolve_tailwind_classes(el: Tag) -> None:
    class_name = el.get("class")
    if not class_name:
        return
    if isinstance(class_name, list):
        class_name = " ".join(class_name)

    tokens = class_name.split()
    keep: List[str] = []
    styles: List[str] = []

    for token in tokens:
        match = TW_COLOR_CLASS_RE.match(token)
        if match:
            prop, color, shade = match.group(1), match.group(2), match.group(3)
            opacity = match.group(4)
            hex_val = TAILWIND_COLORS.get(color, {}).get(shade)
            if hex_val:
                if opacity:
                    a = int(opacity) / 100
                    r = int(hex_val[1:3], 16)
                    g = int(hex_val[3:5], 16)
                    b = int(hex_val[5:7], 16)
                    el[prop] = f"rgba({r},{g},{b},{a})"
                else:
                    el[prop] = hex_val
                continue

        match = TW_SPECIAL_CLASS_RE.match(token)
        if match:
            el[match.group(1)] = TAILWIND_SPECIAL[match.group(2)]
            continue

        match = TW_ARBITRARY_RE.match(token)
        if (
            match
            and not match.group(1).startswith("#")
            and not match.group(1).startswith("rgb")
            and not match.group(1).startswith("hsl")
        ):
            styles.append(f"font-size:{match.group(1)}")
            continue

        if token == "font-semibold":
            styles.append("font-weight:600")
            continue
        if token == "font-bold":
            styles.append("font-weight:700")
            continue
        if token == "font-medium":
            styles.append("font-weight:500")
            continue
        if token == "font-mono":
            styles.append("font-family:monospace")
            continue

        keep.append(token)

    if len(keep) == len(tokens):
        return

    if keep:
        el["class"] = " ".join(keep)
    elif "class" in el.attrs:
        del el["class"]

    if styles:
        existing = el.get("style", "") or ""
        sep = ";" if existing and not existing.endswith(";") else ""
        el["style"] = existing + sep + ";".join(styles)


def remove_empty_elements(element: Tag) -> None:
    removed_count = 0

    def _is_empty(el: Tag) -> bool:
        tag = el.name.lower() if el.name else ""
        if tag in ALLOWED_EMPTY_ELEMENTS:
            return False

        if tag == "div":
            children = list(el.children)
            child_elements = [c for c in children if is_element(c)]
            if child_elements:
                all_comma_spans = True
                for child in child_elements:
                    if child.name != "span":
                        all_comma_spans = False
                        break
                    content = child.get_text().strip()
                    if content not in (",", "", " "):
                        all_comma_spans = False
                        break
                if all_comma_spans:
                    return True

        text_content = el.get_text()
        if text_content.strip() or "\xa0" in text_content:
            return False

        if not list(el.children):
            return True
        for node in list(el.children):
            if is_element(node) and node.name and node.name.lower() == "br":
                continue
            if not is_text_node(node):
                return False
            node_text = str(node)
            if node_text.strip() or "\xa0" in node_text:
                return False
        return True

    all_elements = list(element.select("*"))
    all_elements.reverse()
    for el in all_elements:
        if el.parent is not None and _is_empty(el):
            el.decompose()
            removed_count += 1

    log_debug(_debug, "Removed empty elements:", removed_count)


def _skip_whitespace(node: Any, direction: str) -> Any:
    if direction == "previous":
        sibling = node.previous_sibling
    else:
        sibling = node.next_sibling
    while sibling is not None and is_text_node(sibling) and not str(sibling).strip():
        if direction == "previous":
            sibling = sibling.previous_sibling
        else:
            sibling = sibling.next_sibling
    return sibling


def strip_extra_br_elements(element: Tag) -> None:
    processed_count = 0

    br_elements = list(element.select("br"))
    consecutive_brs: List[Tag] = []

    def _process_brs() -> None:
        nonlocal processed_count
        if len(consecutive_brs) > 2:
            for i in range(2, len(consecutive_brs)):
                consecutive_brs[i].decompose()
                processed_count += 1

    for current_node in br_elements:
        is_consecutive = False
        if consecutive_brs:
            last_br = consecutive_brs[-1]
            if _skip_whitespace(current_node, "previous") is last_br:
                is_consecutive = True
        if is_consecutive:
            consecutive_brs.append(current_node)
        else:
            _process_brs()
            consecutive_brs = [current_node]

    _process_brs()

    remaining_brs = list(element.select("br"))

    for br in remaining_brs:
        parent = br.parent
        if parent is None:
            continue
        if closest(br, "pre, code"):
            continue

        parent_tag = parent.name.lower() if parent.name else ""

        if parent_tag in BLOCK_LEVEL_ELEMENTS or parent_tag == "body":
            group: List[Tag] = [br]
            scan = _skip_whitespace(br, "next")
            while scan is not None and is_element(scan) and scan.name and scan.name.lower() == "br":
                group.append(scan)
                scan = _skip_whitespace(scan, "next")

            prev_node = _skip_whitespace(group[0], "previous")
            next_node = _skip_whitespace(group[-1], "next")
            prev_is_block = (
                prev_node is not None
                and is_element(prev_node)
                and prev_node.name
                and prev_node.name.lower() in BLOCK_LEVEL_ELEMENTS
            )
            next_is_block = (
                next_node is not None
                and is_element(next_node)
                and next_node.name
                and next_node.name.lower() in BLOCK_LEVEL_ELEMENTS
            )

            if (prev_is_block and next_is_block) or (prev_is_block and not next_node) or not prev_node:
                for b in group:
                    b.decompose()
                    processed_count += 1
                continue

        if parent_tag in BLOCK_LEVEL_ELEMENTS:
            if not _skip_whitespace(br, "next"):
                br.decompose()
                processed_count += 1


def _move_whitespace_outside(node: Tag, soup: BeautifulSoup, direction: str) -> int:
    if direction == "leading":
        child = node.contents[0] if node.contents else None
    else:
        child = node.contents[-1] if node.contents else None
    if child is None or not is_text_node(child):
        return 0

    text = str(child)
    if direction == "leading":
        trimmed = re.sub(r"^\s+", "", text)
    else:
        trimmed = re.sub(r"\s+$", "", text)
    if trimmed == text or node.parent is None:
        return 0

    child.replace_with(NavigableString(trimmed))

    if direction == "leading":
        neighbor = node.previous_sibling
        neighbor_has_space = neighbor is not None and is_text_node(neighbor) and str(neighbor).endswith(" ")
    else:
        neighbor = node.next_sibling
        neighbor_has_space = neighbor is not None and is_text_node(neighbor) and str(neighbor).startswith(" ")

    if not neighbor_has_space:
        space = NavigableString(" ")
        if direction == "leading":
            node.insert_before(space)
        else:
            node.insert_after(space)

    return 1


def remove_empty_lines(element: Tag, doc: Any) -> None:
    removed_count = 0

    def _remove_empty_text_nodes(node: Any) -> None:
        nonlocal removed_count
        if is_element(node):
            tag = node.name.lower() if node.name else ""
            if tag in ("pre", "code"):
                return

        children = list(node.children) if hasattr(node, "children") else []
        for child in children:
            _remove_empty_text_nodes(child)

        if is_text_node(node):
            text = str(node)
            if not text or re.match(r"^[\u200c\u200b\u200d\u200e\u200f\ufeff]*$", text):
                node.extract()
                removed_count += 1
            else:
                new_text = text.replace("\n", " ").replace("\r", "")
                new_text = re.sub(r"\t+", " ", new_text)
                new_text = re.sub(r" {2,}", " ", new_text)
                new_text = re.sub(r"^[ ]+$", " ", new_text)
                new_text = re.sub(r"\s+([,.!?:;])", r"\1", new_text)
                new_text = re.sub(r"[\u200b\u200d\u200e\u200f\ufeff]+", "", new_text)
                new_text = re.sub(r"(?:\xa0){2,}", "\xa0", new_text)

                if new_text != text:
                    node.replace_with(NavigableString(new_text))
                    removed_count += len(text) - len(new_text)

    def _cleanup_empty_elements(node: Any) -> None:
        nonlocal removed_count
        if not is_element(node):
            return

        tag = node.name.lower() if node.name else ""
        if tag in ("pre", "code"):
            return

        for child in list(node.children):
            if is_element(child):
                _cleanup_empty_elements(child)

        _normalize(node)

        computed = get_computed_style(node)
        is_block_element = computed.get("display") == "block"

        if is_block_element:
            ws_pattern = re.compile(r"^[\n\r\t \u200c\u200b\u200d\u200e\u200f\ufeff\xa0]*$")
        else:
            ws_pattern = re.compile(r"^[\n\r\t\u200c\u200b\u200d\u200e\u200f\ufeff]*$")

        while node.contents:
            first = node.contents[0]
            if is_text_node(first) and ws_pattern.match(str(first)):
                first.extract()
                removed_count += 1
            else:
                break

        while node.contents:
            last = node.contents[-1]
            if is_text_node(last) and ws_pattern.match(str(last)):
                last.extract()
                removed_count += 1
            else:
                break

        if not is_block_element and tag in INLINE_ELEMENTS and node.parent:
            soup = _get_soup(node)
            removed_count += _move_whitespace_outside(node, soup, "leading")
            removed_count += _move_whitespace_outside(node, soup, "trailing")

        if not is_block_element:
            children = list(node.contents)
            for i in range(len(children) - 1):
                current = children[i]
                nxt = children[i + 1]
                if is_element(current) or is_element(nxt):
                    next_content = nxt.get_text() if is_element(nxt) else str(nxt)
                    current_content = current.get_text() if is_element(current) else str(current)
                    next_starts_punct = bool(re.match(r"^[,.!?:;)\]]", next_content))
                    current_ends_punct = bool(re.search(r"[,.!?:;(\[]\s*$", current_content))
                    has_space = (is_text_node(current) and str(current).endswith(" ")) or (
                        is_text_node(nxt) and str(nxt).startswith(" ")
                    )
                    if not next_starts_punct and not current_ends_punct and not has_space:
                        space = NavigableString(" ")
                        nxt.insert_before(space)

    _remove_empty_text_nodes(element)
    _cleanup_empty_elements(element)


def standardize_elements(element: Tag, doc: Any, sub_profile: Optional[Dict[str, float]] = None) -> None:
    processed_count = 0

    def step_se(name: str, fn: Callable) -> Any:
        nonlocal sub_profile
        if sub_profile is not None:
            t = time.perf_counter()
            r = fn()
            elapsed = (time.perf_counter() - t) * 1000
            key = "se:" + name
            sub_profile[key] = (sub_profile.get(key) or 0) + round(elapsed)
            return r
        else:
            return fn()

    step_se("wrapRawLatexDelimiters", lambda: _wrap_raw_latex_delimiters(element, doc))

    def _convert_latex_images() -> None:
        nonlocal processed_count
        for img in list(element.select("img[src]")):
            src = img.get("src", "")
            if not src:
                continue
            latex = _extract_latex_from_image_src(src)
            if not latex:
                alt = img.get("alt", "") or ""
                if alt and _looks_like_latex(alt):
                    latex = alt
            if not latex:
                continue
            is_block = bool(re.search(r"\\begin\{", latex))
            if not is_block:
                parent = img.parent
                if parent and parent.name == "p" and len(list(parent.children)) == 1:
                    is_block = True
            soup = _get_soup(img)
            math_el = _create_clean_math_el(latex, is_block, soup)
            img.replace_with(math_el)
            processed_count += 1

    step_se("convertLatexImages", _convert_latex_images)

    for rule in _ELEMENT_STANDARDIZATION_RULES:
        selector = rule["selector"]
        selector_key = selector[:30]

        def _apply_rule(sel: str = selector, r: dict = rule) -> None:
            nonlocal processed_count
            fast_check = r.get("fast_check")
            if fast_check and not element.select_one(fast_check):
                return
            try:
                els = list(element.select(sel))
            except Exception:
                return
            for el in els:
                transform = r.get("transform")
                if transform:
                    transformed = transform(el, doc)
                    el.replace_with(transformed)
                    processed_count += 1

        step_se(selector_key, _apply_rule)

    for pre in list(element.select("code > pre")):
        outer_code = pre.parent
        if outer_code is None or outer_code.name != "code":
            continue
        outer_code.replace_with(pre.extract())

    equation_tables = list(element.select("table.ltx_equation, table.ltx_eqn_table, table.ltx_equationgroup"))
    for table in equation_tables:
        math_elements = table.select("math")
        if not math_elements:
            continue
        soup = _get_soup(table)
        frag_container = soup.new_tag("div")
        for math_el in math_elements:
            alttext = math_el.get("alttext", "")
            annotation = math_el.select_one('annotation[encoding="application/x-tex"]')
            latex = alttext or (annotation.get_text().strip() if annotation else "")
            if not latex:
                continue
            is_block = (
                math_el.get("display") == "block"
                or _has_class(table, "ltx_equation")
                or _has_class(table, "ltx_equationgroup")
            )
            clean_math = soup.new_tag("math")
            clean_math["xmlns"] = "http://www.w3.org/1998/Math/MathML"
            clean_math["display"] = "block" if is_block else "inline"
            clean_math["data-latex"] = latex
            clean_math.string = latex
            frag_container.append(clean_math)
        children = list(frag_container.children)
        if children:
            for child in children:
                table.insert_before(child.extract())
            table.decompose()
            processed_count += 1

    note_outers = list(element.select("span.ltx_note_outer"))
    for outer in note_outers:
        outer.decompose()
        processed_count += 1

    ref_links = list(element.select("a.ltx_ref"))
    for link in ref_links:
        ref_tag = link.select_one("span.ltx_ref_tag, span.ltx_text.ltx_ref_tag")
        if ref_tag:
            text = NavigableString(link.get_text())
            link.replace_with(text)
            processed_count += 1

    for table in list(element.select("table")):
        if table.parent is None:
            continue
        cells = table.select("td, th")
        if (
            cells
            and all(not cell.get_text().strip() for cell in cells)
            and not table.select_one("img, picture, video, audio, iframe, svg, math")
        ):
            table.decompose()
            processed_count += 1

    tables = list(element.select("table"))
    for table in tables:
        if table.parent is None:
            return
        direct_cells = [cell for cell in table.select("td, th") if is_direct_table_child(cell, table)]
        if any(cell.name == "th" for cell in direct_cells):
            continue
        direct_rows = [row for row in table.select("tr") if is_direct_table_child(row, table)]
        if not direct_rows:
            continue
        is_single_column = all(sum(1 for cell in direct_cells if cell.parent is tr) <= 1 for tr in direct_rows)
        if not is_single_column:
            continue
        for cell in direct_cells:
            children = list(cell.children)
            for child in reversed(children):
                table.insert_before(child.extract())
        table.decompose()
        processed_count += 1

    for el in element.select("video:not([controls])"):
        el["controls"] = ""

    for el in list(element.select("lite-youtube")):
        video_id = el.get("videoid")
        if not video_id:
            continue
        soup = _get_soup(el)
        iframe = soup.new_tag(
            "iframe",
            attrs={
                "width": "560",
                "height": "315",
                "src": f"https://www.youtube.com/embed/{video_id}",
                "title": el.get("videotitle", "YouTube video player"),
                "frameborder": "0",
                "allow": "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share",
                "allowfullscreen": "",
            },
        )
        el.replace_with(iframe)
        processed_count += 1

    log_debug(_debug, "Converted embedded elements:", processed_count)

    merge_adjacent_verso_code_blocks(element)


def _wrap_raw_latex_delimiters(element: Tag, doc: Any) -> None:
    pass


def _extract_latex_from_image_src(src: str) -> str:
    return ""


def _looks_like_latex(text: str) -> bool:
    return bool(re.search(r"\\[a-zA-Z]+", text))


def _create_clean_math_el(latex: str, is_block: bool, soup: BeautifulSoup) -> Tag:
    math_el = soup.new_tag("math")
    math_el["display"] = "block" if is_block else "inline"
    math_el["data-latex"] = latex
    math_el.string = latex
    return math_el


def _has_class(el: Tag, cls: str) -> bool:
    classes = el.get("class", [])
    if isinstance(classes, list):
        return cls in classes
    return cls in str(classes).split()


def _transform_paragraph_role(el: Tag, doc: Tag) -> Tag:
    soup = BeautifulSoup("", "lxml")
    p = soup.new_tag("p")
    transfer_content(el, p)
    for attr_name in list(el.attrs.keys()):
        if attr_name in ALLOWED_ATTRIBUTES:
            p[attr_name] = el[attr_name]
    return p


def _transform_list_role(el: Tag, doc: Tag) -> Tag:
    soup = BeautifulSoup("", "lxml")
    first_item = el.select_one('div[role="listitem"] .label')
    label = first_item.get_text().strip() if first_item else ""
    is_ordered = bool(re.match(r"^\d+\)", label))
    list_el = soup.new_tag("ol" if is_ordered else "ul")

    items = el.select('div[role="listitem"]')
    for item in items:
        li = soup.new_tag("li")
        content = item.select_one(".content")
        if content:
            for div in content.select('div[role="paragraph"]'):
                p = soup.new_tag("p")
                transfer_content(div, p)
                div.replace_with(p)
            for nested_list in content.select('div[role="list"]'):
                n_first = nested_list.select_one('div[role="listitem"] .label')
                n_label = n_first.get_text().strip() if n_first else ""
                n_ordered = bool(re.match(r"^\d+\)", n_label))
                n_list = soup.new_tag("ol" if n_ordered else "ul")
                for n_item in nested_list.select('div[role="listitem"]'):
                    n_li = soup.new_tag("li")
                    n_content = n_item.select_one(".content")
                    if n_content:
                        for n_div in n_content.select('div[role="paragraph"]'):
                            n_p = soup.new_tag("p")
                            transfer_content(n_div, n_p)
                            n_div.replace_with(n_p)
                        transfer_content(n_content, n_li)
                    n_list.append(n_li)
                nested_list.replace_with(n_list)
            transfer_content(content, li)
        list_el.append(li)
    return list_el


def _transform_listitem_role(el: Tag, doc: Tag) -> Tag:
    content = el.select_one(".content")
    if not content:
        return el
    for div in content.select('div[role="paragraph"]'):
        soup = BeautifulSoup("", "lxml")
        p = soup.new_tag("p")
        transfer_content(div, p)
        div.replace_with(p)
    return content


_ELEMENT_STANDARDIZATION_RULES: List[Dict[str, Any]] = [
    *math_rules,
    *code_block_rules,
    *heading_rules,
    *image_rules,
    {
        "selector": 'div[data-testid^="paragraph"], div[role="paragraph"]',
        "element": "p",
        "transform": _transform_paragraph_role,
    },
    {
        "selector": 'div[role="list"]',
        "element": "ul",
        "transform": _transform_list_role,
    },
    {
        "selector": 'div[role="listitem"]',
        "element": "li",
        "transform": _transform_listitem_role,
    },
]


def merge_adjacent_verso_code_blocks(root: Tag) -> None:
    def _get_code_node(pre: Tag) -> Optional[Tag]:
        code: Optional[Tag] = None
        for child in pre.children:
            if not is_element(child):
                continue
            if child.name and child.name.lower() != "code":
                return None
            if code is not None:
                return None
            code = child
        return code

    def _get_language(code: Tag) -> str:
        data_lang = (code.get("data-lang", "") or "").lower()
        if data_lang:
            return data_lang
        class_name = code.get("class", "")
        if isinstance(class_name, list):
            class_name = " ".join(class_name)
        match = re.search(r"(?:^|\s)language-([a-z0-9_+-]+)(?:\s|$)", class_name, re.IGNORECASE)
        return match.group(1).lower() if match else ""

    candidates = root.select('pre[data-verso-code="true"]')
    parents: Set[Tag] = set()
    for candidate in candidates:
        if candidate.parent is not None:
            parents.add(candidate.parent)

    for container in parents:
        children = list(container.children)
        i = 0
        while i < len(children):
            start_node = children[i]
            if not is_element(start_node) or start_node.name != "pre":
                i += 1
                continue
            if start_node.get("data-verso-code") != "true":
                i += 1
                continue
            start_code = _get_code_node(start_node)
            if not start_code:
                i += 1
                continue
            language = _get_language(start_code)
            if language not in ("lean", "lean4"):
                i += 1
                continue

            run: List[Tuple[Tag, Tag]] = [(start_node, start_code)]
            between_whitespace: List[Any] = []
            j = i + 1

            while j < len(children):
                node = children[j]
                if is_text_node(node) and not str(node).strip():
                    between_whitespace.append(node)
                    j += 1
                    continue
                if not is_element(node) or node.name != "pre":
                    break
                if node.get("data-verso-code") != "true":
                    break
                code = _get_code_node(node)
                if not code or _get_language(code) != language:
                    break
                run.append((node, code))
                j += 1

            if len(run) <= 1:
                i += 1
                continue

            merged = "\n".join(re.sub(r"\r?\n$", "", code.get_text()) for _, code in run)
            merged = re.sub(r"\n{3,}", "\n\n", merged)
            merged = re.sub(r"^\n+|\n+$", "", merged)

            start_code.clear()
            start_code.append(NavigableString(merged))

            for k in range(1, len(run)):
                run[k][0].decompose()
            for ws_node in between_whitespace:
                ws_node.extract()

            i = j
        pass


def flatten_wrapper_elements(element: Tag, doc: Any) -> None:
    processed_count = 0

    def _has_direct_inline_content(el: Tag) -> bool:
        for child in el.children:
            if is_text_node(child) and str(child).strip():
                return True
            if is_element(child) and child.name and child.name.lower() in INLINE_ELEMENTS:
                return True
        return False

    def _should_preserve(el: Tag) -> bool:
        tag = el.name.lower() if el.name else ""
        if is_svg_element(el):
            return True
        if tag in PRESERVE_ELEMENTS:
            return True
        if el.get("data-callout") or closest(el, "[data-callout]"):
            return True
        role = el.get("role", "")
        if role and role in ("article", "main", "navigation", "banner", "contentinfo"):
            return True
        class_name = get_class_name(el)
        if class_name and re.search(
            r"(?:article|main|content|footnote|reference|bibliography)", class_name, re.IGNORECASE
        ):
            return True
        children = list(el.children)
        child_elements = [c for c in children if is_element(c)]
        has_preserved = any(
            (c.name and c.name.lower() in PRESERVE_ELEMENTS)
            or c.get("role") == "article"
            or (
                get_class_name(c)
                and re.search(
                    r"(?:article|main|content|footnote|reference|bibliography)", get_class_name(c), re.IGNORECASE
                )
            )
            for c in child_elements
        )
        if has_preserved:
            return True
        return False

    def _is_wrapper(el: Tag) -> bool:
        if _has_direct_inline_content(el):
            return False
        if not el.get_text().strip():
            return True
        child_elements = [c for c in el.children if is_element(c)]
        if not child_elements:
            return True
        all_block = all(c.name and c.name.lower() in BLOCK_LEVEL_ELEMENTS for c in child_elements)
        if all_block:
            return True
        class_name = get_class_name(el).lower()
        if re.search(r"(?:wrapper|container|layout|row|col|grid|flex|outer|inner|content-area)", class_name):
            return True
        text_nodes = [n for n in el.children if is_text_node(n) and str(n).strip()]
        if not text_nodes:
            return True
        has_only_block = len(child_elements) > 0 and not any(
            c.name and c.name.lower() in INLINE_ELEMENTS for c in child_elements
        )
        if has_only_block:
            return True
        return False

    def _process(el: Tag) -> bool:
        nonlocal processed_count
        if el.parent is None or _should_preserve(el):
            return False
        tag = el.name.lower() if el.name else ""

        if tag not in ALLOWED_EMPTY_ELEMENTS and not list(el.children):
            if not el.get_text().strip():
                el.decompose()
                processed_count += 1
                return True

        if el.parent is element:
            child_elements = [c for c in el.children if is_element(c)]
            has_only_block = len(child_elements) > 0 and not any(
                c.name and c.name.lower() in INLINE_ELEMENTS for c in child_elements
            )
            if has_only_block:
                children = list(el.children)
                for child in reversed(children):
                    el.insert_before(child.extract())
                el.decompose()
                processed_count += 1
                return True

        if _is_wrapper(el):
            children = list(el.children)
            for child in reversed(children):
                el.insert_before(child.extract())
            el.decompose()
            processed_count += 1
            return True

        child_nodes = list(el.children)
        has_only_inline_or_text = len(child_nodes) > 0 and all(
            is_text_node(c) or (is_element(c) and c.name and c.name.lower() in INLINE_ELEMENTS) for c in child_nodes
        )

        if has_only_inline_or_text and el.get_text().strip():
            soup = _get_soup(el)
            p = soup.new_tag("p")
            children = list(el.children)
            for child in children:
                p.append(child.extract())
            el.replace_with(p)
            processed_count += 1
            return True

        child_elements = [c for c in el.children if is_element(c)]
        if len(child_elements) == 1:
            child = child_elements[0]
            child_tag = child.name.lower() if child.name else ""
            if child_tag in BLOCK_ELEMENTS_SET and not _should_preserve(child):
                el.replace_with(child.extract())
                processed_count += 1
                return True

        nesting_depth = 0
        parent = el.parent
        while parent is not None:
            if is_element(parent) and parent.name and parent.name.lower() in BLOCK_ELEMENTS_SET:
                nesting_depth += 1
            parent = parent.parent

        if nesting_depth > 0 and not _has_direct_inline_content(el):
            children = list(el.children)
            for child in reversed(children):
                el.insert_before(child.extract())
            el.decompose()
            processed_count += 1
            return True

        return False

    def _process_top_level() -> bool:
        top_elements = [
            el for el in element.children if is_element(el) and el.name and el.name.lower() in BLOCK_ELEMENTS_SET
        ]
        modified = False
        for el in top_elements:
            if _process(el):
                modified = True
        return modified

    def _get_depth(el: Tag) -> int:
        depth = 0
        parent = el.parent
        while parent is not None:
            if is_element(parent) and parent.name and parent.name.lower() in BLOCK_ELEMENTS_SET:
                depth += 1
            parent = parent.parent
        return depth

    def _process_remaining() -> bool:
        all_elements = list(element.select(BLOCK_ELEMENTS_SELECTOR))
        all_elements.sort(key=lambda e: _get_depth(e), reverse=True)
        modified = False
        for el in all_elements:
            if _process(el):
                modified = True
        return modified

    def _final_cleanup() -> bool:
        nonlocal processed_count
        remaining = list(element.select(BLOCK_ELEMENTS_SELECTOR))
        modified = False
        for el in remaining:
            child_elements = [c for c in el.children if is_element(c)]
            only_paragraphs = len(child_elements) > 0 and all(c.name == "p" for c in child_elements)
            if only_paragraphs or (not _should_preserve(el) and _is_wrapper(el)):
                children = list(el.children)
                for child in reversed(children):
                    el.insert_before(child.extract())
                el.decompose()
                processed_count += 1
                modified = True
        return modified

    keep_processing = True
    while keep_processing:
        keep_processing = False
        if _process_top_level():
            keep_processing = True
        if _process_remaining():
            keep_processing = True
        if _final_cleanup():
            keep_processing = True

    log_debug(_debug, "Flattened wrapper elements:", processed_count)


def _normalize(element: Tag) -> None:
    if not isinstance(element, Tag):
        return
    try:
        element.smooth()
    except (AttributeError, TypeError):
        pass
    except Exception:
        pass
