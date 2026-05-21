from __future__ import annotations

import re
from typing import Any, Callable, Dict, List, Optional

from bs4 import BeautifulSoup, Comment, NavigableString, Tag

from domdown.types import DomdownOptions, DomdownResponse
from domdown.utils import is_element, is_text_node
from domdown.utils.dom import closest, is_direct_table_child, serialize_html

WIDTH_DESCRIPTOR_RE = re.compile(r"^(\d+)w,?$")
DENSITY_DESCRIPTOR_RE = re.compile(r"^\d+(?:\.\d+)?x,?$")


def _has_class(el: Tag, class_name: str) -> bool:
    return class_name in el.get("class", [])


def _get_classes(el: Tag) -> List[str]:
    return el.get("class", [])


def get_best_image_src(node: Tag) -> str:
    srcset = node.get("srcset")
    if srcset:
        best_url = ""
        best_width = 0
        tokens = srcset.strip().split()
        url_parts: List[str] = []
        for token in tokens:
            width_match = WIDTH_DESCRIPTOR_RE.match(token)
            if width_match:
                width = int(width_match.group(1))
                if url_parts and width > best_width:
                    url = re.sub(r"^,\s*", "", " ".join(url_parts))
                    if url:
                        best_width = width
                        best_url = url
                url_parts = []
            elif DENSITY_DESCRIPTOR_RE.match(token):
                url_parts = []
            else:
                url_parts.append(token)
        if best_url:
            return best_url
    return node.get("src", "")


