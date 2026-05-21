from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

import soupsieve as sv
from bs4 import BeautifulSoup, NavigableString, Tag

from domdown.constants import BLOCK_LEVEL_ELEMENTS, FOOTNOTE_INLINE_REFERENCES, FOOTNOTE_LIST_SELECTORS
from domdown.utils import is_element, is_text_node
from domdown.utils.dom import closest, get_class_name, parse_html, serialize_html, transfer_content

FOOTNOTE_SECTION_RE = re.compile(r"^(foot\s*notes?|end\s*notes?|notes?|references?)$", re.IGNORECASE)

_BACKREF_SYMBOLS_RE = re.compile(r"^[\^\u21A9\u21A5\u2191\u21B5\u2934\u2935\u23CE]+$")
_CITE_REF_RE = re.compile(r"^#cite_ref-")
_FOOTNOTE_MARKER_RE = re.compile(r"^\[?\(?(\d{1,4})\)?\]?$")


def _get_href_fragment(anchor: Tag) -> str:
    href = anchor.get("href", "") or ""
    parts = href.split("#")
    return parts[-1].lower() if len(parts) > 1 else ""


def _get_soup(el: Tag) -> BeautifulSoup:
    node = el
    while node.parent is not None:
        node = node.parent
    if isinstance(node, BeautifulSoup):
        return node
    return BeautifulSoup("", "lxml")


@dataclass
class FootnoteData:
    content: Any
    original_id: str
    refs: List[str] = field(default_factory=list)


FootnoteCollection = Dict[int, FootnoteData]


@dataclass
class CollectState:
    footnotes: FootnoteCollection = field(default_factory=dict)
    processed_ids: Set[str] = field(default_factory=set)
    count: int = 1


_INLINE_REF_EXTRACTORS: List[dict] = [
    {
        "selector": "sup.footnoteref",
        "extract": lambda el: (
            m.group(1)
            if (
                el.select_one('a[id^="footnoteref-"]')
                and (m := re.match(r"^footnoteref-(\d+)$", el.select_one('a[id^="footnoteref-"]').get("id", "")))
            )
            else ""
        ),
    },
    {
        "selector": 'a[id^="ref-link"]',
        "extract": lambda el: el.get_text().strip(),
    },
    {
        "selector": 'a[role="doc-biblioref"]',
        "extract": lambda el: (
            el.get("data-xml-rid", "")
            or ((href := el.get("href", "")) and href.startswith("#core-R") and href.replace("#core-", "") or "")
        ),
    },
    {
        "selector": "a.footnote-anchor, span.footnote-hovercard-target a",
        "extract": lambda el: (el.get("id", "") or "").replace("footnote-anchor-", "").lower(),
    },
    {
        "selector": "sup.reference",
        "extract": lambda el: _extract_mediawiki_ref(el),
    },
    {
        "selector": 'sup[id^="fnref:"], span[id^="fnref:"]',
        "extract": lambda el: el.get("id", "").replace("fnref:", "").lower(),
    },
    {
        "selector": 'sup[id^="fnr"]',
        "extract": lambda el: el.get("id", "").replace("fnr", "").lower(),
    },
    {
        "selector": "sup.footnote-reference",
        "extract": lambda el: (
            _get_href_fragment(el.select_one('a[href^="#"]')) if el.select_one('a[href^="#"]') else ""
        ),
    },
    {
        "selector": "span.footnote-reference",
        "extract": lambda el: (
            el.get("data-footnote-id", "")
            or (el.get("id", "").startswith("fnref") and el.get("id", "").replace("fnref", "").lower() or "")
        ),
    },
    {
        "selector": "span.footnote-link",
        "extract": lambda el: el.get("data-footnote-id", "") or "",
    },
    {
        "selector": "a.citation",
        "extract": lambda el: el.get_text().strip(),
    },
    {
        "selector": 'a[id^="fnref"]',
        "extract": lambda el: el.get("id", "").replace("fnref", "").lower(),
    },
]


def _extract_mediawiki_ref(el: Tag) -> str:
    id_val = ""
    for link in el.select("a"):
        href = link.get("href", "") or ""
        parts = href.split("/")
        m = re.search(r"(?:cite_note|cite_ref)-(.+)", parts[-1] if parts else "")
        if m:
            id_val = m.group(1).lower()
    return id_val


