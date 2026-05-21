from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional, Union

import soupsieve as sv
from bs4 import BeautifulSoup, NavigableString, Tag

from domdown.utils import get_class_name, is_element, is_text_node
from domdown.utils.dom import closest, parse_html, transfer_content

_MATH_SELECTORS = ", ".join(
    [
        'img.latex[src*="latex.php"]',
        "span.MathJax",
        "mjx-container",
        'script[type="math/tex"]',
        'script[type="math/tex; mode=display"]',
        '.MathJax_Preview + script[type="math/tex"]',
        ".MathJax_Display",
        ".MathJax_SVG",
        ".MathJax_MathML",
        ".mwe-math-element",
        ".mwe-math-fallback-image-inline",
        ".mwe-math-fallback-image-display",
        ".mwe-math-mathml-inline",
        ".mwe-math-mathml-display",
        ".katex",
        ".katex-display",
        ".katex-mathml",
        ".katex-html",
        "[data-katex]",
        'script[type="math/katex"]',
        "math",
        "[data-math]",
        "[data-latex]",
        "[data-tex]",
        'script[type^="math/"]',
        'annotation[encoding="application/x-tex"]',
    ]
)

MATH_FAST_CHECK = 'math, mjx-container, .MathJax, .katex, img.latex, [data-math], [data-latex], script[type^="math/"]'

LOOKS_LIKE_LATEX_RE = re.compile(r"\\[a-zA-Z]{2,}")

_LATEX_PARAM_REGEXES = [
    re.compile(r"[?&]" + param + r"=([^&#]+)", re.IGNORECASE) for param in ("latex", "chl", "tex", "eq", "math")
]

_LATEX_DELIM_RE = re.compile(r"\$\$([\s\S]+?)\$\$|\\\[([\s\S]+?)\\\]|\$([^\s$][^$]*[^\s$]|[^\s$])\$|\\\(([\s\S]+?)\\\)")
_LATEX_CMD_RE = re.compile(r"\\[a-zA-Z]")
_LATEX_STRUCT_RE = re.compile(r"[_^{}]")
_RAW_LATEX_SKIP_TAGS = frozenset(["pre", "code", "script", "style", "math", "svg", "textarea"])


@dataclass
class MathData:
    mathml: str
    latex: Optional[str]
    is_block: bool


def _decode_latex(raw: str) -> Optional[str]:
    try:
        from urllib.parse import unquote_plus

        decoded = unquote_plus(raw)
        return decoded if LOOKS_LIKE_LATEX_RE.search(decoded) else None
    except Exception:
        return None


def extract_latex_from_image_src(src: str) -> Optional[str]:
    for re_pat in _LATEX_PARAM_REGEXES:
        m = re_pat.search(src)
        if m:
            latex = _decode_latex(m.group(1))
            if latex:
                return latex

    query_match = re.search(r"\?([^#]+)", src)
    if query_match:
        latex = _decode_latex(query_match.group(1))
        if latex:
            return latex

    path_part = src.split("?")[0]
    segments = path_part.split("/")
    for seg in reversed(segments):
        if re.search(r"%5[Cc]", seg):
            latex = _decode_latex(seg)
            if latex:
                return latex

    return None


def _get_mathml_from_element(el: Tag) -> Optional[MathData]:
    if el.name == "math":
        is_block = el.get("display") == "block"
        mathml = str(el)
        latex = el.get("alttext") or None
        return MathData(mathml=mathml, latex=latex, is_block=is_block)

    mathml_str = el.get("data-mathml")
    if mathml_str:
        fragment = parse_html(mathml_str)
        math_element = fragment.select_one("math")
        if math_element:
            is_block = math_element.get("display") == "block"
            return MathData(
                mathml=str(math_element),
                latex=math_element.get("alttext") or None,
                is_block=is_block,
            )

    assistive = el.select_one(".MJX_Assistive_MathML, mjx-assistive-mml")
    if assistive:
        math_element = assistive.select_one("math")
        if math_element:
            math_display = math_element.get("display")
            container_display = assistive.get("display")
            is_block = math_display == "block" or container_display == "block"
            return MathData(
                mathml=str(math_element),
                latex=math_element.get("alttext") or None,
                is_block=is_block,
            )

    katex_mathml = el.select_one(".katex-mathml math")
    if katex_mathml:
        return MathData(mathml=str(katex_mathml), latex=None, is_block=False)

    return None


