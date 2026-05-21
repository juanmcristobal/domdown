from __future__ import annotations

import re
from typing import List, Optional, Set

import soupsieve as sv
from bs4 import BeautifulSoup, Tag

from domdown.utils import count_words, is_element, is_text_node

HIGHLIGHTER_PATTERNS = [
    re.compile(r"^language-(\w+)$"),
    re.compile(r"^lang-(\w+)$"),
    re.compile(r"^(\w+)-code$"),
    re.compile(r"^code-(\w+)$"),
    re.compile(r"^syntax-(\w+)$"),
    re.compile(r"^code-snippet__(\w+)$"),
    re.compile(r"^highlight-(\w+)$"),
    re.compile(r"^(\w+)-snippet$"),
    re.compile(r"(?:^|\s)(?:language|lang|brush|syntax)-(\w+)(?:\s|$)", re.IGNORECASE),
]

CODE_LANGUAGES: Set[str] = {
    "abap",
    "actionscript",
    "ada",
    "adoc",
    "agda",
    "antlr4",
    "applescript",
    "arduino",
    "armasm",
    "asciidoc",
    "aspnet",
    "atom",
    "bash",
    "batch",
    "c",
    "clojure",
    "cmake",
    "cobol",
    "coffeescript",
    "cpp",
    "c++",
    "crystal",
    "csharp",
    "cs",
    "dart",
    "django",
    "dockerfile",
    "dotnet",
    "elixir",
    "elm",
    "erlang",
    "fortran",
    "fsharp",
    "gdscript",
    "gitignore",
    "glsl",
    "golang",
    "gradle",
    "graphql",
    "groovy",
    "haskell",
    "hs",
    "haxe",
    "hlsl",
    "html",
    "idris",
    "java",
    "javascript",
    "js",
    "jsx",
    "jsdoc",
    "json",
    "jsonp",
    "julia",
    "kotlin",
    "latex",
    "lean",
    "lean4",
    "lisp",
    "elisp",
    "livescript",
    "lua",
    "makefile",
    "markdown",
    "md",
    "markup",
    "masm",
    "mathml",
    "matlab",
    "mongodb",
    "mysql",
    "nasm",
    "nginx",
    "nim",
    "nix",
    "objc",
    "ocaml",
    "pascal",
    "perl",
    "php",
    "postgresql",
    "powershell",
    "prolog",
    "puppet",
    "python",
    "regex",
    "rss",
    "ruby",
    "rb",
    "rust",
    "scala",
    "scheme",
    "shell",
    "sh",
    "solidity",
    "sparql",
    "sql",
    "ssml",
    "svg",
    "swift",
    "tcl",
    "terraform",
    "tex",
    "toml",
    "typescript",
    "ts",
    "tsx",
    "unrealscript",
    "verilog",
    "vhdl",
    "webassembly",
    "wasm",
    "xml",
    "yaml",
    "yml",
    "zig",
}

_SELECTOR = ", ".join(
    [
        "pre",
        'div[class*="prismjs"]',
        ".syntaxhighlighter",
        ".highlight",
        ".highlight-source",
        ".wp-block-syntaxhighlighter-code",
        ".wp-block-code",
        'div[class*="language-"]',
        ".code-block[data-lang]",
        "code.hl.block",
    ]
)


def _get_classes(el: Tag) -> List[str]:
    cls = el.get("class", [])
    if isinstance(cls, list):
        return cls
    return [cls] if cls else []


def _get_code_language(element: Tag) -> str:
    data_lang = element.get("data-lang") or element.get("data-language") or element.get("language")
    if data_lang:
        return data_lang.lower()

    class_names = _get_classes(element)

    classes_lower = [c.lower() for c in class_names]
    if "syntaxhighlighter" in classes_lower:
        lang_class = next(
            (c for c in class_names if c.lower() not in ("syntaxhighlighter", "nogutter")),
            None,
        )
        if lang_class and lang_class.lower() in CODE_LANGUAGES:
            return lang_class.lower()

    for class_name in class_names:
        for pattern in HIGHLIGHTER_PATTERNS:
            m = pattern.match(class_name)
            if m and m.group(1).lower() in CODE_LANGUAGES:
                return m.group(1).lower()

    for class_name in class_names:
        if class_name.lower() in CODE_LANGUAGES:
            return class_name.lower()

    return ""