class FootnoteHandler:
    def __init__(self, doc: BeautifulSoup):
        self.doc = doc
        self.pending_removals: List[Any] = []

    def _make_ref_id(self, footnote_number: str, refs_length: int) -> str:
        if refs_length > 0:
            return f"fnref:{footnote_number}-{refs_length + 1}"
        return f"fnref:{footnote_number}"

    def _merge_footnotes(self, target: FootnoteCollection, source: FootnoteCollection) -> None:
        for num, data in source.items():
            if num not in target:
                target[num] = data

    def _add_footnote(self, state: CollectState, id_val: str, content: Any, explicit_num: Optional[int] = None) -> bool:
        if not id_val or id_val in state.processed_ids:
            return False
        key = explicit_num if explicit_num is not None else state.count
        state.footnotes[key] = FootnoteData(content=content, original_id=id_val)
        state.processed_ids.add(id_val)
        if explicit_num is None:
            state.count += 1
        elif explicit_num >= state.count:
            state.count = explicit_num + 1
        return True

    def create_footnote_item(self, footnote_number: int, content: Any, refs: List[str]) -> Tag:
        doc = self.doc
        new_item = doc.new_tag("li")
        new_item["class"] = "footnote"
        new_item["id"] = f"fn:{footnote_number}"

        if isinstance(content, str):
            paragraph = doc.new_tag("p")
            parsed = parse_html(content)
            transfer_content(parsed, paragraph)
            new_item.append(paragraph)
        else:
            children = [c for c in content.children if isinstance(c, Tag)]
            has_paragraphs = any(c.name == "p" for c in children)
            has_block = any(c.name in BLOCK_LEVEL_ELEMENTS for c in children)

            if not has_paragraphs and not has_block:
                paragraph = doc.new_tag("p")
                transfer_content(content, paragraph)
                self.remove_backrefs(paragraph)
                new_item.append(paragraph)
            elif not has_paragraphs and has_block:
                for child in children:
                    if self.is_backref_link(child):
                        continue
                    from copy import copy

                    clone = copy(child)
                    self.remove_backrefs(clone)
                    new_item.append(clone)
            else:
                for child in children:
                    if self.is_backref_link(child):
                        continue
                    if child.name == "p":
                        if not child.get_text().strip() and not child.select_one("img, br"):
                            continue
                        new_p = doc.new_tag("p")
                        transfer_content(child, new_p)
                        self.remove_backrefs(new_p)
                        new_item.append(new_p)
                    else:
                        from copy import copy

                        clone = copy(child)
                        self.remove_backrefs(clone)
                        new_item.append(clone)

        last_p = new_item.select_one("p:last-of-type") or new_item
        for i, ref_id in enumerate(refs):
            backlink = doc.new_tag("a")
            backlink["href"] = f"#{ref_id}"
            backlink["title"] = "return to article"
            backlink["class"] = "footnote-backref"
            backlink.string = "↩"
            if i < len(refs) - 1:
                backlink.string = backlink.string + " "
            last_p.append(backlink)

        return new_item

    def collect_footnotes(self, element: Tag) -> FootnoteCollection:
        state = CollectState()
        footnote_lists = element.select(FOOTNOTE_LIST_SELECTORS)

        for lst in footnote_lists:
            try:
                is_wikidot = sv.match("div.footnotes-footer", lst)
            except Exception:
                is_wikidot = False

            if is_wikidot:
                for div in lst.select("div.footnote-footer"):
                    m = re.match(r"^footnote-(\d+)$", div.get("id", "") or "")
                    if not m:
                        continue
                    id_val = m.group(1)
                    if id_val in state.processed_ids:
                        continue
                    from copy import copy

                    clone = copy(div)
                    back_link = clone.select_one("a")
                    if back_link:
                        back_link.decompose()
                    text = serialize_html(clone).strip()
                    text = re.sub(r"^\s*\.\s*", "", text)
                    content_div = _get_soup(element).new_tag("div")
                    parsed = parse_html(text.strip())
                    transfer_content(parsed, content_div)
                    self._add_footnote(state, id_val, content_div)
                continue

            try:
                is_standalone_fn_def = sv.match("div.footnote-definition", lst)
            except Exception:
                is_standalone_fn_def = False

            if is_standalone_fn_def:
                parent = lst.parent
                if parent and isinstance(parent, Tag):
                    try:
                        is_wrapper = sv.match("div.footnote-definitions", parent)
                    except Exception:
                        is_wrapper = False
                    if is_wrapper:
                        continue

                id_val = (lst.get("id", "") or "").lower()
                from copy import copy

                clone = copy(lst)
                label = clone.select_one("sup.footnote-definition-label")
                if label:
                    label.decompose()
                self._add_footnote(state, id_val, clone)
                continue

            try:
                is_fn_defs = sv.match("div.footnote-definitions", lst)
            except Exception:
                is_fn_defs = False

            if is_fn_defs:
                for defn in lst.select("div.footnote-definition"):
                    sup_el = defn.select_one("sup[id]")
                    body = defn.select_one(".footnote-body")
                    if not sup_el or not body:
                        continue
                    from copy import copy

                    self._add_footnote(state, (sup_el.get("id", "") or "").lower(), copy(body))
                parent = lst.parent
                if parent and parent is not element:
                    parent_classes = parent.get("class", []) or []
                    if isinstance(parent_classes, list) and "footnotes" in parent_classes:
                        self.pending_removals.append(parent)
                continue

            try:
                is_easy = sv.match("ol.easy-footnotes-wrapper", lst)
            except Exception:
                is_easy = False

            if is_easy:
                for li in lst.select("li.easy-footnote-single"):
                    id_span = li.select_one('span[id^="easy-footnote-bottom-"]')
                    if not id_span:
                        continue
                    from copy import copy

                    clone = copy(li)
                    bottom_span = clone.select_one('span[id^="easy-footnote-bottom-"]')
                    if bottom_span:
                        bottom_span.decompose()
                    top_link = clone.select_one("a.easy-footnote-to-top")
                    if top_link:
                        top_link.decompose()
                    self._add_footnote(state, id_span.get("id", "").lower(), clone)
                for span in element.select("span.easy-footnote-margin-adjust"):
                    self.pending_removals.append(span)
                continue

            try:
                is_substack = sv.match('div.footnote[data-component-name="FootnoteToDOM"]', lst)
            except Exception:
                is_substack = False

            if is_substack:
                anchor = lst.select_one("a.footnote-number")
                content = lst.select_one(".footnote-content")
                if anchor and content:
                    self._add_footnote(
                        state,
                        anchor.get("id", "").replace("footnote-", "").lower(),
                        content,
                    )
                continue

            items = lst.select('li, div[role="listitem"]')
            for li in items:
                id_val, content = self._extract_list_item_id_and_content(li)
                self._add_footnote(state, id_val, content or li)

        fallbacks = [
            self._try_generic_id_detection,
            self._try_word_export,
            self._try_google_docs,
            self._try_labeled_section,
            self._try_loose_footnotes,
            self._try_class_footnote,
        ]
        for fallback in fallbacks:
            if state.count > 1:
                break
            fallback(element, state)

        return state.footnotes

    def _try_generic_id_detection(self, element: Tag, state: CollectState) -> None:
        candidate_refs: Dict[str, List[Tag]] = {}
        for a in element.select('a[href*="#"]'):
            fragment = _get_href_fragment(a)
            if not fragment:
                continue
            text = a.get_text().strip()
            if not _FOOTNOTE_MARKER_RE.match(text):
                continue
            candidate_refs.setdefault(fragment, []).append(a)

        if len(candidate_refs) < 2:
            return

        fragment_set = set(candidate_refs.keys())
        containers = element.select("div, section, aside, footer, ol, ul")
        best_container: Optional[Tag] = None
        best_match_count = 0

        for container in containers:
            if container is element:
                continue
            match_count = len(self._find_matching_footnote_elements(container, fragment_set))
            if match_count >= 2 and match_count >= best_match_count:
                best_match_count = match_count
                best_container = container

        if not best_container:
            return

        ordered_elements = self._find_matching_footnote_elements(best_container, fragment_set)
        footnote_fragments = {item["id"] for item in ordered_elements}
        external_total = 0
        external_match = 0
        for frag, anchors in candidate_refs.items():
            if any(best_container is not None and _dom_contains(best_container, a) for a in anchors):
                continue
            external_total += 1
            if frag in footnote_fragments:
                external_match += 1
        if external_match < max(2, -(-external_total * 75 // 100)):
            best_container = None

        for item in ordered_elements:
            el = item["el"]
            id_val = item["id"]
            if id_val in state.processed_ids:
                continue

            soup = _get_soup(element)
            content_div = soup.new_tag("div")
            from copy import copy

            clone = copy(el)

            id_anchor = clone.select_one(f'a[id="{id_val}"]')
            if id_anchor:
                anchor_text = id_anchor.get_text().strip()
                if not anchor_text or re.match(r"^\d+[.)]*\s*$", anchor_text):
                    id_anchor.decompose()

            named_anchor = clone.select_one("a[name]")
            if named_anchor and (named_anchor.get("name", "") or "").lower() == id_val:
                named_anchor.decompose()

            first_child = list(clone.children)[0] if list(clone.children) else None
            if isinstance(first_child, NavigableString):
                first_child.replace_with(
                    NavigableString(re.sub(r"^\d+\.\s*", "", re.sub(r"^\s+", "", str(first_child))))
                )

            try:
                is_li = sv.match("li", clone)
            except Exception:
                is_li = clone.name == "li"

            if is_li:
                transfer_content(clone, content_div)
            else:
                content_div.append(clone)

            sibling = el.next_sibling
            while sibling is not None and isinstance(sibling, Tag) and not sibling.get("id"):
                sib_anchor_id = self._get_child_anchor_id(sibling)
                if sib_anchor_id and sib_anchor_id in fragment_set:
                    break
                from copy import copy as copy2

                content_div.append(copy2(sibling))
                sibling = sibling.next_sibling

            self._add_footnote(state, id_val, content_div)

        if best_container:
            self.pending_removals.append(best_container)

    def _try_word_export(self, element: Tag, state: CollectState) -> None:
        word_backrefs = element.select('a[href*="#_ftnref"]')
        if len(word_backrefs) < 2:
            return

        pairs: List[Tuple[int, Tag]] = []
        for anchor in word_backrefs:
            m = re.match(r"^_ftnref(\d+)$", _get_href_fragment(anchor))
            if m:
                pairs.append((int(m.group(1)), anchor))
        pairs.sort(key=lambda x: x[0])

        for num, anchor in pairs:
            original_id = f"_ftn{num}"
            if original_id in state.processed_ids:
                continue

            container: Optional[Tag] = anchor.parent
            while container and container is not element:
                tag = container.name
                if tag in ("p", "div", "li"):
                    break
                container = container.parent
            if not container or container is element:
                continue

            from copy import copy

            clone = copy(container)
            backref_anchor = clone.select_one('a[href*="_ftnref"]')
            if backref_anchor:
                wrap_sup = None
                for parent in backref_anchor.parents:
                    if parent.name == "sup":
                        wrap_sup = parent
                        break
                if wrap_sup:
                    wrap_sup.decompose()
                else:
                    backref_anchor.decompose()

            soup = _get_soup(element)
            content_div = soup.new_tag("div")
            content_div.append(clone)

            self._add_footnote(state, original_id, content_div, num)
            self.pending_removals.append(container)

    def _try_google_docs(self, element: Tag, state: CollectState) -> None:
        gdoc_pairs: List[Tuple[int, Tag]] = []
        for p in element.select('p[id^="ftnt"]'):
            m = re.match(r"^ftnt(\d+)$", p.get("id", "") or "")
            if m:
                gdoc_pairs.append((int(m.group(1)), p))

        if len(gdoc_pairs) < 2:
            return

        gdoc_pairs.sort(key=lambda x: x[0])
        for num, el in gdoc_pairs:
            original_id = f"ftnt{num}"
            if original_id in state.processed_ids:
                continue

            from copy import copy

            clone = copy(el)
            backref = clone.select_one('a[href*="#ftnt_ref"]')
            if backref:
                backref.decompose()

            soup = _get_soup(element)
            content_div = soup.new_tag("div")
            content_div.append(clone)

            self._add_footnote(state, original_id, content_div, num)
            self.pending_removals.append(el)

            parent = el.parent
            if parent and parent is not element and isinstance(parent, Tag) and parent.name == "div":
                direct_children = [c for c in parent.children if isinstance(c, Tag)]
                if len(direct_children) == 1:
                    self.pending_removals.append(parent)

        first_el = gdoc_pairs[0][1]
        first_parent = first_el.parent
        if (
            first_parent
            and first_parent is not element
            and isinstance(first_parent, Tag)
            and first_parent.name == "div"
        ):
            scan_from = first_parent
        else:
            scan_from = first_el
        prev = scan_from.previous_sibling
        while prev is not None:
            if isinstance(prev, Tag):
                break
            prev = prev.previous_sibling
        if (
            prev
            and isinstance(prev, Tag)
            and re.match(r"^h[1-6]$", prev.name)
            and FOOTNOTE_SECTION_RE.match(prev.get_text().strip() or "")
        ):
            self.pending_removals.append(prev)

    def _try_loose_footnotes(self, element: Tag, state: CollectState) -> None:
        result = self._find_loose_footnote_paragraphs(element)
        if not result:
            return

        paragraphs, to_remove = result["paragraphs"], result["to_remove"]
        to_remove_set = set(id(r) for r in to_remove)
        for i, item in enumerate(paragraphs):
            num = item["num"]
            def_para = item["el"]
            next_def = paragraphs[i + 1]["el"] if i + 1 < len(paragraphs) else None

            content_div = self._strip_marker_and_wrap(def_para)
            sibling = def_para.next_sibling
            while sibling is not None and isinstance(sibling, Tag) and sibling is not next_def:
                if id(sibling) in to_remove_set:
                    from copy import copy

                    content_div.append(copy(sibling))
                sibling = sibling.next_sibling

            self._add_footnote(state, str(num), content_div)

        self.pending_removals.extend(to_remove)

    def _try_class_footnote(self, element: Tag, state: CollectState) -> None:
        footnote_paragraphs: List[Tuple[int, Tag]] = []
        for p in element.select("p.footnote"):
            num = self._parse_footnote_num(p)
            if num is not None:
                footnote_paragraphs.append((num, p))

        for num, def_para in footnote_paragraphs:
            self._add_footnote(state, str(num), self._strip_marker_and_wrap(def_para))
        self.pending_removals.extend([p for _, p in footnote_paragraphs])

    def _try_labeled_section(self, element: Tag, state: CollectState) -> None:
        containers = element.select("div, section, aside")
        for container in containers:
            class_name = get_class_name(container)
            id_val = container.get("id", "") or ""
            if not re.search(r"footnote", class_name, re.IGNORECASE) and not re.search(
                r"footnote", id_val, re.IGNORECASE
            ):
                continue

            heading = container.select_one("h1, h2, h3, h4, h5, h6")
            if not heading or not FOOTNOTE_SECTION_RE.match(heading.get_text().strip() or ""):
                continue

            paragraphs: List[Tuple[int, Tag]] = []
            for p in container.select("p"):
                num = self._parse_footnote_num(p)
                if num is not None:
                    paragraphs.append((num, p))

            if not paragraphs:
                continue

            numbered_set = set(id(p) for _, p in paragraphs)
            for i, (num, def_para) in enumerate(paragraphs):
                content_div = self._strip_marker_and_wrap(def_para)

                sibling = def_para.next_sibling
                while sibling is not None and isinstance(sibling, Tag):
                    if id(sibling) in numbered_set:
                        break
                    if sibling.get_text().strip():
                        from copy import copy

                        content_div.append(copy(sibling))
                    self.pending_removals.append(sibling)
                    sibling = sibling.next_sibling

                self._add_footnote(state, str(num), content_div)
                self.pending_removals.append(def_para)

            self.pending_removals.append(container)
            break

    def _trim_leading_whitespace(self, parent: Tag) -> None:
        first = list(parent.children)[0] if list(parent.children) else None
        if isinstance(first, NavigableString):
            first.replace_with(NavigableString(re.sub(r"^\s+", "", str(first))))

    def _is_bold_wrapped_sup(self, el: Tag) -> bool:
        tag = el.name
        if tag not in ("b", "strong"):
            return False
        first_child = list(el.children)[0] if list(el.children) else None
        first_element = el.find(True)
        return first_child is first_element and isinstance(first_element, Tag) and first_element.name == "sup"

    def _strip_marker_and_wrap(self, el: Tag) -> Tag:
        soup = _get_soup(el)
        content_div = soup.new_tag("div")
        from copy import copy

        clone = copy(el)
        first_elem = clone.find(True)
        if first_elem:
            if self._is_bold_wrapped_sup(first_elem):
                inner_sup = first_elem.find(True)
                if inner_sup:
                    inner_sup.decompose()
                self._trim_leading_whitespace(first_elem)
            else:
                first_elem.decompose()
                self._trim_leading_whitespace(clone)
        content_div.append(clone)
        return content_div

    def _parse_footnote_num(self, el: Tag) -> Optional[int]:
        children = list(el.children)
        if not children:
            return None
        first_elem = el.find(True)
        if not first_elem:
            return None
        if first_elem is not children[0]:
            return None
        first = first_elem
        tag = first.name
        if self._is_bold_wrapped_sup(first):
            inner = first.find(True)
            if inner:
                first = inner
                tag = "sup"
        if tag not in ("sup", "strong"):
            return None
        num_text = first.get_text().strip()
        try:
            num = int(num_text)
        except (ValueError, TypeError):
            return None
        if num >= 1 and str(num) == num_text:
            return num
        return None

    def _cross_validate(self, element: Tag, paragraphs: List[dict]) -> bool:
        numbered_nums = {p["num"] for p in paragraphs}
        paragraph_els = {id(p["el"]) for p in paragraphs}
        matched: Set[int] = set()
        for sup in element.select("sup"):
            if id(sup) in paragraph_els:
                continue
            if _dom_contains_any(sup, [p["el"] for p in paragraphs]):
                continue
            if sup.select_one("a"):
                continue
            text = sup.get_text().strip()
            try:
                n = int(text)
            except (ValueError, TypeError):
                continue
            if n >= 1 and str(n) == text and n in numbered_nums:
                matched.add(n)
        return len(matched) >= 2

    def _find_loose_footnote_paragraphs(self, element: Tag) -> Optional[dict]:
        all_ps = element.select("p")
        if not all_ps:
            return None
        container = all_ps[-1].parent or element
        children = [c for c in container.children if isinstance(c, Tag)]

        for i in range(len(children) - 1, -1, -1):
            if children[i].name == "hr":
                paragraphs = []
                for j in range(i + 1, len(children)):
                    num = self._parse_footnote_num(children[j])
                    if num is not None:
                        paragraphs.append({"num": num, "el": children[j]})
                if len(paragraphs) >= 2 and self._cross_validate(element, paragraphs):
                    return {"paragraphs": paragraphs, "to_remove": children[i:]}
                break

        trailing: List[dict] = []
        first_footnote_idx = -1
        for i in range(len(children) - 1, -1, -1):
            child = children[i]
            if child.name == "p":
                num = self._parse_footnote_num(child)
                if num is not None:
                    trailing.insert(0, {"num": num, "el": child})
                    first_footnote_idx = i
                    continue
                break
            if child.name in ("ul", "ol", "blockquote"):
                continue
            break

        if len(trailing) >= 2 and self._cross_validate(element, trailing):
            to_remove = children[first_footnote_idx:]
            prev = trailing[0]["el"].previous_sibling
            while prev is not None:
                if isinstance(prev, Tag):
                    break
                prev = prev.previous_sibling
            if (
                prev
                and isinstance(prev, Tag)
                and re.match(r"^h[1-6]$", prev.name)
                and FOOTNOTE_SECTION_RE.match(prev.get_text().strip() or "")
            ):
                to_remove = [prev] + to_remove
            return {"paragraphs": trailing, "to_remove": to_remove}

        half_idx = len(all_ps) // 2
        scattered: List[dict] = []
        for i in range(half_idx, len(all_ps)):
            num = self._parse_footnote_num(all_ps[i])
            if num is not None:
                scattered.append({"num": num, "el": all_ps[i]})

        if len(scattered) >= 2 and self._cross_validate(element, scattered):
            return {"paragraphs": scattered, "to_remove": [p["el"] for p in scattered]}

        return None

    def is_backref_link(self, el: Tag) -> bool:
        if el.name != "a":
            return False
        text = el.get_text().strip()
        text = re.sub(r"[\uFE0E\uFE0F]", "", text)
        if _BACKREF_SYMBOLS_RE.match(text):
            return True
        classes = el.get("class", []) or []
        if isinstance(classes, list) and "footnote-backref" in classes:
            return True
        href = el.get("href", "") or ""
        if _CITE_REF_RE.match(href):
            return True
        return False

    def remove_backrefs(self, el: Tag) -> None:
        for a in list(el.select("a")):
            if self.is_backref_link(a):
                parent = a.parent
                if parent and isinstance(parent, Tag) and parent.name == "sup":
                    siblings = [c for c in parent.children if isinstance(c, Tag)]
                    if len(siblings) == 1:
                        parent.decompose()
                        continue
                a.decompose()

        children = list(el.children)
        while children:
            first = children[0]
            if isinstance(first, NavigableString):
                text = str(first)
                if re.match(r"^[\s\^,.;]*$", text) and "^" in text:
                    first.extract()
                    children = list(el.children)
                    continue
            break

        children = list(el.children)
        while children:
            last = children[-1]
            if isinstance(last, NavigableString):
                text = str(last)
                if re.match(r"^[\s,.;]*$", text):
                    last.extract()
                    children = list(el.children)
                    continue
            break

    def _get_child_anchor_id(self, el: Tag) -> str:
        anchor = el.select_one("a[id], a[name]")
        if not anchor:
            return ""
        return (anchor.get("id", "") or anchor.get("name", "") or "").lower()

    def _extract_list_item_id_and_content(self, li: Tag) -> Tuple[str, Optional[Tag]]:
        citations_div = li.select_one(".citations")
        if citations_div:
            cid = citations_div.get("id", "") or ""
            if cid.lower().startswith("r"):
                content = citations_div.select_one(".citation-content")
                return cid.lower(), content

        raw_id = (li.get("id", "") or "").lower()
        for prefix in ["bib.bib", "fn:", "fn"]:
            if raw_id.startswith(prefix):
                return raw_id[len(prefix) :], li

        if li.get("data-counter"):
            id_val = re.sub(r"\.$", "", li["data-counter"]).lower()
            return id_val, li

        parts = raw_id.split("/")
        m = re.search(r"cite_note-(.+)", parts[-1])
        return (m.group(1) if m else raw_id), li

    def _find_matching_footnote_elements(self, container: Tag, fragment_set: Set[str]) -> List[dict]:
        results: List[dict] = []
        seen: Set[str] = set()
        for el in container.select("li, p, div"):
            id_val = ""
            el_id = (el.get("id", "") or "").lower()
            if el_id and el_id in fragment_set:
                id_val = el_id
            elif not el_id:
                anchor_id = self._get_child_anchor_id(el)
                if anchor_id and anchor_id in fragment_set:
                    id_val = anchor_id
            if id_val and id_val not in seen:
                results.append({"el": el, "id": id_val})
                seen.add(id_val)
        return results

    def _replace_container_preserving_text(self, container: Tag, footnote_ref: Tag) -> None:
        direct_text = ""
        has_child_elements = False
        for node in container.children:
            if is_text_node(node):
                direct_text += str(node)
            elif is_element(node):
                has_child_elements = True
        direct_text = direct_text.strip()

        if direct_text and has_child_elements:
            frag = BeautifulSoup("", "lxml")
            frag.append(NavigableString(direct_text))
            frag.append(footnote_ref)
            container.replace_with(*list(frag.children))
        else:
            container.replace_with(footnote_ref)

    def _find_outer_footnote_container(self, el: Tag) -> Tag:
        current: Tag = el
        parent = el.parent

        while parent is not None and isinstance(parent, Tag):
            tag = parent.name
            if tag not in ("span", "sup"):
                break

            if tag == "span":
                has_non_footnote = False
                for child in parent.children:
                    if child is current:
                        continue
                    if is_text_node(child) and str(child).strip():
                        has_non_footnote = True
                        break
                    if is_element(child) and child.name != "sup":
                        has_non_footnote = True
                        break
                if has_non_footnote:
                    break

            current = parent
            parent = parent.parent

        return current

    def _create_footnote_reference(self, footnote_number: str, ref_id: str) -> Tag:
        sup = self.doc.new_tag("sup")
        sup["id"] = ref_id
        link = self.doc.new_tag("a")
        link["href"] = f"#fn:{footnote_number}"
        link.string = footnote_number
        sup.append(link)
        return sup

    def _collect_inline_sidenotes(self, element: Tag) -> FootnoteCollection:
        footnotes: FootnoteCollection = {}
        containers = element.select("span.footnote-container, span.sidenote-container, span.inline-footnote")

        if not containers:
            footrefs = element.select("label.footref")
            if footrefs:
                footnote_count = 1
                for label in footrefs:
                    sibling = label.next_sibling
                    while sibling is not None and not isinstance(sibling, Tag):
                        sibling = sibling.next_sibling
                    if (
                        sibling
                        and isinstance(sibling, Tag)
                        and sibling.name == "input"
                        and "footref-toggle" in (sibling.get("class", []) or [])
                    ):
                        sibling = sibling.next_sibling
                        while sibling is not None and not isinstance(sibling, Tag):
                            sibling = sibling.next_sibling

                    if (
                        not sibling
                        or not isinstance(sibling, Tag)
                        or sibling.name != "span"
                        or "sidenote" not in (sibling.get("class", []) or [])
                    ):
                        continue

                    from copy import copy

                    content = copy(sibling)
                    leading_sup = content.find(True)
                    if leading_sup and leading_sup.name == "sup" and content.children:
                        children_list = list(content.children)
                        if children_list[0] is leading_sup:
                            leading_sup.decompose()

                    footnotes[footnote_count] = FootnoteData(
                        content=content,
                        original_id=str(footnote_count),
                        refs=[f"fnref:{footnote_count}"],
                    )

                    ref = self._create_footnote_reference(str(footnote_count), f"fnref:{footnote_count}")
                    input_el = label.next_sibling
                    while input_el is not None and not isinstance(input_el, Tag):
                        input_el = input_el.next_sibling
                    if (
                        input_el
                        and isinstance(input_el, Tag)
                        and input_el.name == "input"
                        and "footref-toggle" in (input_el.get("class", []) or [])
                    ):
                        input_el.decompose()
                    sibling.decompose()
                    label.replace_with(ref)
                    footnote_count += 1

                for footer in element.select("footer"):
                    if footer.select_one(".footdef"):
                        footer.decompose()

                return footnotes

            for sidenote in element.select("span.sidenote"):
                sidenote.decompose()
            return footnotes

        footnote_count = 1
        for container in containers:
            content = container.select_one("span.footnote, span.sidenote, span.footnoteContent")
            if not content:
                continue

            from copy import copy

            footnotes[footnote_count] = FootnoteData(
                content=copy(content),
                original_id=str(footnote_count),
                refs=[f"fnref:{footnote_count}"],
            )

            ref = self._create_footnote_reference(str(footnote_count), f"fnref:{footnote_count}")
            container.replace_with(ref)
            footnote_count += 1

        return footnotes

    def _collect_sidenotes_column(self, element: Tag) -> FootnoteCollection:
        footnotes: FootnoteCollection = {}
        columns = element.select(".sidenotes-column")

        if not columns:
            ancestor = element.parent
            for _ in range(3):
                if ancestor is None or not isinstance(ancestor, Tag):
                    break
                columns = [
                    c
                    for c in ancestor.children
                    if isinstance(c, Tag) and "sidenotes-column" in (c.get("class", []) or [])
                ]
                if columns:
                    break
                ancestor = ancestor.parent

        if not columns:
            return footnotes

        footnote_count = 1
        for column in columns:
            for sidenote in column.select(".sidenote[id]"):
                id_val = sidenote.get("id", "")
                if not id_val:
                    continue

                id_span = sidenote.select_one(".sidenote__id")
                num_text = re.sub(r"\D", "", id_span.get_text()) if id_span else ""
                footnote_number = int(num_text) if num_text else footnote_count

                content_div = self.doc.new_tag("div")
                for node in list(sidenote.children):
                    if is_element(node):
                        classes = node.get("class", []) or []
                        if isinstance(classes, list):
                            if "sidenote__id" in classes:
                                continue
                            if "sidenote__label" in classes:
                                continue
                            if "sn-backref" in classes:
                                continue
                    from copy import copy

                    content_div.append(copy(node) if isinstance(node, Tag) else copy(node))

                self.remove_backrefs(content_div)

                footnotes[footnote_number] = FootnoteData(
                    content=content_div,
                    original_id=id_val.lower(),
                    refs=[],
                )
                footnote_count += 1

            column.decompose()

        return footnotes

    def _collect_aside_footnotes(self, element: Tag) -> FootnoteCollection:
        footnotes: FootnoteCollection = {}
        ols = element.select("aside > ol[start]")
        if not ols:
            return footnotes

        for ol_tag in ols:
            aside = ol_tag.parent
            if not isinstance(aside, Tag):
                continue
            try:
                footnote_number = int(ol_tag.get("start", ""))
            except (ValueError, TypeError):
                continue
            if footnote_number < 1:
                continue

            items = ol_tag.select("li")
            if not items:
                continue

            content_div = self.doc.new_tag("div")
            if len(items) == 1:
                from copy import copy

                transfer_content(copy(items[0]), content_div)
            else:
                for li in items:
                    p = self.doc.new_tag("p")
                    from copy import copy

                    transfer_content(copy(li), p)
                    content_div.append(p)

            footnotes[footnote_number] = FootnoteData(
                content=content_div,
                original_id=str(footnote_number),
                refs=[],
            )

            aside.decompose()

        return footnotes

    def _collect_hidden_aside_footnotes(self, element: Tag) -> FootnoteCollection:
        footnotes: FootnoteCollection = {}
        refs = element.select("span[data-definition]")
        if not refs:
            return footnotes

        aside_map: Dict[str, Tag] = {}
        for aside in element.select("aside[id]"):
            aside_map[aside["id"]] = aside

        footnote_count = 1
        for ref_el in refs:
            def_id = ref_el.get("data-definition", "")
            if not def_id:
                continue
            aside = aside_map.get(def_id)
            if not aside:
                continue

            content_div = self.doc.new_tag("div")
            transfer_content(aside, content_div)
            aside.decompose()

            footnote_number = str(footnote_count)
            ref_id = f"fnref:{footnote_number}"
            footnotes[footnote_count] = FootnoteData(
                content=content_div,
                original_id=def_id.lower(),
                refs=[ref_id],
            )

            ref_el.replace_with(self._create_footnote_reference(footnote_number, ref_id))
            footnote_count += 1

        return footnotes

    def standardize_footnotes(self, element: Tag) -> None:
        sidenotes = self._collect_inline_sidenotes(element)
        footnotes = self._collect_hidden_aside_footnotes(element)
        self._merge_footnotes(footnotes, self.collect_footnotes(element))
        self._merge_footnotes(footnotes, self._collect_sidenotes_column(element))
        self._merge_footnotes(footnotes, self._collect_aside_footnotes(element))

        footnote_inline_refs = element.select(FOOTNOTE_INLINE_REFERENCES)
        sup_groups: Dict[int, List[dict]] = {}

        footnotes_by_original_id: Dict[str, Tuple[str, FootnoteData]] = {}
        for num, data in footnotes.items():
            footnotes_by_original_id[data.original_id.lower()] = (str(num), data)

        for el in footnote_inline_refs:
            if not el or el.parent is None:
                continue
            if not el.get_text().strip():
                continue

            try:
                is_arxiv = sv.match("cite.ltx_cite", el)
            except Exception:
                is_arxiv = False

            if is_arxiv:
                refs_list: List[Tag] = []
                for link in el.select("a"):
                    href = link.get("href", "")
                    if not href:
                        continue
                    parts = href.split("/")
                    m = re.search(r"bib\.bib(\d+)", parts[-1] if parts else "")
                    if not m:
                        continue
                    entry = footnotes_by_original_id.get(m.group(1).lower())
                    if not entry:
                        continue
                    fn_num, fn_data = entry
                    ref_id = self._make_ref_id(fn_num, len(fn_data.refs))
                    fn_data.refs.append(ref_id)
                    refs_list.append(self._create_footnote_reference(fn_num, ref_id))
                if refs_list:
                    container = self._find_outer_footnote_container(el)
                    frag_soup = BeautifulSoup("", "lxml")
                    for i, ref in enumerate(refs_list):
                        if i > 0:
                            frag_soup.append(NavigableString(" "))
                        frag_soup.append(ref)
                    container.replace_with(*list(frag_soup.children))
                continue

            footnote_id = ""
            for extractor in _INLINE_REF_EXTRACTORS:
                try:
                    if sv.match(extractor["selector"], el):
                        footnote_id = extractor["extract"](el)
                        break
                except Exception:
                    continue

            if not footnote_id:
                href = el.get("href", "")
                if href:
                    footnote_id = re.sub(r"^[#]", "", href).lower()

            if footnote_id:
                footnote_entry = footnotes_by_original_id.get(footnote_id.lower())
                if footnote_entry:
                    fn_num_str, fn_data = footnote_entry
                    container = self._find_outer_footnote_container(el)
                    is_sup = container.name == "sup"

                    if is_sup and id(container) in sup_groups:
                        if any(r["footnote_number"] == fn_num_str for r in sup_groups[id(container)]):
                            continue

                    ref_id = self._make_ref_id(fn_num_str, len(fn_data.refs))
                    fn_data.refs.append(ref_id)

                    if is_sup:
                        sup_groups.setdefault(id(container), []).append(
                            {"footnote_number": fn_num_str, "ref_id": ref_id}
                        )
                    else:
                        self._replace_container_preserving_text(
                            container, self._create_footnote_reference(fn_num_str, ref_id)
                        )

        unmatched = [(str(num), data) for num, data in footnotes.items() if not data.refs]

        if unmatched:
            footnote_id_map: Dict[str, Tuple[str, FootnoteData]] = {}
            footnote_num_map: Dict[str, Tuple[str, FootnoteData]] = {}
            for num_str, data in unmatched:
                footnote_id_map[data.original_id] = (num_str, data)
                footnote_num_map[num_str] = (num_str, data)

            def is_inside_footnotes(check_el: Tag) -> bool:
                c = closest(check_el, '[id^="fnref:"]')
                if c:
                    return True
                c = closest(check_el, "#footnotes")
                if c:
                    return True
                for g in self.pending_removals:
                    if isinstance(g, Tag) and _dom_contains(g, check_el):
                        return True
                return False

            def assign_ref(assign_el: Tag, entry: Tuple[str, FootnoteData]) -> None:
                fn_num_str, fn_data = entry
                ref_id = self._make_ref_id(fn_num_str, len(fn_data.refs))
                fn_data.refs.append(ref_id)
                cont = self._find_outer_footnote_container(assign_el)
                self._replace_container_preserving_text(cont, self._create_footnote_reference(fn_num_str, ref_id))

            for link in element.select('a[href*="#"]'):
                if link.parent is None or is_inside_footnotes(link):
                    continue
                fragment = _get_href_fragment(link)
                if not fragment:
                    continue
                entry = footnote_id_map.get(fragment)
                if not entry:
                    continue
                text = link.get_text().strip()
                if not _FOOTNOTE_MARKER_RE.match(text):
                    continue
                assign_ref(link, entry)

            has_unmatched = any(not d.refs for d in footnotes.values())
            if has_unmatched:
                for check_el in element.select("sup, span.footnote-ref"):
                    if check_el.parent is None:
                        continue
                    el_id = check_el.get("id", "") or ""
                    if el_id.startswith("fnref:"):
                        continue
                    if closest(check_el, "#footnotes"):
                        continue
                    text = check_el.get_text().strip()
                    m = _FOOTNOTE_MARKER_RE.match(text)
                    if not m:
                        continue
                    entry = footnote_num_map.get(m.group(1)) or footnote_id_map.get(m.group(1))
                    if not entry or entry[1].refs:
                        continue
                    assign_ref(check_el, entry)

        for container_id, refs_list in sup_groups.items():
            container_el = None
            for el_ref in footnote_inline_refs:
                outer = self._find_outer_footnote_container(el_ref)
                if id(outer) == container_id:
                    container_el = outer
                    break
            if not container_el:
                continue
            frag_soup = BeautifulSoup("", "lxml")
            for ref_info in refs_list:
                frag_soup.append(self._create_footnote_reference(ref_info["footnote_number"], ref_info["ref_id"]))
            container_el.replace_with(*list(frag_soup.children))

        new_list = self.doc.new_tag("div")
        new_list["id"] = "footnotes"
        ordered_list = self.doc.new_tag("ol")

        all_footnotes: FootnoteCollection = {}
        all_footnotes.update(sidenotes)
        all_footnotes.update(footnotes)

        for number in sorted(all_footnotes.keys()):
            data = all_footnotes[number]
            ordered_list.append(self.create_footnote_item(int(number), data.content, data.refs))

        for lst in element.select(FOOTNOTE_LIST_SELECTORS):
            lst.decompose()

        for el in self.pending_removals:
            if isinstance(el, Tag) and el.parent is not None:
                el.decompose()

        _remove_orphaned_dividers(element)

        if ordered_list.children:
            new_list.append(ordered_list)
            element.append(new_list)


def _dom_contains(parent: Tag, child: Tag) -> bool:
    current = child.parent
    while current is not None:
        if current is parent:
            return True
        current = current.parent if hasattr(current, "parent") else None
    return False


def _dom_contains_any(parent: Tag, children: list) -> bool:
    for child in children:
        if parent is child or _dom_contains(parent, child):
            return True
    return False


def _remove_orphaned_dividers(element: Tag) -> None:
    while True:
        node = list(element.children)[0] if list(element.children) else None
        while node is not None and is_text_node(node) and not str(node).strip():
            node = node.next_sibling
        if node is not None and isinstance(node, Tag) and node.name == "hr":
            node.decompose()
        else:
            break

    while True:
        children = list(element.children)
        node = children[-1] if children else None
        while node is not None and is_text_node(node) and not str(node).strip():
            node = node.previous_sibling
        if node is not None and isinstance(node, Tag) and node.name == "hr":
            node.decompose()
        else:
            break

    for hr in list(element.select("hr")):
        if hr.parent is None:
            continue
        next_node = hr.next_sibling
        while next_node is not None and is_text_node(next_node) and not str(next_node).strip():
            next_node = next_node.next_sibling
        if next_node is not None and isinstance(next_node, Tag) and next_node.name == "hr":
            hr.decompose()


def standardize_footnotes(element: Tag) -> None:
    soup = _get_soup(element)
    handler = FootnoteHandler(soup)
    handler.standardize_footnotes(element)