def _get_basic_latex_from_element(el: Tag) -> Optional[str]:
    data_latex = el.get("data-latex")
    if data_latex:
        return data_latex
    data_math = el.get("data-math")
    if data_math:
        return data_math

    if el.name == "img" and "latex" in (el.get("class", []) or []):
        alt = el.get("alt")
        if alt:
            return alt
        src = el.get("src", "")
        if src:
            m = re.search(r"latex\.php\?latex=([^&]+)", src)
            if m:
                from urllib.parse import unquote

                return unquote(m.group(1)).replace("+", " ").replace("%5C", "\\")

    annotation = el.select_one('annotation[encoding="application/x-tex"]')
    if annotation and annotation.get_text().strip():
        return annotation.get_text().strip()

    try:
        if sv.match(".katex", el):
            katex_ann = el.select_one('.katex-mathml annotation[encoding="application/x-tex"]')
            if katex_ann and katex_ann.get_text().strip():
                return katex_ann.get_text().strip()
    except Exception:
        pass

    el_type = el.get("type", "")
    if el_type in ("math/tex", "math/tex; mode=display"):
        text = el.get_text().strip()
        if text:
            return text

    if el.parent:
        sibling_script = el.parent.select_one('script[type="math/tex"], script[type="math/tex; mode=display"]')
        if sibling_script:
            text = sibling_script.get_text().strip()
            if text:
                return text

    if el.name == "math":
        text = el.get_text().strip()
        if text:
            return text

    alt = el.get("alt")
    if alt:
        return alt

    return None


def _get_latex_from_element(el: Tag) -> Optional[str]:
    basic = _get_basic_latex_from_element(el)
    if basic:
        return basic

    math_data = _get_mathml_from_element(el)
    if math_data and math_data.mathml:
        try:
            from mathml2latex import mathml2latex

            return mathml2latex(math_data.mathml)
        except ImportError:
            pass
        except Exception:
            pass

    return None


def _is_block_display(el: Tag) -> bool:
    display_attr = el.get("display")
    if display_attr == "block":
        return True

    class_names = get_class_name(el).lower()
    if "display" in class_names or "block" in class_names:
        return True

    container = closest(el, '.katex-display, .MathJax_Display, [data-display="block"]')
    if container:
        return True

    prev = el.previous_sibling
    while prev is not None:
        if isinstance(prev, Tag):
            if prev.name == "p":
                return True
            break
        prev = prev.previous_sibling

    try:
        if sv.match(".mwe-math-fallback-image-display", el):
            return True
    except Exception:
        pass

    try:
        if sv.match(".katex", el):
            return closest(el, ".katex-display") is not None
    except Exception:
        pass

    if el.get("display") == "true":
        return True

    el_type = el.get("type", "")
    if el_type == "math/tex; mode=display":
        return True

    parent_container = closest(el, "[display]")
    if parent_container and parent_container.get("display") == "true":
        return True

    return False


def _get_soup(el: Tag) -> BeautifulSoup:
    node = el
    while node.parent is not None:
        node = node.parent
    if isinstance(node, BeautifulSoup):
        return node
    return BeautifulSoup("", "lxml")


def create_clean_math_el(
    math_data: Optional[MathData],
    latex: Optional[str],
    is_block: bool,
    doc: BeautifulSoup,
) -> Tag:
    clean = doc.new_tag("math")
    clean["xmlns"] = "http://www.w3.org/1998/Math/MathML"
    clean["display"] = "block" if is_block else "inline"
    clean["data-latex"] = latex or ""

    if math_data and math_data.mathml:
        fragment = parse_html(math_data.mathml)
        math_content = fragment.select_one("math")
        if math_content:
            transfer_content(math_content, clean)
    elif latex:
        clean.string = latex

    return clean