def _extract_wordpress_content(element: Tag) -> str:
    code_container = element.select_one(".syntaxhighlighter table .code .container")
    if code_container:
        lines = []
        for line_el in code_container.find_all(True, recursive=False):
            parts = []
            for code in line_el.select("code"):
                text = code.get_text()
                classes = _get_classes(code)
                if "spaces" in classes:
                    text = " " * len(text)
                parts.append(text)
            code_text = "".join(parts) or line_el.get_text()
            lines.append(code_text)
        return "\n".join(lines)

    code_lines = element.select(".code .line")
    if code_lines:
        lines = []
        for line_el in code_lines:
            parts = []
            for code in line_el.select("code"):
                parts.append(code.get_text())
            code_text = "".join(parts) or line_el.get_text()
            lines.append(code_text)
        return "\n".join(lines)

    return ""


def _extract_structured_text(node) -> str:
    if is_text_node(node):
        parent = getattr(node, "parent", None)
        if isinstance(parent, Tag):
            if parent.select_one("[data-line], .line") is not None:
                if not node.strip():
                    return ""
        return str(node) if node else ""

    if not is_element(node):
        return ""

    if sv.match(".hover-info, .hover-container", node):
        return ""

    if node.name in ("button", "style"):
        return ""

    if node.name == "br":
        prev = node.previous_sibling
        if isinstance(prev, Tag):
            try:
                if sv.match(
                    'div[class*="line"], span[class*="line"], .ec-line, [data-line-number], [data-line]',
                    prev,
                ):
                    return ""
            except Exception:
                pass
        return "\n"

    try:
        if sv.match("span.lnt", node):
            return ""
    except Exception:
        pass

    try:
        if sv.match("span.lineno", node):
            return ""
    except Exception:
        pass

    try:
        if sv.match(".react-syntax-highlighter-line-number", node):
            return ""
    except Exception:
        pass

    try:
        if sv.match(".rouge-gutter", node):
            return ""
    except Exception:
        pass

    direct_children = [c for c in node.children if isinstance(c, Tag)]
    if node.name in ("div", "span") and len(direct_children) == 2:
        gutter = direct_children[0].get_text().strip()
        if re.match(r"^\d+$", gutter):
            return re.sub(r"\n$", "", _extract_structured_text(direct_children[1])) + "\n"

    try:
        is_line = sv.match(
            'div[class*="line"], span[class*="line"], .ec-line, [data-line-number], [data-line]',
            node,
        )
    except Exception:
        is_line = False

    if is_line:
        code_container = node.select_one(
            '.code:not(.token), .content:not(.token), [class*="code-"], [class*="content-"]'
        )
        if code_container:
            return re.sub(r"\n$", "", code_container.get_text()) + "\n"

        line_number = node.select_one('.line-number, .gutter, [class*="line-number"], [class*="gutter"]')
        if line_number:
            parts = []
            for child in list(node.children):
                if is_element(child) and _dom_contains(line_number, child):
                    continue
                if is_text_node(child) and _is_inside(child, line_number):
                    continue
                parts.append(_extract_structured_text(child))
            return re.sub(r"\n$", "", "".join(parts)) + "\n"

        return re.sub(r"\n$", "", node.get_text()) + "\n"

    text = ""
    for child in node.children:
        text += _extract_structured_text(child)
    return text


def _dom_contains(parent: Tag, child: Tag) -> bool:
    current = child.parent
    while current is not None:
        if current is parent:
            return True
        current = current.parent if hasattr(current, "parent") else None
    return False


def _is_inside(text_node, container: Tag) -> bool:
    current = text_node.parent
    while current is not None:
        if current is container:
            return True
        current = current.parent if hasattr(current, "parent") else None
    return False


