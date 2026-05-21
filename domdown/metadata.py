from __future__ import annotations

import re
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

from bs4 import Tag

from domdown.types import DomdownMetadata, MetaTagItem
from domdown.utils import count_words


class MetadataExtractor:
    @staticmethod
    def extract(
        doc: Tag,
        schema_org_data: Any,
        meta_tags: List[MetaTagItem],
    ) -> DomdownMetadata:
        domain = ""
        url = ""

        try:
            url = ""
            if not url:
                url = (
                    MetadataExtractor.get_meta_content(meta_tags, "property", "og:url")
                    or MetadataExtractor.get_meta_content(meta_tags, "property", "twitter:url")
                    or MetadataExtractor.get_schema_property(schema_org_data, "url")
                    or MetadataExtractor.get_schema_property(schema_org_data, "mainEntityOfPage.url")
                    or MetadataExtractor.get_schema_property(schema_org_data, "mainEntity.url")
                    or MetadataExtractor.get_schema_property(schema_org_data, "WebSite.url")
                    or (
                        lambda: (lambda el: el.get("href", "") if el else "")(doc.select_one('link[rel="canonical"]'))
                    )()
                    or ""
                )

            if url:
                try:
                    parsed = urlparse(url)
                    domain = re.sub(r"^www\.", "", parsed.hostname or "")
                except Exception:
                    pass
        except Exception:
            base_tag = doc.select_one("base[href]")
            if base_tag:
                try:
                    url = base_tag.get("href", "")
                    parsed = urlparse(url)
                    domain = re.sub(r"^www\.", "", parsed.hostname or "")
                except Exception:
                    pass

        site_name = MetadataExtractor.get_site_name(schema_org_data, meta_tags)
        best_title = MetadataExtractor.get_best_title(doc, schema_org_data, meta_tags, domain, site_name)
        title, detected_site_name = MetadataExtractor.clean_title(best_title, site_name)
        author = MetadataExtractor.get_author(doc, schema_org_data, meta_tags)
        author_as_site = author if author and "," not in author else ""
        site = site_name or detected_site_name or author_as_site or domain or ""

        return DomdownMetadata(
            title=title,
            description=MetadataExtractor.get_description(doc, schema_org_data, meta_tags),
            domain=domain,
            favicon=MetadataExtractor.get_favicon(doc, url, meta_tags),
            image=MetadataExtractor.get_image(doc, schema_org_data, meta_tags),
            language=MetadataExtractor.get_language(doc, schema_org_data, meta_tags),
            published=MetadataExtractor.get_published(doc, schema_org_data, meta_tags),
            author=author,
            site=site,
            schema_org_data=schema_org_data,
            word_count=0,
            parse_time=0.0,
        )

    @staticmethod
    def is_placeholder_value(s: str) -> bool:
        if re.search(r"[{}]", s) or re.match(r"^#[a-zA-Z]", s):
            return True
        if not re.search(r"[\w]", s):
            return True
        return False

    @staticmethod
    def first_valid(thunks: List[Callable[[], str]]) -> str:
        for thunk in thunks:
            v = thunk()
            if v and not MetadataExtractor.is_placeholder_value(v):
                return v
        return ""

    @staticmethod
    def get_author(doc: Tag, schema_org_data: Any, meta_tags: List[MetaTagItem]) -> str:
        authors_string: Optional[str] = None

        authors_string = MetadataExtractor.first_valid(
            [
                lambda: MetadataExtractor.get_meta_content(meta_tags, "name", "sailthru.author"),
                lambda: MetadataExtractor.get_meta_content(meta_tags, "property", "article:author"),
                lambda: MetadataExtractor.get_meta_content(meta_tags, "property", "author"),
                lambda: MetadataExtractor.get_meta_content(meta_tags, "name", "author"),
                lambda: MetadataExtractor.get_meta_content(meta_tags, "name", "byl"),
                lambda: MetadataExtractor.get_meta_content(meta_tags, "name", "authorList"),
            ]
        )
        if authors_string:
            cleaned = MetadataExtractor.clean_author_string(authors_string)
            if cleaned:
                return cleaned

        authors_strings: List[str] = [
            s
            for s in MetadataExtractor.get_meta_contents(meta_tags, "name", "citation_author")
            if not MetadataExtractor.is_placeholder_value(s)
        ]
        if len(authors_strings) == 0:
            authors_strings = [
                s
                for s in MetadataExtractor.get_meta_contents(meta_tags, "property", "dc.creator")
                if not MetadataExtractor.is_placeholder_value(s)
            ]
        if len(authors_strings) > 0:
            parts_list: List[str] = []
            for s in authors_strings:
                if "," not in s:
                    parts_list.append(s.strip())
                else:
                    m = re.match(r"(.*),\s(.*)", s)
                    if m:
                        parts_list.append(f"{m.group(2)} {m.group(1)}")
                    else:
                        parts_list.append(s.strip())
            return ", ".join(parts_list)

        schema_authors = MetadataExtractor.get_schema_property(
            schema_org_data, "author.name"
        ) or MetadataExtractor.get_schema_property(schema_org_data, "author.[].name")

        if schema_authors:
            parts = [
                part.strip().rstrip(",").strip()
                for part in schema_authors.split(",")
                if part.strip().rstrip(",").strip()
                and not MetadataExtractor.is_placeholder_value(part.strip().rstrip(",").strip())
            ]
            if parts:
                unique_schema_authors = list(dict.fromkeys(parts))
                if len(unique_schema_authors) > 10:
                    unique_schema_authors = unique_schema_authors[:10]
                return ", ".join(unique_schema_authors)

        rel_author_els = doc.select('a[rel~="author"], address[rel~="author"]')
        if 0 < len(rel_author_els) <= 3:
            rel_names: List[str] = []
            for el in rel_author_els:
                text = MetadataExtractor.get_visible_text(el)
                lower = text.lower()
                if (
                    text
                    and len(text) < 100
                    and lower != "author"
                    and lower != "authors"
                    and not MetadataExtractor.is_placeholder_value(text)
                ):
                    rel_names.append(text)
            unique_rel_names = list(dict.fromkeys(rel_names))
            if unique_rel_names:
                return ", ".join(unique_rel_names)

        collected_authors_from_dom: List[str] = []

        def add_dom_author(value: Optional[str]) -> None:
            if not value:
                return
            for name_part in value.split(","):
                cleaned_name = re.sub(r"\s+", " ", name_part).strip().rstrip(",").strip()
                lower_cleaned_name = cleaned_name.lower()
                if (
                    cleaned_name
                    and lower_cleaned_name != "author"
                    and lower_cleaned_name != "authors"
                    and not MetadataExtractor.is_placeholder_value(cleaned_name)
                ):
                    collected_authors_from_dom.append(cleaned_name)

        dom_author_selectors: List[Tuple[str, Optional[int]]] = [
            ('[itemprop="author"]', None),
            (".author", 3),
            ('[href*="/author/"]', 3),
            (".authors a", 3),
        ]

        for selector, max_matches in dom_author_selectors:
            matches = doc.select(selector)
            if max_matches and len(matches) > max_matches:
                continue
            for el in matches:
                add_dom_author(MetadataExtractor.get_author_name(el))

        if collected_authors_from_dom:
            unique_authors = list(dict.fromkeys([n.strip() for n in collected_authors_from_dom if n.strip()]))
            if len(unique_authors) > 1:
                unique_authors = [a for a in unique_authors if not any(b != a and a in b for b in unique_authors)]
            if unique_authors:
                if len(unique_authors) > 10:
                    unique_authors = unique_authors[:10]
                return ", ".join(unique_authors)

        h1 = doc.select_one("h1")
        if h1:
            sibling = h1.next_sibling
            while sibling is not None:
                if not isinstance(sibling, Tag):
                    sibling = sibling.next_sibling
                    continue
                sibling_text = sibling.get_text().strip()
                child_els = sibling.select("p, time")
                has_date_child = any(MetadataExtractor.parse_date_text(el.get_text().strip()) for el in child_els)
                has_sibling_date = bool(MetadataExtractor.parse_date_text(sibling_text)) or has_date_child
                if has_sibling_date:
                    links = sibling.select("a")
                    if len(links) == 1:
                        link_text = links[0].get_text().strip().replace("\u00a0", " ")
                        if 0 < len(link_text) < 100 and not MetadataExtractor.parse_date_text(link_text):
                            return link_text
                    if has_date_child and len(sibling_text) < 300:
                        for p in child_els:
                            if p.name != "p":
                                continue
                            p_text = p.get_text().strip().replace("\u00a0", " ")
                            if 0 < len(p_text) < 150 and not MetadataExtractor.parse_date_text(p_text):
                                return p_text
                sibling = sibling.next_sibling
                count = 0
                while sibling is not None and count < 100:
                    if isinstance(sibling, Tag):
                        break
                    sibling = sibling.next_sibling
                    count += 1

            byline_scope: Optional[Tag] = h1
            for _depth in range(3):
                if byline_scope is None:
                    break
                byline_candidate = byline_scope.previous_sibling
                while byline_candidate is not None and not isinstance(byline_candidate, Tag):
                    byline_candidate = byline_candidate.previous_sibling
                for _i in range(3):
                    if byline_candidate is None:
                        break
                    byline_result = MetadataExtractor.extract_byline(byline_candidate)
                    if byline_result:
                        return byline_result
                    nxt = byline_candidate.previous_sibling
                    while nxt is not None and not isinstance(nxt, Tag):
                        nxt = nxt.previous_sibling
                    byline_candidate = nxt

                byline_candidate = byline_scope.next_sibling
                while byline_candidate is not None and not isinstance(byline_candidate, Tag):
                    byline_candidate = byline_candidate.next_sibling
                for _i in range(3):
                    if byline_candidate is None:
                        break
                    byline_result = MetadataExtractor.extract_byline(byline_candidate)
                    if byline_result:
                        return byline_result
                    nxt = byline_candidate.next_sibling
                    while nxt is not None and not isinstance(nxt, Tag):
                        nxt = nxt.next_sibling
                    byline_candidate = nxt

                byline_scope = byline_scope.parent

        return ""

    @staticmethod
    def extract_byline(el: Tag) -> Optional[str]:
        candidates = [el] + el.select("p, span, address")
        for candidate in candidates:
            if not isinstance(candidate, Tag):
                continue
            text = candidate.get_text().strip().replace("\u00a0", " ")
            if 0 < len(text) < 50:
                m = re.match(r"^By\s+([A-Z].+)$", text, re.IGNORECASE)
                if m:
                    return m.group(1).strip()
        return None

    @staticmethod
    def clean_author_string(s: str) -> str:
        s = re.sub(r"^by\s+", "", s, flags=re.IGNORECASE)
        s = re.sub(r"\(?\s*https?://\S+\s*\)?", "", s, flags=re.IGNORECASE)
        s = re.sub(r",?\s+and\s+", ", ", s, flags=re.IGNORECASE)
        s = re.sub(r"\s*[-\u2013\u2014|]\s*$", "", s)
        return s.strip()

    @staticmethod
    def get_site_name(schema_org_data: Any, meta_tags: List[MetaTagItem]) -> str:
        candidate = MetadataExtractor.first_valid(
            [
                lambda: MetadataExtractor.get_schema_property(schema_org_data, "publisher.name"),
                lambda: MetadataExtractor.get_meta_content(meta_tags, "property", "og:site_name"),
                lambda: MetadataExtractor.get_meta_content(meta_tags, "name", "og:site_name"),
                lambda: MetadataExtractor.get_schema_property(schema_org_data, "WebSite.name"),
                lambda: MetadataExtractor.get_schema_property(schema_org_data, "sourceOrganization.name"),
                lambda: MetadataExtractor.get_meta_content(meta_tags, "name", "copyright"),
                lambda: MetadataExtractor.get_schema_property(schema_org_data, "copyrightHolder.name"),
                lambda: MetadataExtractor.get_schema_property(schema_org_data, "isPartOf.name"),
                lambda: MetadataExtractor.get_meta_content(meta_tags, "name", "application-name"),
            ]
        )

        if candidate and count_words(candidate) > 6:
            return ""

        return candidate

    @staticmethod
    def get_best_title(
        doc: Tag,
        schema_org_data: Any,
        meta_tags: List[MetaTagItem],
        domain: str,
        site_name: str,
    ) -> str:
        candidates = [
            c
            for c in [
                MetadataExtractor.get_meta_content(meta_tags, "property", "og:title"),
                MetadataExtractor.get_meta_content(meta_tags, "name", "twitter:title"),
                MetadataExtractor.get_schema_property(schema_org_data, "headline"),
                MetadataExtractor.get_meta_content(meta_tags, "name", "title"),
                MetadataExtractor.get_meta_content(meta_tags, "name", "sailthru.title"),
                (lambda el: el.get_text().strip() if el else "")(doc.select_one("title")),
                (lambda el: el.get_text().strip() if el else "")(doc.select_one("h1")),
            ]
            if c and not MetadataExtractor.is_placeholder_value(c)
        ]

        if not candidates:
            return ""

        author_meta = MetadataExtractor.get_meta_content(
            meta_tags, "property", "author"
        ) or MetadataExtractor.get_meta_content(meta_tags, "name", "author")

        author_norm = author_meta.strip().lower()
        site_norm = site_name.strip().lower()
        domain_norm = re.sub(r"[^a-z0-9]", "", re.sub(r"\.[^.]+$", "", domain).lower()) if domain else ""

        for c in candidates:
            if not MetadataExtractor.is_site_identifier(c, author_norm, site_norm, domain_norm):
                return c
        return candidates[0]

    @staticmethod
    def is_site_identifier(
        candidate: str,
        author_norm: str,
        site_norm: str,
        domain_norm: str,
    ) -> bool:
        norm = candidate.strip().lower()

        if author_norm and norm == author_norm:
            return True
        if site_norm and norm == site_norm:
            return True

        if domain_norm:
            candidate_norm = re.sub(r"[^a-z0-9]", "", norm)
            if candidate_norm == domain_norm:
                return True

        return False

    @staticmethod
    def clean_title(title: str, site_name: str) -> Tuple[str, str]:
        if not title:
            return title, ""

        separators = r"[|\-–—/·]"

        if site_name and site_name.lower() != title.lower() and count_words(site_name) <= 6:
            site_name_lower = site_name.lower()

            site_name_escaped = re.escape(site_name)
            patterns = [
                rf"\s*{separators}\s*{site_name_escaped}\s*$",
                rf"^\s*{site_name_escaped}\s*{separators}\s*",
            ]

            for pattern in patterns:
                regex = re.compile(pattern, re.IGNORECASE)
                if regex.search(title):
                    return regex.sub("", title).strip(), site_name

            all_sep_pattern = re.compile(rf"\s+{separators}\s+")
            all_positions: List[Tuple[int, int]] = []
            for m in all_sep_pattern.finditer(title):
                all_positions.append((m.start(), len(m.group(0))))

            if all_positions:
                last_idx, last_len = all_positions[-1]
                last_segment = title[last_idx + last_len :].strip().lower()
                if last_segment and last_segment in site_name_lower:
                    cut_index = last_idx
                    for i in range(len(all_positions) - 2, -1, -1):
                        pos_idx, pos_len = all_positions[i]
                        segment = title[pos_idx + pos_len : cut_index].strip()
                        if count_words(segment) > 3:
                            break
                        cut_index = pos_idx
                    return title[:cut_index].strip(), site_name

                first_idx, first_len = all_positions[0]
                prefix_segment = title[:first_idx].strip().lower()
                if prefix_segment and prefix_segment in site_name_lower:
                    cut_index = first_idx + first_len
                    for i in range(1, len(all_positions)):
                        pos_idx, pos_len = all_positions[i]
                        segment = title[cut_index:pos_idx].strip()
                        if count_words(segment) > 3:
                            break
                        cut_index = pos_idx + pos_len
                    return title[cut_index:].strip(), site_name

        strong_result = MetadataExtractor.try_separator_split(
            title,
            re.compile(r"\s+([|/·])\s+"),
            suffix_only=False,
            guard=lambda t_w, s_w: s_w <= 3 and t_w >= 2 and t_w >= s_w * 2,
        )
        if strong_result:
            return strong_result

        dash_result = MetadataExtractor.try_separator_split(
            title,
            re.compile(r"\s+[-–—]\s+"),
            suffix_only=True,
            guard=lambda t_w, s_w: s_w <= 2 and t_w >= 2 and t_w > s_w,
        )
        if dash_result:
            return dash_result

        return title.strip(), ""

    @staticmethod
    def try_separator_split(
        title: str,
        pattern: re.Pattern,
        suffix_only: bool,
        guard: Callable[[int, int], bool],
    ) -> Optional[Tuple[str, str]]:
        positions: List[Tuple[int, int]] = []
        for m in pattern.finditer(title):
            positions.append((m.start(), len(m.group(0))))
        if not positions:
            return None

        last_idx, last_len = positions[-1]
        suffix_title = title[:last_idx].strip()
        suffix_site = title[last_idx + last_len :].strip()
        if guard(count_words(suffix_title), count_words(suffix_site)):
            return suffix_title, suffix_site

        if not suffix_only:
            first_idx, first_len = positions[0]
            prefix_site = title[:first_idx].strip()
            prefix_title = title[first_idx + first_len :].strip()
            if guard(count_words(prefix_title), count_words(prefix_site)):
                return prefix_title, prefix_site

        return None

    @staticmethod
    def get_description(
        doc: Tag,
        schema_org_data: Any,
        meta_tags: List[MetaTagItem],
    ) -> str:
        return MetadataExtractor.first_valid(
            [
                lambda: MetadataExtractor.get_meta_content(meta_tags, "name", "description"),
                lambda: MetadataExtractor.get_meta_content(meta_tags, "property", "description"),
                lambda: MetadataExtractor.get_meta_content(meta_tags, "property", "og:description"),
                lambda: MetadataExtractor.get_schema_property(schema_org_data, "description"),
                lambda: MetadataExtractor.get_meta_content(meta_tags, "name", "twitter:description"),
                lambda: MetadataExtractor.get_meta_content(meta_tags, "name", "sailthru.description"),
            ]
        )

    @staticmethod
    def get_image(
        doc: Tag,
        schema_org_data: Any,
        meta_tags: List[MetaTagItem],
    ) -> str:
        return (
            MetadataExtractor.get_meta_content(meta_tags, "property", "og:image")
            or MetadataExtractor.get_meta_content(meta_tags, "name", "twitter:image")
            or MetadataExtractor.get_schema_property(schema_org_data, "image.url")
            or MetadataExtractor.get_meta_content(meta_tags, "name", "sailthru.image.full")
            or ""
        )

    @staticmethod
    def get_language(
        doc: Tag,
        schema_org_data: Any,
        meta_tags: List[MetaTagItem],
    ) -> str:
        html_el = doc.find_parent("html")
        if html_el is None:
            root = doc
            while root.parent is not None:
                root = root.parent
            if isinstance(root, Tag) and root.name == "html":
                html_el = root
            elif isinstance(root, Tag):
                html_el = root.select_one("html")

        if html_el:
            html_lang = html_el.get("lang")
            if html_lang and isinstance(html_lang, str):
                return MetadataExtractor.normalize_lang_code(html_lang.strip())

        content_lang = MetadataExtractor.get_meta_content(
            meta_tags, "name", "content-language"
        ) or MetadataExtractor.get_meta_content(meta_tags, "property", "og:locale")
        if content_lang:
            return MetadataExtractor.normalize_lang_code(content_lang)

        http_equiv_el = doc.select_one('meta[http-equiv="Content-Language"]')
        if http_equiv_el:
            content = http_equiv_el.get("content")
            if content and isinstance(content, str):
                return MetadataExtractor.normalize_lang_code(content.strip())

        schema_lang = MetadataExtractor.get_schema_property(schema_org_data, "inLanguage")
        if schema_lang:
            return MetadataExtractor.normalize_lang_code(schema_lang)

        return ""

    @staticmethod
    def normalize_lang_code(code: str) -> str:
        return code.replace("_", "-")

    @staticmethod
    def get_favicon(
        doc: Tag,
        base_url: str,
        meta_tags: List[MetaTagItem],
    ) -> str:
        icon_from_meta = MetadataExtractor.get_meta_content(meta_tags, "property", "og:image:favicon")
        if icon_from_meta:
            return icon_from_meta

        icon_link_el = doc.select_one("link[rel='icon']")
        if icon_link_el:
            href = icon_link_el.get("href")
            if href:
                return href

        shortcut_link_el = doc.select_one("link[rel='shortcut icon']")
        if shortcut_link_el:
            href = shortcut_link_el.get("href")
            if href:
                return href

        if base_url and re.match(r"^https?://", base_url):
            try:
                return urljoin(base_url, "/favicon.ico")
            except Exception:
                pass

        return ""

    @staticmethod
    def get_published(
        doc: Tag,
        schema_org_data: Any,
        meta_tags: List[MetaTagItem],
    ) -> str:
        result = MetadataExtractor.first_valid(
            [
                lambda: MetadataExtractor.get_schema_property(schema_org_data, "datePublished"),
                lambda: MetadataExtractor.get_meta_content(meta_tags, "name", "publishDate"),
                lambda: MetadataExtractor.get_meta_content(meta_tags, "property", "article:published_time"),
                lambda: (lambda el: (el.get("title", "").strip() if el else ""))(
                    doc.select_one('abbr[itemprop="datePublished"]')
                ),
                lambda: MetadataExtractor.get_time_element(doc),
                lambda: MetadataExtractor.get_meta_content(meta_tags, "name", "sailthru.date"),
            ]
        )
        if result:
            return result

        h1 = doc.select_one("h1")
        if h1:
            sibling = h1.next_sibling
            tag_count = 0
            while sibling is not None and tag_count < 3:
                if not isinstance(sibling, Tag):
                    sibling = sibling.next_sibling
                    continue
                tag_count += 1
                for child in sibling.select("p, time"):
                    parsed = MetadataExtractor.parse_date_text(child.get_text().strip())
                    if parsed:
                        return parsed
                parsed = MetadataExtractor.parse_date_text(sibling.get_text().strip())
                if parsed:
                    return parsed
                sibling = sibling.next_sibling

        return ""

    @staticmethod
    def get_meta_content(
        meta_tags: List[MetaTagItem],
        attr: str,
        value: str,
    ) -> str:
        results = MetadataExtractor.get_meta_contents(meta_tags, attr, value)
        return results[0] if results else ""

    @staticmethod
    def get_meta_contents(
        meta_tags: List[MetaTagItem],
        attr: str,
        value: str,
    ) -> List[str]:
        results: List[str] = []
        value_lower = value.lower()
        for tag in meta_tags:
            attribute_value = tag.name if attr == "name" else tag.property
            if attribute_value and attribute_value.lower() == value_lower:
                results.append((tag.content or "").strip())
        return results

    @staticmethod
    def get_time_element(doc: Tag) -> str:
        elements = doc.select("time")
        if not elements:
            return ""
        element = elements[0]
        datetime = element.get("datetime")
        if datetime and isinstance(datetime, str):
            return datetime.strip()
        text = element.get_text().strip()
        return text

    MONTH_MAP: Dict[str, str] = {
        "january": "01",
        "february": "02",
        "march": "03",
        "april": "04",
        "may": "05",
        "june": "06",
        "july": "07",
        "august": "08",
        "september": "09",
        "october": "10",
        "november": "11",
        "december": "12",
    }

    @staticmethod
    def parse_date_text(text: str) -> str:
        months = "(January|February|March|April|May|June|July|August|September|October|November|December)"

        m = re.match(
            rf"\b(\d{{1,2}})\s+{months}\s+(\d{{4}})\b",
            text,
            re.IGNORECASE,
        )
        if m:
            day = m.group(1).zfill(2)
            month = MetadataExtractor.MONTH_MAP[m.group(2).lower()]
            return f"{m.group(3)}-{month}-{day}T00:00:00+00:00"

        m = re.match(
            rf"\b{months}\s+(\d{{1,2}}),?\s+(\d{{4}})\b",
            text,
            re.IGNORECASE,
        )
        if m:
            month = MetadataExtractor.MONTH_MAP[m.group(1).lower()]
            day = m.group(2).zfill(2)
            return f"{m.group(3)}-{month}-{day}T00:00:00+00:00"

        return ""

    @staticmethod
    def get_visible_text(el: Tag) -> str:
        clone = _clone_element(el)
        for s in clone.select("script, style, noscript"):
            s.decompose()
        return re.sub(r"\s+", " ", clone.get_text()).strip()

    @staticmethod
    def get_author_name(el: Tag) -> str:
        clone = _clone_element(el)
        for s in clone.select("script, style, noscript"):
            s.decompose()
        text = re.sub(r"\s+", " ", clone.get_text()).strip()
        if not text:
            return ""

        for child in clone.select("span, a, p"):
            child_text = re.sub(r"\s+", " ", child.get_text()).strip()
            if 2 <= len(child_text) <= 50 and child_text != text:
                return child_text

        return text if len(text) <= 100 else ""

    @staticmethod
    def get_schema_property(
        schema_org_data: Any,
        property_path: str,
        default_value: str = "",
    ) -> str:
        if not schema_org_data:
            return default_value

        def search_schema(
            data: Any,
            props: List[str],
            full_path: str,
            is_exact_match: bool = True,
        ) -> List[str]:
            if isinstance(data, str):
                return [data] if len(props) == 0 else []

            if data is None or not isinstance(data, (dict, list)):
                return []

            if isinstance(data, list):
                if not props:
                    return []
                current_prop = props[0]
                if re.match(r"^\[\d+\]$", current_prop):
                    index = int(current_prop[1:-1])
                    if index < len(data) and data[index] is not None:
                        return search_schema(data[index], props[1:], full_path, is_exact_match)
                    return []

                if len(props) == 0 and all(isinstance(item, (str, int, float)) for item in data):
                    return [str(item) for item in data]

                results: List[str] = []
                for item in data:
                    results.extend(search_schema(item, props, full_path, is_exact_match))
                return results

            current_prop = props[0] if props else None
            remaining_props = props[1:] if props else []

            if not current_prop:
                if isinstance(data, str):
                    return [data]
                if isinstance(data, dict) and "name" in data:
                    return [data["name"]]
                return []

            if current_prop in data:
                return search_schema(
                    data[current_prop],
                    remaining_props,
                    f"{full_path}.{current_prop}" if full_path else current_prop,
                    True,
                )

            if not is_exact_match:
                nested_results: List[str] = []
                for key, val in data.items():
                    if isinstance(val, (dict, list)):
                        results = search_schema(
                            val,
                            props,
                            f"{full_path}.{key}" if full_path else key,
                            False,
                        )
                        nested_results.extend(results)
                if nested_results:
                    return nested_results

            return []

        try:
            props_list = property_path.split(".")
            results = search_schema(schema_org_data, props_list, "", True)
            if not results:
                results = search_schema(schema_org_data, props_list, "", False)
            unique = list(dict.fromkeys([r for r in results if r]))
            return ", ".join(unique) if unique else default_value
        except Exception:
            return default_value


def _clone_element(el: Tag) -> Tag:
    parent = el.parent
    idx = None
    if parent is not None:
        idx = list(parent.children).index(el)

    import copy

    clone = copy.copy(el)

    if parent is not None and idx is not None:
        pass

    return clone
