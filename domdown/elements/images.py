from __future__ import annotations

import base64
import re
from typing import List, Optional, Set

from bs4 import BeautifulSoup, Tag

from domdown.utils.dom import get_class_name

ALLOWED_IMAGE_TYPES: Set[str] = {"image/png", "image/webp", "image/gif", "image/svg+xml", "image/jpeg"}
DATA_IMAGE_PATTERN = re.compile(r"^data:image/(\w+);base64,")
SRC_Width_PATTERN = re.compile(r"(?:width[=:/]|[/,?&]w[_:=])(\d+)")


def _is_valid_image_type(mime_type: str) -> bool:
    return mime_type in ALLOWED_IMAGE_TYPES


def _get_soup(el: Tag) -> BeautifulSoup:
    node = el
    while node.parent is not None:
        node = node.parent
    if isinstance(node, BeautifulSoup):
        return node
    return BeautifulSoup("", "lxml")


def _contains_image(el: Tag) -> bool:
    return bool(el.select_one("img, picture, video, iframe, svg"))


def _find_main_image(el: Tag) -> Optional[Tag]:
    picture = el.select_one("picture")
    if picture:
        img = picture.select_one("img")
        if img:
            return img
        sources = picture.select("source")
        for source in sources:
            srcset = source.get("srcset", "")
            if srcset:
                return picture.extract() or None
        return None
    return el.select_one("img")


def _find_caption(el: Tag) -> Optional[Tag]:
    for selector in ["figcaption", '[class*="caption"]', '[class*="Caption"]']:
        caption = el.select_one(selector)
        if caption:
            return caption
    return None


def _has_meaningful_caption(caption: Tag) -> bool:
    text = caption.get_text().strip()
    return len(text) > 10 and not re.match(r"^(?:image|photo|picture|fig\.?\s*\d+)\s*$", text, re.IGNORECASE)


def _process_image_element(img: Tag, soup: BeautifulSoup) -> Tag:
    new_img = soup.new_tag("img")
    for attr in ["src", "srcset", "alt", "title", "width", "height", "loading"]:
        val = img.get(attr)
        if val is not None:
            new_img[attr] = val
    return new_img


def _create_figure_with_caption(img: Tag, caption: Tag, soup: BeautifulSoup) -> Tag:
    fig = soup.new_tag("figure")
    fig.append(img)
    fig.append(caption)
    return fig


def _transform_picture(el: Tag, doc: Tag) -> Tag:
    try:
        source_elements = list(el.select("source"))
        img_element = el.select_one("img")

        if not img_element:
            for source in source_elements:
                srcset = source.get("srcset", "")
                if srcset:
                    best_url = _extract_first_url(srcset)
                    if best_url:
                        new_img = doc.new_tag("img")
                        new_img["src"] = best_url
                        for child in list(el.children):
                            if hasattr(child, "name") and child.name != "source":
                                continue
                            child.decompose()
                        el.append(new_img)
                        return el
            return el

        for source in source_elements:
            srcset = source.get("srcset", "")
            if srcset:
                best_url = _extract_first_url(srcset)
                if best_url and _is_valid_url(best_url):
                    if not img_element.get("src") or not _is_valid_url(img_element.get("src", "")):
                        img_element["src"] = best_url
                srcset_val = source.get("srcset")
                if srcset_val:
                    img_element["srcset"] = srcset_val
            source.decompose()

        if not img_element.get("src") or not _is_valid_url(img_element.get("src", "")):
            srcset = img_element.get("srcset", "")
            if srcset:
                url = _extract_first_url(srcset)
                if url and _is_valid_url(url):
                    img_element["src"] = url

        return el
    except Exception:
        return el


def _transform_uni_image(el: Tag, doc: Tag) -> Tag:
    try:
        if not _contains_image(el):
            return el
        img = el.select_one("img")
        if not img:
            return el
        src = img.get("src", "")
        if src.startswith("data:image/svg+xml"):
            match = DATA_IMAGE_PATTERN.match(src)
            if match:
                svg_data = src.split(",", 1)
                if len(svg_data) > 1:
                    try:
                        decoded = base64.b64decode(svg_data[1])
                        svg_text = decoded.decode("utf-8", errors="replace")
                        if "<svg" in svg_text:
                            new_soup = BeautifulSoup(svg_text, "lxml")
                            svg_el = new_soup.find("svg")
                            if svg_el:
                                for attr, val in list(img.attrs.items()):
                                    if attr not in ("src", "srcset"):
                                        svg_el[attr] = val
                                return svg_el
                    except Exception:
                        pass
        return el
    except Exception:
        return el


def _transform_lazy_img(el: Tag, doc: Tag) -> Tag:
    try:
        src = el.get("src", "")
        data_src = el.get("data-src", "")
        data_srcset = el.get("data-srcset", "")
        srcset = el.get("srcset", "")
        loading = el.get("loading", "")

        is_lazy = (
            data_src
            or data_srcset
            or loading == "lazy"
            or bool(re.search(r"lazy(load|ed)?", get_class_name(el), re.IGNORECASE))
            or src.startswith("data:image/svg+xml")
        )

        if not is_lazy:
            return el

        best_src = data_src or src
        best_srcset = data_srcset or srcset

        if best_src and best_src != src:
            el["src"] = best_src
            if data_src:
                del el["data-src"]

        if best_srcset and best_srcset != srcset:
            el["srcset"] = best_srcset
            if data_srcset:
                del el["data-srcset"]

        if "loading" in el.attrs:
            del el["loading"]

        return el
    except Exception:
        return el


def _transform_span_with_img(el: Tag, doc: Tag) -> Tag:
    try:
        if not _contains_image(el):
            return el
        img = _find_main_image(el)
        if not img:
            return el
        return img
    except Exception:
        return el


def _transform_figure(el: Tag, doc: Tag) -> Tag:
    try:
        if not _contains_image(el):
            return el

        img_element = _find_main_image(el)
        if not img_element:
            return el

        caption = _find_caption(el)

        if caption and _has_meaningful_caption(caption):
            current_img = _find_main_image(el)
            soup = _get_soup(el)
            if current_img:
                image_to_add = current_img
            else:
                image_to_add = _process_image_element(img_element, soup)
            return _create_figure_with_caption(image_to_add, caption, soup)
        else:
            return el
    except Exception:
        return el


def _extract_first_url(srcset: str) -> Optional[str]:
    if not srcset:
        return None
    entries = srcset.split(",")
    for entry in entries:
        parts = entry.strip().split()
        if parts:
            return parts[0]
    return None


def _is_valid_url(url: str) -> bool:
    if not url:
        return False
    if url.startswith("data:"):
        match = DATA_IMAGE_PATTERN.match(url)
        if match:
            return _is_valid_image_type(f"image/{match.group(1)}")
        return False
    if url.startswith("javascript:") or url.startswith("data:text/html"):
        return False
    return True


image_rules: List[dict] = [
    {
        "selector": "picture",
        "element": "picture",
        "transform": _transform_picture,
    },
    {
        "selector": "uni-image-full-width",
        "element": "figure",
        "transform": _transform_uni_image,
    },
    {
        "selector": 'img[data-src], img[data-srcset], img[loading="lazy"], img.lazy, img.lazyload, img[src^="data:image/svg+xml"]',
        "element": "img",
        "transform": _transform_lazy_img,
    },
    {
        "selector": "span:has(img)",
        "element": "span",
        "transform": _transform_span_with_img,
    },
    {
        "selector": 'figure, p:has([class*="caption"])',
        "element": "figure",
        "transform": _transform_figure,
    },
]