def _transform_code_block(el: Tag, doc: Tag) -> Tag:
    for btn in el.select('button, [class*="codeblock-button"]'):
        btn.decompose()

    for elem in el.select('[class*="header"], [class*="toolbar"], [class*="titlebar"], [class*="title-bar"]'):
        if elem.name not in ("div", "span"):
            continue
        line_ancestor = None
        try:
            from ..utils.dom import closest

            line_ancestor = closest(elem, "[data-line], .line")
        except Exception:
            pass
        if line_ancestor and _dom_contains(el, line_ancestor):
            continue
        if elem.select_one("[data-line], .line, pre"):
            continue
        text = elem.get_text().strip()
        if count_words(text) <= 5:
            elem.decompose()

    language = ""
    current_element: Optional[Tag] = el

    while current_element is not None and not language:
        language = _get_code_language(current_element)

        if not language and current_element is el:
            code_el = current_element.select_one('code[data-lang], code[class*="language-"]')
            if not code_el:
                code_el = current_element.select_one("code")
            if code_el:
                language = _get_code_language(code_el)

        current_element = current_element.parent

    cm_content = el.select_one(".cm-content")
    if cm_content and not language:
        all_divs = el.select("div")
        for div in all_divs:
            if _dom_contains(div, cm_content):
                continue
            text = div.get_text().strip().lower()
            if text and text in CODE_LANGUAGES:
                language = text
                break

    code_content = ""
    try:
        is_syntax = sv.match(".syntaxhighlighter, .wp-block-syntaxhighlighter-code", el)
    except Exception:
        is_syntax = False

    if is_syntax:
        code_content = _extract_wordpress_content(el)

    if not code_content and cm_content:
        code_content = _extract_structured_text(cm_content)
    elif not code_content:
        extract_target = el
        if el.name not in ("pre", "code"):
            pres = el.select("pre")
            code_pre = None
            for p in pres:
                if p.select_one('code[data-lang], code[class*="language-"], .line, [data-line]'):
                    code_pre = p
                    break
            if not code_pre:
                for p in pres:
                    if p.select_one("span[class]") and "lineno" not in _get_classes(p):
                        code_pre = p
                        break
            if code_pre:
                extract_target = code_pre
        code_content = _extract_structured_text(extract_target)

    try:
        is_verso = sv.match("code.hl.block", el)
    except Exception:
        is_verso = False

    if is_verso:
        code_content = re.sub(r"^[ \t]+|[ \t]+$", "", code_content).replace("\t", "    ").replace("\u00a0", " ")
        code_content = re.sub(r"^\n+", "", code_content)
    else:
        code_content = code_content.replace("\t", "    ").replace("\u00a0", " ")

        lines = code_content.split("\n")
        min_indent = float("inf")
        for line in lines:
            first_char = re.search(r"\S", line)
            if first_char is not None:
                min_indent = min(min_indent, first_char.start())
        if min_indent == float("inf"):
            min_indent = 0
        if min_indent > 0:
            code_content = "\n".join(line[min_indent:] for line in lines)

        code_content = re.sub(r"^\s+|\s+$", "", code_content)
        code_content = re.sub(r"\n{3,}", "\n\n", code_content)
        code_content = re.sub(r"^\n+", "", code_content)
        code_content = re.sub(r"\n+$", "", code_content)

    ancestor = el
    for _ in range(3):
        if ancestor is None:
            break
        container = ancestor.parent
        if container is None:
            break
        if not isinstance(container, Tag):
            break
        if container.name == "body":
            break

        direct_children = [c for c in container.children if isinstance(c, Tag)]
        if len(direct_children) > 5:
            break

        try:
            from ..utils.dom import closest as _closest

            if _closest(container, "[data-callout]"):
                break
        except Exception:
            pass

        for sib in list(direct_children):
            if sib is el or _dom_contains(sib, el):
                continue
            if sib.name not in ("div", "span"):
                continue
            sib_text = sib.get_text().strip()
            sib_words = count_words(sib_text)
            if sib_words <= 5 and not sib.select_one(
                "pre, code, img, svg, table, h1, h2, h3, h4, h5, h6, p, blockquote, ul, ol, hr"
            ):
                sib.decompose()
        ancestor = container

    soup = _get_soup(el)
    new_pre = soup.new_tag("pre")

    try:
        is_verso_block = sv.match("code.hl.block, pre.hl.lean.lean-output", el)
    except Exception:
        is_verso_block = False

    if is_verso_block:
        new_pre["data-verso-code"] = "true"

    code = soup.new_tag("code")
    if language:
        code["data-lang"] = language
        code["class"] = f"language-{language}"
    code.string = code_content

    new_pre.append(code)
    return new_pre


def _get_soup(el: Tag) -> BeautifulSoup:
    node = el
    while node.parent is not None:
        node = node.parent
    if isinstance(node, BeautifulSoup):
        return node
    return BeautifulSoup("", "lxml")


code_block_rules: List[dict] = [
    {
        "selector": _SELECTOR,
        "element": "pre",
        "transform": _transform_code_block,
    }
]