def _math_transform(el: Tag, doc: Tag) -> Tag:
    soup = _get_soup(el)

    math_data = _get_mathml_from_element(el)
    latex = _get_latex_from_element(el)
    is_block = _is_block_display(el)
    clean_el = create_clean_math_el(math_data, latex, is_block, soup)

    if el.parent:
        try:
            is_math_script = sv.match('script[type^="math/"]', el)
        except Exception:
            is_math_script = False

        if not is_math_script:
            for math_el in el.parent.select(
                'script[type^="math/"], .MathJax_Preview, '
                'script[type="text/javascript"][src*="mathjax"], '
                'script[type="text/javascript"][src*="katex"]'
            ):
                math_el.decompose()

    return clean_el


def _contains_latex_command(s: str) -> bool:
    return bool(_LATEX_CMD_RE.search(s) or _LATEX_STRUCT_RE.search(s))


def _has_math_library(doc: BeautifulSoup) -> bool:
    for s in doc.select("script[src]"):
        src = (s.get("src", "") or "").lower()
        if "mathjax" in src or "katex" in src:
            return True
    for s in doc.select("script:not([src])"):
        text = s.get_text() or ""
        if re.search(r"MathJax\s*[.=]", text) or re.search(r"katex", text, re.IGNORECASE):
            return True
    return False


def wrap_raw_latex_delimiters(element: Tag, doc: BeautifulSoup) -> None:
    if not _has_math_library(doc):
        return

    if element.select_one(MATH_FAST_CHECK):
        return

    text_nodes: list = []

    def walk(node):
        if is_element(node) and node.name.upper() in _RAW_LATEX_SKIP_TAGS:
            return
        if is_text_node(node):
            text_nodes.append(node)
        elif is_element(node):
            for child in list(node.children):
                walk(child)

    walk(element)

    for text_node in text_nodes:
        text = str(text_node)
        if "$" not in text and "\\(" not in text and "\\[" not in text:
            continue

        parts: List[Union[str, dict]] = []
        last_index = 0
        has_block_math = False

        for m in _LATEX_DELIM_RE.finditer(text):
            block_content = m.group(1) or m.group(2)
            inline_content = m.group(3) or m.group(4)
            is_block = block_content is not None
            latex = (block_content or inline_content).strip()
            is_backslash = m.group(2) is not None or m.group(4) is not None
            if not is_backslash and not _contains_latex_command(latex):
                continue

            if last_index < m.start():
                parts.append(text[last_index : m.start()])
            if is_block:
                has_block_math = True
            parts.append({"latex": latex, "is_block": is_block})
            last_index = m.end()

        if not parts:
            continue
        if last_index < len(text):
            parts.append(text[last_index:])

        if has_block_math:
            has_surrounding = any(isinstance(p, str) and p.strip() for p in parts)
            parent = text_node.parent
            parent_has_other = False
            if parent:
                for n in parent.children:
                    if n is text_node:
                        continue
                    if is_text_node(n) and str(n).strip():
                        parent_has_other = True
                        break
                    if is_element(n):
                        parent_has_other = True
                        break

            if has_surrounding or parent_has_other:
                for p in parts:
                    if isinstance(p, dict):
                        p["is_block"] = False

        frag = BeautifulSoup("", "lxml")
        for part in parts:
            if isinstance(part, str):
                frag.append(NavigableString(part))
            else:
                math_el = frag.new_tag("math")
                math_el["xmlns"] = "http://www.w3.org/1998/Math/MathML"
                math_el["display"] = "block" if part["is_block"] else "inline"
                math_el["data-latex"] = part["latex"]
                math_el.string = part["latex"]
                frag.append(math_el)

        text_node.replace_with(*frag.children)


math_rules: List[dict] = [
    {
        "selector": _MATH_SELECTORS,
        "element": "math",
        "fast_check": MATH_FAST_CHECK,
        "transform": _math_transform,
    }
]