class MarkdownConverter:
    REMOVE_TAGS = frozenset(["style", "script"])
    KEEP_TAGS = frozenset(["iframe", "video", "audio", "sup", "sub", "svg", "math"])

    def __init__(self):
        self.footnotes: Dict[str, str] = {}
        self._rules: List[Dict[str, Any]] = []
        self._setup_rules()

    def _setup_rules(self):
        self._rules = [
            {"filter": self._filter_table, "replacement": self._replace_table},
            {"filter": lambda el: el.name == "button", "replacement": lambda c, el: c},
            {
                "filter": lambda el: el.name in ("ul", "ol")
                and not self._is_footnotes_list(el)
                and not self._is_arxiv_enumerate(el),
                "replacement": self._replace_list,
            },
            {"filter": lambda el: el.name == "li", "replacement": self._replace_list_item},
            {"filter": lambda el: el.name == "figure", "replacement": self._replace_figure},
            {"filter": lambda el: el.name == "img", "replacement": self._replace_image},
            {"filter": self._filter_embed, "replacement": self._replace_embed},
            {
                "filter": lambda el: el.name == "mark",
                "replacement": lambda c, el: f"=={c}==",
            },
            {
                "filter": lambda el: el.name in ("del", "s", "strike"),
                "replacement": lambda c, el: f"~~{c}~~",
            },
            {
                "filter": self._filter_complex_link,
                "replacement": self._replace_complex_link,
            },
            {
                "filter": self._is_arxiv_enumerate,
                "replacement": self._replace_arxiv_enumerate,
            },
            {"filter": self._filter_citation, "replacement": self._replace_citation},
            {
                "filter": self._is_footnotes_list,
                "replacement": self._replace_footnotes_list,
            },
            {"filter": self._filter_removals, "replacement": lambda c, el: ""},
            {"filter": lambda el: el.name == "pre", "replacement": self._replace_preformatted},
            {"filter": self._filter_math, "replacement": self._replace_math},
            {"filter": self._filter_katex, "replacement": self._replace_katex},
            {"filter": self._filter_callout, "replacement": self._replace_callout},
        ]

    # ── main entry ────────────────────────────────────────────────────

    def convert(self, html_str: str) -> str:
        html_str = re.sub(r"<wbr\s*/?>", "", html_str, flags=re.IGNORECASE)

        soup = BeautifulSoup(html_str, "lxml")
        root = soup.body if soup.body else soup
        markdown = self._process(root)

        title_match = re.match(r"^# .+\n+", markdown)
        if title_match:
            markdown = markdown[title_match.end() :]

        markdown = re.sub(r"\n*(?<!!)\[]\([^)]+\)\n*", "", markdown)
        markdown = re.sub(r"!(?=!\[|\[!\[)", "! ", markdown)
        markdown = re.sub(r"\n{3,}", "\n\n", markdown)

        if self.footnotes:
            markdown += "\n\n---\n\n"
            for fid, fcontent in self.footnotes.items():
                markdown += f"[^{fid}]: {fcontent}\n\n"

        return markdown.strip()

    # ── DOM walk ──────────────────────────────────────────────────────

    def _process(self, node) -> str:
        if isinstance(node, Comment):
            return ""
        if isinstance(node, NavigableString):
            return self._process_text(node)
        if isinstance(node, Tag):
            return self._process_element(node)
        return ""

    def _process_text(self, node) -> str:
        text = str(node)
        if self._is_inside_pre(node):
            return text
        return re.sub(r"\s+", " ", text)

    def _is_inside_pre(self, node) -> bool:
        parent = node.parent
        while parent:
            if isinstance(parent, Tag) and parent.name == "pre":
                return True
            parent = parent.parent
        return False

    def _process_element(self, el: Tag) -> str:
        if not isinstance(el, Tag):
            return ""

        tag = el.name.lower() if el.name else ""

        if tag in ("[document]", "html", "body"):
            return self._convert_children(el)

        if tag in self.REMOVE_TAGS:
            return ""

        for rule in self._rules:
            if rule["filter"](el):
                content = self._convert_children(el)
                return rule["replacement"](content, el)

        handler = self._default_handlers.get(tag)
        if handler:
            content = self._convert_children(el)
            return handler(content, el)

        if tag in self.KEEP_TAGS:
            return str(el)

        return self._convert_children(el)

    def _convert_children(self, el) -> str:
        return "".join(self._process(child) for child in list(el.children))

    def _turndown(self, html_str: str) -> str:
        soup = BeautifulSoup(html_str, "lxml")
        root = soup.body if soup.body else soup
        return self._process(root)

    # ── default handlers ──────────────────────────────────────────────

    @property
    def _default_handlers(self) -> Dict[str, Callable]:
        return {
            "h1": lambda c, el: f"\n\n# {c.strip()}\n\n",
            "h2": lambda c, el: f"\n\n## {c.strip()}\n\n",
            "h3": lambda c, el: f"\n\n### {c.strip()}\n\n",
            "h4": lambda c, el: f"\n\n#### {c.strip()}\n\n",
            "h5": lambda c, el: f"\n\n##### {c.strip()}\n\n",
            "h6": lambda c, el: f"\n\n###### {c.strip()}\n\n",
            "p": lambda c, el: f"\n\n{c.strip()}\n\n",
            "strong": lambda c, el: f"**{c}**",
            "b": lambda c, el: f"**{c}**",
            "em": lambda c, el: f"*{c}*",
            "i": lambda c, el: f"*{c}*",
            "a": self._handle_link,
            "blockquote": self._handle_blockquote,
            "hr": lambda c, el: "\n\n---\n\n",
            "br": lambda c, el: "\n",
            "code": self._handle_inline_code,
            "dl": lambda c, el: f"\n\n{c.strip()}\n\n",
            "dt": lambda c, el: f"\n\n{c.strip()}\n\n",
            "dd": lambda c, el: f"\n\n:   {c.strip()}\n\n",
            "thead": lambda c, el: c,
            "tbody": lambda c, el: c,
            "tfoot": lambda c, el: c,
            "tr": lambda c, el: c,
            "th": lambda c, el: c,
            "td": lambda c, el: c,
            "colgroup": lambda c, el: "",
            "col": lambda c, el: "",
            "caption": lambda c, el: c,
        }

    def _handle_link(self, content: str, el: Tag) -> str:
        href = el.get("href", "")
        title = el.get("title", "")
        if not href:
            return content
        title_part = f' "{title}"' if title else ""
        return f"[{content}]({href}{title_part})"

    def _handle_blockquote(self, content: str, el: Tag) -> str:
        lines = content.strip().split("\n")
        return "\n\n" + "\n".join(f"> {line}" for line in lines) + "\n\n"

    def _handle_inline_code(self, content: str, el: Tag) -> str:
        parent = el.parent
        if parent and isinstance(parent, Tag) and parent.name == "pre":
            return content
        text = el.get_text()
        if "`" in text:
            return f"`` {text} ``"
        return f"`{text}`"

    # ── custom rule: table ────────────────────────────────────────────

    def _filter_table(self, el: Tag) -> bool:
        return el.name == "table"

    def _replace_table(self, content: str, el: Tag) -> str:
        classes = _get_classes(el)
        if any(c in classes for c in ("ltx_equation", "ltx_eqn_table", "numblk")):
            return self._handle_nested_equations(el)

        has_nested = el.select_one("table") is not None
        direct_cells = [c for c in el.select("td, th") if is_direct_table_child(c, el)]

        if has_nested or len(direct_cells) <= 1:
            direct_rows = [r for r in el.select("tr") if is_direct_table_child(r, el)]
            cell_counts = [sum(1 for c in direct_cells if c.parent is r) for r in direct_rows]
            is_single_column = len(direct_rows) > 0 and len(set(cell_counts)) == 1 and cell_counts[0] <= 1
            if is_single_column:
                cell_html = "".join(serialize_html(c) for c in direct_cells)
                return f"\n\n{self._turndown(cell_html)}\n\n"

        all_cells = el.select("td, th")
        has_complex = any(c.get("colspan") is not None or c.get("rowspan") is not None for c in all_cells)
        if has_complex:
            return f"\n\n{self._cleanup_table_html(el)}\n\n"

        direct_rows = [r for r in el.select("tr") if is_direct_table_child(r, el)]

        rows: List[str] = []
        for row in direct_rows:
            cell_els = [c for c in row.select("td, th") if c.parent is row]
            cell_contents = []
            for cell in cell_els:
                cell_md = self._turndown(serialize_html(cell)).replace("\n", " ").strip()
                cell_md = cell_md.replace("|", "\\|")
                cell_contents.append(cell_md)
            rows.append(f"| {' | '.join(cell_contents)} |")

        if not rows:
            return content

        col_count = len(rows[0].split("|")) - 2
        separator = f"| {' | '.join(['---'] * col_count)} |"

        table_content = "\n".join([rows[0], separator] + rows[1:])
        return f"\n\n{table_content}\n\n"

    # ── custom rule: list / listItem ──────────────────────────────────

    def _replace_list(self, content: str, el: Tag) -> str:
        content = content.strip()
        parent = el.parent
        is_top_level = not (parent and isinstance(parent, Tag) and parent.name in ("ul", "ol"))
        return ("\n" if is_top_level else "") + content + "\n"

    def _replace_list_item(self, content: str, el: Tag) -> str:
        is_task = _has_class(el, "task-list-item")
        checkbox = el.select_one('input[type="checkbox"]')
        task_marker = ""

        if is_task and checkbox:
            content = re.sub(r"<input[^>]*>", "", content)
            task_marker = "[x] " if checkbox.get("checked") is not None else "[ ] "

        content = "\t".join(line for line in content.rstrip("\n").split("\n") if line)

        level = 0
        current: Optional[Tag] = el.parent
        while current and is_element(current):
            if current.name in ("ul", "ol"):
                level += 1
            elif current.name != "li":
                break
            current = current.parent

        indent_level = max(0, level - 1)
        prefix = "\t" * indent_level + "- "

        parent = el.parent
        if parent and is_element(parent) and parent.name == "ol":
            element_children = [c for c in parent.children if is_element(c)]
            try:
                index = element_children.index(el) + 1
            except ValueError:
                index = 1
            start = parent.get("start")
            if start:
                index = int(start) + index - 1
            prefix = "\t" * max(0, level - 1) + f"{index}. "

        result = prefix + task_marker + content.strip()
        next_sib = el.next_sibling
        if next_sib is not None and not content.endswith("\n"):
            result += "\n"
        return result

    # ── custom rule: figure ───────────────────────────────────────────

    def _replace_figure(self, content: str, el: Tag) -> str:
        img = el.select_one("img")
        figcaption = el.select_one("figcaption")

        if not img:
            return content

        has_para_outside = False
        for p in el.select("p"):
            ancestor = p.parent
            while ancestor and ancestor is not el:
                if isinstance(ancestor, Tag) and ancestor.name == "figcaption":
                    break
                ancestor = ancestor.parent
            else:
                if ancestor is el:
                    has_para_outside = True
                    break
        if has_para_outside:
            return content

        alt = img.get("alt", "")
        src = get_best_image_src(img)
        caption = ""

        if figcaption:
            tag_span = figcaption.select_one(".ltx_tag_figure")
            tag_text = tag_span.get_text().strip() if tag_span else ""

            caption_html = serialize_html(figcaption)
            caption_html = re.sub(
                r"<math.*?</math>",
                self._replace_math_in_caption,
                caption_html,
                flags=re.DOTALL,
            )

            caption_md = self._turndown(caption_html)
            caption = f"{tag_text} {caption_md}".strip()

        caption = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"[\1](\2)", caption)

        return f"![{alt}]({src})\n\n{caption}\n\n"

    def _replace_math_in_caption(self, match: re.Match) -> str:
        full_match = match.group(0)
        offset = match.start()
        full_string = match.string

        soup = BeautifulSoup(full_match, "lxml")
        math_el = soup.select_one("math")
        latex = self._extract_latex(math_el) if math_el else ""

        prev_char = full_string[offset - 1] if offset > 0 else ""
        next_char = full_string[offset + len(full_match)] if offset + len(full_match) < len(full_string) else ""

        is_start = offset == 0 or (prev_char and prev_char.isspace())
        is_end = offset + len(full_match) == len(full_string) or (next_char and next_char.isspace())

        left_space = " " if (not is_start and prev_char and not re.match(r"[\s$]", prev_char)) else ""
        right_space = " " if (not is_end and next_char and not re.match(r"[\s$]", next_char)) else ""

        return f"{left_space}${latex}${right_space}"

    # ── custom rule: image ────────────────────────────────────────────

    def _replace_image(self, content: str, el: Tag) -> str:
        alt = el.get("alt", "")
        src = get_best_image_src(el)
        title = el.get("title", "")
        title_part = f' "{title}"' if title else ""
        return f"![{alt}]({src}{title_part})" if src else ""

    # ── custom rule: embed (youtube / twitter) ────────────────────────

    def _filter_embed(self, el: Tag) -> bool:
        if el.name != "iframe":
            return False
        src = el.get("src", "")
        return bool(
            src
            and (
                re.search(r"(?:youtube\.com|youtube-nocookie\.com|youtu\.be)", src)
                or re.search(r"(?:twitter\.com|x\.com)", src)
            )
        )

    def _replace_embed(self, content: str, el: Tag) -> str:
        src = el.get("src", "")
        if src:
            yt_match = re.search(
                r"(?:https?://)?(?:www\.)?(?:youtube\.com|youtube-nocookie\.com|youtu\.be)/(?:embed/|watch\?v=)?([a-zA-Z0-9_-]+)",
                src,
            )
            if yt_match and yt_match.group(1):
                return f"\n![](https://www.youtube.com/watch?v={yt_match.group(1)})\n"

            tweet_direct = re.search(
                r"(?:https?://)?(?:www\.)?(?:twitter\.com|x\.com)/([^/]+)/status/([0-9]+)",
                src,
            )
            if tweet_direct:
                return f"\n![](https://x.com/{tweet_direct.group(1)}/status/{tweet_direct.group(2)})\n"

            tweet_embed = re.search(
                r"(?:https?://)?(?:platform\.)?twitter\.com/embed/Tweet\.html\?.*?id=([0-9]+)",
                src,
            )
            if tweet_embed:
                return f"\n![](https://x.com/i/status/{tweet_embed.group(1)})\n"

        return content

    # ── custom rule: complex link structure ───────────────────────────

    def _filter_complex_link(self, el: Tag) -> bool:
        if el.name != "a":
            return False
        children = list(el.children)
        if len(children) <= 1:
            return False
        return any(isinstance(c, Tag) and c.name in ("h1", "h2", "h3", "h4", "h5", "h6") for c in children)

    def _replace_complex_link(self, content: str, el: Tag) -> str:
        href = el.get("href", "")
        title = el.get("title", "")

        heading = el.select_one("h1, h2, h3, h4, h5, h6")
        heading_content = self._turndown(str(heading)) if heading else ""

        if heading:
            heading.decompose()

        remaining = self._turndown(serialize_html(el))

        markdown = f"{heading_content}\n\n{remaining}\n\n"
        if href:
            markdown += f"[View original]({href}"
            if title:
                markdown += f' "{title}"'
            markdown += ")"
        return markdown

    # ── custom rule: arXiv enumerate ──────────────────────────────────

    def _is_arxiv_enumerate(self, el: Tag) -> bool:
        return el.name == "ol" and _has_class(el, "ltx_enumerate")

    def _replace_arxiv_enumerate(self, content: str, el: Tag) -> str:
        items: List[str] = []
        for i, child in enumerate(list(el.children)):
            if is_element(child):
                item_html = serialize_html(child)
                item_html = re.sub(
                    r'^<span class="ltx_tag ltx_tag_item">\d+\.</span>\s*',
                    "",
                    item_html,
                )
                items.append(f"{i + 1}. {self._turndown(item_html)}")
        return "\n\n" + "\n\n".join(items) + "\n\n"

    # ── custom rule: citations ────────────────────────────────────────

    def _filter_citation(self, el: Tag) -> bool:
        if el.name != "sup":
            return False
        el_id = el.get("id", "")
        return isinstance(el_id, str) and el_id.startswith("fnref:")

    def _replace_citation(self, content: str, el: Tag) -> str:
        el_id = el.get("id", "")
        if el_id.startswith("fnref:"):
            primary = el_id.replace("fnref:", "").split("-")[0]
            return f"[^{primary}]"
        return content

    # ── custom rule: footnotes list ───────────────────────────────────

    def _is_footnotes_list(self, el: Tag) -> bool:
        if el.name != "ol":
            return False
        parent = el.parent
        return parent is not None and is_element(parent) and parent.get("id") == "footnotes"

    def _replace_footnotes_list(self, content: str, el: Tag) -> str:
        references: List[str] = []
        for li in list(el.children):
            if not is_element(li):
                continue

            li_id = li.get("id", "")
            fid = ""
            if li_id:
                if li_id.startswith("fn:"):
                    fid = li_id.replace("fn:", "")
                else:
                    match = re.search(r"cite_note-(.+)", li_id.split("/")[-1])
                    fid = match.group(1) if match else li_id

            sup = li.select_one("sup")
            if sup and sup.get_text().strip() == fid:
                sup.decompose()

            ref_content = self._turndown(serialize_html(li))
            cleaned = re.sub(r"\s*↩︎$", "", ref_content).strip()
            references.append(f"[^{fid.lower()}]: {cleaned}")

        return "\n\n" + "\n\n".join(references) + "\n\n"

    # ── custom rule: removals ─────────────────────────────────────────

    def _filter_removals(self, el: Tag) -> bool:
        href = el.get("href", "")
        if href and "#fnref" in href:
            return True
        if _has_class(el, "footnote-backref"):
            return True
        return False

    # ── custom rule: preformatted code ────────────────────────────────

    def _replace_preformatted(self, content: str, el: Tag) -> str:
        code_el = el.select_one("code")
        if not code_el:
            return content

        lang = code_el.get("data-lang", "") or code_el.get("data-language", "") or ""
        if not lang:
            for cls in _get_classes(code_el):
                m = re.match(r"language-(\w+)", cls)
                if m:
                    lang = m.group(1)
                    break
        if not lang:
            lang = el.get("data-language", "")

        code_text = code_el.get_text()
        clean_code = code_text.strip().replace("`", "\\`")

        return f"\n```{lang}\n{clean_code}\n```\n"

    # ── custom rule: math ─────────────────────────────────────────────

    def _filter_math(self, el: Tag) -> bool:
        if el.name == "math":
            return True
        classes = _get_classes(el)
        return any(
            c in classes
            for c in (
                "mwe-math-element",
                "mwe-math-fallback-image-inline",
                "mwe-math-fallback-image-display",
            )
        )

    def _replace_math(self, content: str, el: Tag) -> str:
        latex = self._extract_latex(el).strip()

        is_in_table = closest(el, "table") is not None

        classes = _get_classes(el)
        if not is_in_table and (
            el.get("display") == "block"
            or "mwe-math-fallback-image-display" in classes
            or self._is_block_math_child(el)
        ):
            return f"\n$$\n{latex}\n$$\n"

        prev = el.previous_sibling
        next_sib = el.next_sibling

        prev_char = ""
        if prev and is_element(prev):
            t = prev.get_text()
            prev_char = t[-1] if t else ""
        elif prev and is_text_node(prev):
            t = str(prev)
            prev_char = t[-1] if t else ""

        next_char = ""
        if next_sib and is_element(next_sib):
            t = next_sib.get_text()
            next_char = t[0] if t else ""
        elif next_sib and is_text_node(next_sib):
            t = str(next_sib)
            next_char = t[0] if t else ""

        is_start = prev is None or (is_text_node(prev) and str(prev).strip() == "")
        is_end = next_sib is None or (is_text_node(next_sib) and str(next_sib).strip() == "")

        left_space = " " if (not is_start and prev_char and not re.match(r"[\s$]", prev_char)) else ""
        right_space = " " if (not is_end and next_char and not re.match(r"[\s$]", next_char)) else ""

        return f"{left_space}${latex}${right_space}"

    def _is_block_math_child(self, el: Tag) -> bool:
        parent = el.parent
        if not parent or not is_element(parent):
            return False
        if not _has_class(parent, "mwe-math-element"):
            return False
        prev = parent.previous_sibling
        while prev and is_text_node(prev) and str(prev).strip() == "":
            prev = prev.previous_sibling
        return prev is not None and is_element(prev) and prev.name == "p"

    # ── custom rule: katex ────────────────────────────────────────────

    def _filter_katex(self, el: Tag) -> bool:
        classes = _get_classes(el)
        return "math" in classes or "katex" in classes

    def _replace_katex(self, content: str, el: Tag) -> str:
        latex = el.get("data-latex", "")

        if not latex:
            annotation = el.select_one('.katex-mathml annotation[encoding="application/x-tex"]')
            latex = annotation.get_text() if annotation else ""

        if not latex:
            latex = el.get_text().strip()

        math_el = el.select_one(".katex-mathml math")
        classes = _get_classes(el)
        is_inline = "math-inline" in classes or (
            math_el and isinstance(math_el, Tag) and math_el.get("display") != "block"
        )

        if is_inline:
            return f"${latex}$"
        return f"\n$$\n{latex}\n$$\n"

    # ── custom rule: callout ──────────────────────────────────────────

    def _filter_callout(self, el: Tag) -> bool:
        return el.get("data-callout") is not None and _has_class(el, "callout")

    def _replace_callout(self, content: str, el: Tag) -> str:
        callout_type = el.get("data-callout", "note")

        fold = el.get("data-callout-fold", "")
        fold_indicator = fold if fold in ("-", "+") else ""

        title_inner = el.select_one(".callout-title-inner")
        title = title_inner.get_text().strip() if title_inner else callout_type.capitalize()

        title_div = el.select_one(".callout-title")
        if title_div:
            title_div.decompose()

        content_el = el.select_one(".callout-content")
        if content_el:
            callout_content = self._turndown(serialize_html(content_el))
        else:
            callout_content = self._turndown(serialize_html(el))

        lines = callout_content.strip().split("\n")
        quoted = "\n".join(f"> {line}" for line in lines)

        return f"\n\n> [!{callout_type}]{fold_indicator} {title}\n{quoted}\n\n"

    # ── helpers ───────────────────────────────────────────────────────

    def _handle_nested_equations(self, element: Tag) -> str:
        math_elements = element.select("math")
        if not math_elements:
            return ""

        results: List[str] = []
        for math_el in math_elements:
            annotation = math_el.select_one('annotation[encoding="application/x-tex"]')
            latex = ""
            if annotation:
                latex = annotation.get_text().strip()
            if not latex:
                alttext = math_el.get("alttext", "")
                if alttext:
                    latex = alttext.strip()

            if latex:
                is_inline = closest(math_el, ".ltx_eqn_inline, .mwe-math-element-inline") is not None
                results.append(f"${latex}$" if is_inline else f"\n$$\n{latex}\n$$")

        return "\n\n".join(results)

    def _cleanup_table_html(self, element: Tag) -> str:
        allowed = frozenset(
            [
                "src",
                "href",
                "style",
                "align",
                "width",
                "height",
                "rowspan",
                "colspan",
                "bgcolor",
                "scope",
                "valign",
                "headers",
            ]
        )

        clone_soup = BeautifulSoup(str(element), "lxml")
        clone = clone_soup.select_one("table")
        if clone is None:
            clone = clone_soup.body if clone_soup.body else clone_soup

        def clean(el: Tag):
            for attr in list(el.attrs.keys()):
                if attr not in allowed:
                    del el[attr]
            for child in list(el.children):
                if is_element(child):
                    clean(child)

        if clone:
            clean(clone)

        result = str(clone)
        return result.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")

    def _extract_latex(self, element: Tag) -> str:
        latex = element.get("data-latex", "")
        if latex:
            return latex.strip()

        alttext = element.get("alttext", "")
        if alttext:
            return alttext.strip()

        if element.name == "math":
            try:
                from mathml2latex import convert

                return convert(str(element)).strip()
            except (ImportError, Exception):
                pass

        return ""


def create_markdown_content(content: str, url: str) -> str:
    converter = MarkdownConverter()
    try:
        return converter.convert(content)
    except Exception:
        return f"Partial conversion completed with errors. Original HTML:\n\n{content}"


def to_markdown(result: DomdownResponse, options: DomdownOptions, url: str) -> None:
    if options.markdown:
        result.content = create_markdown_content(result.content, url)
    elif options.separate_markdown:
        result.content_markdown = create_markdown_content(result.content, url)
