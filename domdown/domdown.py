from __future__ import annotations

import copy
import json
import re
import time
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, Comment, Tag

from domdown.constants import (
    BLOCK_ELEMENTS_SELECTOR,
    ENTRY_POINT_ELEMENTS,
    HIDDEN_EXACT_SKIP_SELECTOR,
    MOBILE_WIDTH,
    UNSAFE_CSS_CLASS_RE,
)
from domdown.elements.callouts import standardize_callouts
from domdown.elements.footnotes import FOOTNOTE_SECTION_RE, standardize_footnotes
from domdown.extractor_registry import ExtractorRegistry
from domdown.extractors._base import BaseExtractor, ExtractorOptions
from domdown.metadata import MetadataExtractor
from domdown.removals.content_patterns import remove_by_content_pattern, remove_eyebrow_label
from domdown.removals.hidden import remove_hidden_elements
from domdown.removals.metadata_block import remove_metadata_block
from domdown.removals.scoring import ContentScorer
from domdown.removals.selectors import remove_by_selector
from domdown.removals.small_images import find_small_images, remove_small_images
from domdown.standardize import standardize_content
from domdown.types import DebugInfo, DebugRemoval, DomdownMetadata, DomdownOptions, DomdownResponse, MetaTagItem
from domdown.utils import count_words, get_computed_style
from domdown.utils.dom import (
    closest,
    contains,
    decode_html_entities,
    get_class_name,
    is_dangerous_url,
    parse_html,
    serialize_html,
)

STANDARD_VARIABLE_KEYS = frozenset(["title", "author", "published", "site", "description", "image", "language"])

_URL_WIDTH_PATTERN = re.compile(r"(?:width[=:/]|[/,?&]w[_:=])(\d+)")


class Domdown:
    def __init__(self, doc: Tag, options: Optional[DomdownOptions] = None):
        self.doc = doc
        self.options = options or DomdownOptions()
        self.debug = self.options.debug
        self._schema_org_data: Any = None
        self._schema_org_extracted = False
        self._meta_tags: Optional[List[MetaTagItem]] = None
        self._metadata: Optional[DomdownMetadata] = None
        self._mobile_styles: Optional[List[Dict[str, str]]] = None
        self._small_images: Optional[Set[str]] = None
        self._in_extractor_pipeline_run = False

    def _get_schema_org_data(self) -> Any:
        if not self._schema_org_extracted:
            self._schema_org_data = self._extract_schema_org_data(self.doc)
            self._schema_org_extracted = True
        return self._schema_org_data

    def parse(self) -> DomdownResponse:
        if self._get_body() is not None:
            self._normalize_attributes(self._get_body())
            self._resolve_noscript_images(self._get_body())

        result = self._parse_internal()

        if result.word_count < 200:
            self._log("Initial parse returned very little content, trying again")
            retry_result = self._parse_internal(override_options=DomdownOptions(remove_partial_selectors=False))
            if retry_result.word_count > result.word_count * 2:
                self._log("Retry produced more content")
                result = retry_result

        if result.word_count < 50:
            self._log("Still very little content, retrying without hidden-element removal")
            hidden_retry = self._parse_internal(override_options=DomdownOptions(remove_hidden_elements=False))
            if hidden_retry.word_count > result.word_count * 2:
                self._log("Hidden-element retry produced more content")
                result = hidden_retry

            hidden_selector = self._find_largest_hidden_content_selector()
            if hidden_selector:
                self._log("Retrying with hidden content selector:", hidden_selector)
                hidden_selector_retry = self._parse_internal(
                    override_options=DomdownOptions(
                        remove_hidden_elements=False,
                        remove_partial_selectors=False,
                        content_selector=hidden_selector,
                    )
                )
                if hidden_selector_retry.word_count > result.word_count or (
                    hidden_selector_retry.word_count > max(20, result.word_count * 0.7)
                    and len(hidden_selector_retry.content) < len(result.content)
                ):
                    self._log("Hidden-selector retry produced better focused content")
                    result = hidden_selector_retry

        if result.word_count < 50:
            self._log("Still very little content, retrying without scoring/partial selectors (possible index page)")
            index_retry = self._parse_internal(
                override_options=DomdownOptions(
                    remove_low_scoring=False,
                    remove_partial_selectors=False,
                    remove_content_patterns=False,
                )
            )
            if index_retry.word_count > result.word_count:
                self._log("Index page retry produced more content")
                result = index_retry

        self._strip_unsafe_elements()

        schema_text = self._get_schema_text(result.schema_org_data)
        if schema_text and self._count_html_words(schema_text) > result.word_count * 1.5:
            best_match = self._find_element_by_schema_text(self._get_body(), schema_text)
            if best_match:
                selector = self._get_element_selector(best_match)
                self._log(
                    "Schema.org suggests a better content element, retrying with selector:",
                    selector,
                )
                schema_retry = self._parse_internal(override_options=DomdownOptions(content_selector=selector))
                result = schema_retry
            else:
                self._log("Using schema.org text as content (DOM element not found)")
                result.content = self._sanitize_schema_text_content(schema_text)
                result.word_count = self._count_html_words(schema_text)

        return result

    async def parse_async(self) -> DomdownResponse:
        if self.options.use_async is not False:
            async_result = await self._try_async_extractor(ExtractorRegistry.find_preferred_async_extractor)
            if async_result:
                return async_result

        result = self.parse()

        if result.word_count > 0 or not self.options.use_async:
            return result

        fallback = await self._try_async_extractor(ExtractorRegistry.find_async_extractor)
        return fallback if fallback is not None else result

    async def fetch_async_variables(self) -> Optional[Dict[str, str]]:
        if not self.options.use_async:
            return None

        try:
            url = self.options.url or self._get_doc_url()
            schema_org_data = self._get_schema_org_data()
            extractor_opts = ExtractorOptions(
                include_replies=(
                    self.options.include_replies if self.options.include_replies != "extractors" else "extractors"
                ),
                language=self.options.language,
                fetch=self.options.fetch,
            )
            extractor = ExtractorRegistry.find_preferred_async_extractor(self.doc, url, schema_org_data, extractor_opts)

            if extractor:
                extracted = await extractor.extract_async()
                variables = self._get_extractor_variables(extracted.get("variables"))
                return variables if variables else None
        except Exception as error:
            print(f"Domdown: Error fetching async variables: {error}")

        return None

    async def _try_async_extractor(self, finder: Any) -> Optional[DomdownResponse]:
        try:
            url = self.options.url or self._get_doc_url()
            schema_org_data = self._get_schema_org_data()
            extractor_opts = ExtractorOptions(
                include_replies=(
                    self.options.include_replies if self.options.include_replies != "extractors" else "extractors"
                ),
                language=self.options.language,
                fetch=self.options.fetch,
            )
            extractor = finder(self.doc, url, schema_org_data, extractor_opts)

            if extractor:
                start_time = time.time()
                extracted = await extractor.extract_async()
                page_meta_tags = self._collect_meta_tags()
                metadata = MetadataExtractor.extract(self.doc, schema_org_data, page_meta_tags)
                return self._build_extractor_response(extracted, metadata, start_time, extractor, page_meta_tags)
        except Exception as error:
            print(f"Domdown: Error in async extraction: {error}")

        return None

    def _parse_internal(self, override_options: Optional[DomdownOptions] = None) -> DomdownResponse:
        start_time = time.time()
        profile: Dict[str, float] = {}
        do_profile = self.options.profile

        if not self._get_document_element():
            url = self.options.url or ""
            domain = ""
            if url:
                try:
                    domain = urlparse(url).hostname or ""
                    domain = re.sub(r"^www\.", "", domain)
                except Exception:
                    pass
            return DomdownResponse(
                content="",
                title="",
                description="",
                domain=domain,
                favicon="",
                image="",
                language="",
                parse_time=time.time() - start_time,
                published="",
                author="",
                site="",
                schema_org_data=None,
                word_count=0,
            )

        options = self._merge_options(override_options)
        debug_removals: List[DebugRemoval] = []

        schema_org_data = self._get_schema_org_data()

        if not self._meta_tags:
            self._meta_tags = self._collect_meta_tags()
        page_meta_tags = self._meta_tags

        if not self._metadata:
            self._metadata = MetadataExtractor.extract(self.doc, schema_org_data, page_meta_tags)
        metadata = self._metadata

        if options.remove_images:
            self._remove_images(self.doc)

        try:
            url = options.url or self._get_doc_url()
            extractor_opts = ExtractorOptions(
                include_replies=options.include_replies if options.include_replies != "extractors" else "extractors",
                language=options.language,
                fetch=options.fetch,
            )

            if not self._in_extractor_pipeline_run:
                extractor = ExtractorRegistry.find_extractor(self.doc, url, schema_org_data, extractor_opts)
                if extractor and extractor.can_extract():
                    extracted = extractor.extract()
                    if extracted.get("contentSelector"):
                        self._in_extractor_pipeline_run = True
                        try:
                            pipeline_result = self._parse_internal(
                                override_options=DomdownOptions(
                                    content_selector=extracted["contentSelector"],
                                    remove_low_scoring=False,
                                    remove_hidden_elements=False,
                                )
                            )
                            variables = self._get_extractor_variables(extracted.get("variables"))
                            ext_vars = extracted.get("variables") or {}
                            pipeline_result.title = ext_vars.get("title") or pipeline_result.title
                            pipeline_result.description = ext_vars.get("description") or pipeline_result.description
                            pipeline_result.author = ext_vars.get("author") or pipeline_result.author
                            pipeline_result.published = ext_vars.get("published") or pipeline_result.published
                            pipeline_result.site = ext_vars.get("site") or pipeline_result.site
                            pipeline_result.language = ext_vars.get("language") or pipeline_result.language
                            extractor_type = type(extractor).__name__.replace("Extractor", "").lower()
                            pipeline_result.extractor_type = extractor_type
                            if variables:
                                pipeline_result.variables = variables
                            return pipeline_result
                        finally:
                            self._in_extractor_pipeline_run = False

                    return self._build_extractor_response(extracted, metadata, start_time, extractor, page_meta_tags)

            if self._small_images is None:
                self._small_images = find_small_images(self.doc, self.debug)
            small_images = self._small_images

            if do_profile:
                t = time.time()
            clone = copy.deepcopy(self.doc)
            if do_profile:
                profile["cloneDocument"] = round((time.time() - t) * 1000)

            if do_profile:
                t = time.time()
            if self._mobile_styles is None:
                self._mobile_styles = self._evaluate_media_queries(self.doc)
            mobile_styles = self._mobile_styles
            if do_profile:
                profile["evaluateMediaQueries"] = round((time.time() - t) * 1000)

            if do_profile:
                t = time.time()
            self._flatten_shadow_roots(self.doc, clone)
            if do_profile:
                profile["flattenShadowRoots"] = round((time.time() - t) * 1000)

            if do_profile:
                t = time.time()
            self._resolve_streamed_content(clone)
            if do_profile:
                profile["resolveStreamedContent"] = round((time.time() - t) * 1000)

            if do_profile:
                t = time.time()
            self._apply_mobile_styles(clone, mobile_styles)
            if do_profile:
                profile["applyMobileStyles"] = round((time.time() - t) * 1000)

            if do_profile:
                t = time.time()
            main_content = self._find_main_content(clone, options.content_selector, schema_org_data)
            if do_profile:
                profile["findMainContent"] = round((time.time() - t) * 1000)

            if not main_content:
                fallback_content = ""
                body = self._get_body()
                if body:
                    fallback_content = self._resolve_content_urls(serialize_html(body))
                end_time = time.time()
                result = DomdownResponse(
                    content=fallback_content,
                    word_count=self._count_html_words(fallback_content),
                    parse_time=end_time - start_time,
                )
                self._apply_metadata_to_response(result, metadata, page_meta_tags)
                return result

            if do_profile:
                t = time.time()
            if metadata.published or metadata.author:
                remove_metadata_block(main_content)
            for wbr in main_content.find_all("wbr"):
                wbr.decompose()
            if do_profile:
                profile["removeMetadataBlock"] = round((time.time() - t) * 1000)

            if do_profile:
                t = time.time()
            if options.standardize:
                self._adopt_external_footnotes(main_content, clone)
            if do_profile:
                profile["adoptExternalFootnotes"] = round((time.time() - t) * 1000)

            if do_profile:
                t = time.time()
            if options.standardize:
                standardize_footnotes(main_content)
                standardize_callouts(main_content)
            if do_profile:
                profile["standardizeFootnotesCallouts"] = round((time.time() - t) * 1000)

            if do_profile:
                t = time.time()
            if options.remove_small_images:
                remove_small_images(clone, small_images, self.debug)
            if do_profile:
                profile["removeSmallImages"] = round((time.time() - t) * 1000)

            if do_profile:
                t = time.time()
            if options.remove_hidden_elements:
                remove_hidden_elements(clone, self.debug, debug_removals)
            if do_profile:
                profile["removeHiddenElements"] = round((time.time() - t) * 1000)

            if do_profile:
                t = time.time()
            if options.remove_content_patterns and main_content:
                remove_eyebrow_label(main_content, self.debug, debug_removals)
            if do_profile:
                profile["removeEyebrowLabel"] = round((time.time() - t) * 1000)

            if do_profile:
                t = time.time()
            if options.remove_exact_selectors or options.remove_partial_selectors:
                remove_by_selector(
                    clone,
                    self.debug,
                    options.remove_exact_selectors,
                    options.remove_partial_selectors,
                    main_content,
                    debug_removals,
                    not options.remove_hidden_elements,
                )
            if do_profile:
                profile["removeBySelector"] = round((time.time() - t) * 1000)

            if do_profile:
                t = time.time()
            if options.remove_low_scoring:
                ContentScorer.score_and_remove(clone, self.debug, debug_removals, main_content)
            if do_profile:
                profile["removeLowScoring"] = round((time.time() - t) * 1000)

            if do_profile:
                t = time.time()
            if options.remove_content_patterns and main_content:
                pattern_url = self.options.url or self._get_doc_url() or ""
                remove_by_content_pattern(
                    main_content,
                    self.debug,
                    pattern_url,
                    metadata.title or "",
                    metadata.description or "",
                    debug_removals,
                )
            if do_profile:
                profile["removeByContentPattern"] = round((time.time() - t) * 1000)

            if do_profile:
                t = time.time()
            if options.standardize:
                standardize_content(
                    main_content,
                    metadata,
                    self.doc,
                    self.debug,
                    profile if do_profile else None,
                )
            if do_profile:
                profile["standardizeContent"] = round((time.time() - t) * 1000)

            if do_profile:
                t = time.time()
            self._resolve_relative_urls(main_content)
            if do_profile:
                profile["resolveRelativeUrls"] = round((time.time() - t) * 1000)

            self._deduplicate_images(main_content)

            best_cover_url = self._remove_cover_image(main_content, metadata.image or "")
            if best_cover_url:
                metadata.image = best_cover_url

            content = str(main_content)
            end_time = time.time()

            result = DomdownResponse(
                content=content,
                word_count=self._count_html_words(content),
                parse_time=end_time - start_time,
            )
            self._apply_metadata_to_response(result, metadata, page_meta_tags)

            if self.debug:
                result.debug = DebugInfo(
                    content_selector=self._get_element_selector(main_content),
                    removals=debug_removals,
                )

            if self.options.profile:
                result.profile = profile

            return result

        except Exception as error:
            print(f"Domdown: Error processing document: {error}")
            error_content = ""
            body = self._get_body()
            if body:
                error_content = self._resolve_content_urls(serialize_html(body))
            end_time = time.time()
            result = DomdownResponse(
                content=error_content,
                word_count=self._count_html_words(error_content),
                parse_time=end_time - start_time,
            )
            self._apply_metadata_to_response(result, metadata, page_meta_tags)
            return result

    def _merge_options(self, override: Optional[DomdownOptions] = None) -> DomdownOptions:
        base = DomdownOptions(
            remove_exact_selectors=True,
            remove_partial_selectors=True,
            remove_hidden_elements=True,
            remove_low_scoring=True,
            remove_small_images=True,
            remove_content_patterns=True,
            standardize=True,
            include_replies="extractors",
        )
        for key, value in vars(self.options).items():
            if value is not None and value is not False:
                if key in (
                    "remove_exact_selectors",
                    "remove_partial_selectors",
                    "remove_hidden_elements",
                    "remove_low_scoring",
                    "remove_small_images",
                    "remove_content_patterns",
                    "standardize",
                ):
                    continue
            setattr(base, key, value)

        for key in (
            "remove_exact_selectors",
            "remove_partial_selectors",
            "remove_hidden_elements",
            "remove_low_scoring",
            "remove_small_images",
            "remove_content_patterns",
            "standardize",
        ):
            val = getattr(self.options, key, None)
            if val is not None:
                setattr(base, key, val)

        if override:
            for key, value in vars(override).items():
                if value is not None:
                    setattr(base, key, value)

        return base

    def _apply_metadata_to_response(
        self,
        result: DomdownResponse,
        metadata: DomdownMetadata,
        meta_tags: List[MetaTagItem],
    ) -> None:
        result.title = metadata.title
        result.description = metadata.description
        result.domain = metadata.domain
        result.favicon = metadata.favicon
        result.image = metadata.image
        result.language = metadata.language
        result.published = metadata.published
        result.author = metadata.author
        result.site = metadata.site
        result.schema_org_data = metadata.schema_org_data
        result.meta_tags = meta_tags

    def _count_html_words(self, content: str) -> int:
        text = content.replace("<", " <").replace(">", "> ")
        text = re.sub(r"<[^>]*>", " ", text)
        text = (
            text.replace("&nbsp;", " ")
            .replace("&amp;", "&")
            .replace("&lt;", "<")
            .replace("&gt;", ">")
            .replace("&quot;", '"')
        )
        text = re.sub(r"&#\d+;", " ", text)
        text = re.sub(r"&\w+;", " ", text)
        return count_words(text)

    def _log(self, *args: Any) -> None:
        if self.debug:
            print("Domdown:", *args)

    def _evaluate_media_queries(self, doc: Tag) -> List[Dict[str, str]]:
        mobile_styles: List[Dict[str, str]] = []
        max_width_re = re.compile(r"max-width[^:]*:\s*(\d+)")

        try:
            style_tags = doc.find_all("style")
            if not style_tags:
                return mobile_styles

            style_rule_re = re.compile(r"([^{}]+)\{([^{}]+)\}")

            for style_tag in style_tags:
                css_text = style_tag.get_text() or ""
                if not css_text:
                    continue

                pos = 0
                css_len = len(css_text)
                while True:
                    media_index = css_text.find("@media", pos)
                    if media_index < 0:
                        break

                    brace_start = css_text.find("{", media_index)
                    if brace_start < 0:
                        break

                    depth = 1
                    i = brace_start + 1
                    while i < css_len and depth > 0:
                        ch = css_text[i]
                        if ch == "{":
                            depth += 1
                        elif ch == "}":
                            depth -= 1
                        i += 1

                    if depth != 0:
                        break

                    condition_text = css_text[media_index + len("@media") : brace_start].strip()
                    body_text = css_text[brace_start + 1 : i - 1]
                    pos = i

                    width_match = max_width_re.search(condition_text)
                    if not width_match:
                        continue

                    try:
                        max_width = int(width_match.group(1))
                    except ValueError:
                        continue

                    if MOBILE_WIDTH > max_width:
                        continue

                    for rule_match in style_rule_re.finditer(body_text):
                        selector = rule_match.group(1).strip()
                        styles = rule_match.group(2).strip()
                        if selector and styles:
                            mobile_styles.append({"selector": selector, "styles": styles})
        except Exception as error:
            print(f"Domdown: Error evaluating media queries: {error}")

        return mobile_styles

    def _apply_mobile_styles(self, doc: Tag, mobile_styles: List[Dict[str, str]]) -> None:
        if not mobile_styles:
            return

        for item in mobile_styles:
            selector = item.get("selector", "")
            styles = item.get("styles", "")
            if not selector or not styles:
                continue

            try:
                elements = doc.select(selector)
            except Exception as error:
                print("Domdown", "Error applying styles for selector:", selector, error)
                continue

            for element in elements:
                existing = element.get("style", "")
                element["style"] = f"{existing}{styles}"

    def _flatten_shadow_roots(self, original: Tag, clone: Tag) -> None:
        original_body = None
        if hasattr(original, "body") and getattr(original, "body") is not None:
            original_body = original.body
        elif isinstance(original, Tag) and original.name == "body":
            original_body = original
        elif isinstance(original, Tag):
            original_body = original.find("body")
        clone_body = clone.body if hasattr(clone, "body") else None
        if not original_body or not clone_body:
            return

        orig_elements = list(original_body.find_all(True))
        clone_elements = list(clone_body.find_all(True))
        if not orig_elements or not clone_elements:
            return

        shadow_data: List[Dict[str, Any]] = []
        for index, orig_el in enumerate(orig_elements):
            shadow_html = orig_el.get("data-domdown-shadow")
            if not shadow_html:
                continue

            if index >= len(clone_elements):
                continue

            clone_el = clone_elements[index]
            shadow_data.append({"clone_el": clone_el, "html": shadow_html})
            if orig_el.has_attr("data-domdown-shadow"):
                del orig_el["data-domdown-shadow"]
            if clone_el.has_attr("data-domdown-shadow"):
                del clone_el["data-domdown-shadow"]

        for item in shadow_data:
            self._replace_shadow_host(item["clone_el"], item["html"], clone)

    def _replace_shadow_host(self, el: Tag, shadow_html: str, doc: Tag) -> None:
        fragment = parse_html(shadow_html)
        fragment_children = list(fragment.children) if hasattr(fragment, "children") else []

        if "-" in (el.name or ""):
            div = BeautifulSoup("", "lxml").new_tag("div")
            for child in fragment_children:
                div.append(child.extract())
            el.replace_with(div)
            return

        el.clear()
        for child in fragment_children:
            el.append(child.extract())

    def _get_body(self) -> Optional[Tag]:
        if hasattr(self.doc, "body"):
            body = self.doc.body
            if body is not None:
                return body
        if isinstance(self.doc, Tag) and self.doc.name == "body":
            return self.doc
        if isinstance(self.doc, Tag):
            body = self.doc.find("body")
            return body
        return None

    def _get_document_element(self) -> Optional[Tag]:
        if isinstance(self.doc, BeautifulSoup):
            html_el = self.doc.find("html")
            if html_el:
                return html_el
            return self.doc
        if hasattr(self.doc, "document_element") and self.doc.document_element is not None:
            return self.doc.document_element
        if isinstance(self.doc, Tag):
            if self.doc.name in ("html", "[document]"):
                return self.doc
            if self.doc.name == "body" and self.doc.parent is not None:
                return self.doc
            html_el = self.doc.find_parent("html")
            if html_el:
                return html_el
            root = self.doc
            while root.parent is not None:
                root = root.parent
            if isinstance(root, Tag):
                return root
        return None

    def _get_doc_url(self) -> str:
        if hasattr(self.doc, "URL"):
            return self.doc.URL
        return ""

    def _normalize_attributes(self, body: Tag) -> None:
        renames = [("srcSet", "srcset")]
        for el in body.select("img, source"):
            for from_attr, to_attr in renames:
                value = el.get(from_attr)
                if value is not None:
                    del el[from_attr]
                    el[to_attr] = value

    def _resolve_noscript_images(self, body: Tag) -> None:
        for noscript in body.find_all("noscript"):
            noscript_img = noscript.find("img")
            if not noscript_img:
                html_content = ""
                if hasattr(noscript, "innerHTML"):
                    html_content = noscript.innerHTML
                else:
                    html_content = (
                        str(noscript.encode_contents(), "utf-8")
                        if hasattr(noscript, "encode_contents")
                        else noscript.decode_contents()
                    )

                if not html_content:
                    html_content = noscript.get_text()

                if "<img" not in html_content:
                    continue

                fragment = parse_html(html_content)
                if isinstance(fragment, Tag):
                    noscript_img = fragment.find("img")
                else:
                    noscript_img = None

            if not noscript_img or not isinstance(noscript_img, Tag):
                continue

            real_src = noscript_img.get("src", "")
            if not real_src or real_src.startswith("data:"):
                continue

            alt = noscript_img.get("alt")
            parent = noscript.parent
            if not parent:
                continue

            matched = False
            direct_children = [c for c in parent.children if isinstance(c, Tag) and c.name == "img"]
            for img in direct_children:
                src = img.get("src", "")
                if not src.startswith("data:"):
                    continue
                if not alt or img.get("alt") != alt:
                    continue
                img["src"] = real_src
                srcset = noscript_img.get("srcset", "")
                if srcset:
                    img["srcset"] = srcset
                matched = True
                break

            if not matched and self._is_lazy_image_context(noscript):
                container = closest(noscript, "figure") or parent
                existing_imgs = container.find_all("img") if isinstance(container, Tag) else []
                has_real_image = False
                for img in existing_imgs:
                    if closest(img, "noscript"):
                        continue
                    src = img.get("src", "")
                    if src and not src.startswith("data:"):
                        has_real_image = True
                        break

                if not has_real_image:
                    promoted_img = copy.copy(noscript_img)
                    noscript.insert_before(promoted_img)

    def _is_lazy_image_context(self, noscript: Tag) -> bool:
        if closest(noscript, "figure"):
            return True

        parent = noscript.parent
        if parent:
            for sibling in parent.children:
                if sibling is noscript:
                    continue
                if not isinstance(sibling, Tag):
                    continue
                cls = get_class_name(sibling).lower()
                if "lazy" in cls:
                    return True

            parent_cls = get_class_name(parent).lower()
            for keyword in ("image", "img", "picture", "photo", "media"):
                if keyword in parent_cls:
                    return True

        return False

    def _strip_unsafe_elements(self) -> None:
        body = self._get_body()
        if not body:
            return

        dangerous_selectors = [
            "script:not([type^='math/'])",
            "style",
            "noscript",
            "frame",
            "frameset",
            "object",
            "embed",
            "applet",
            "base",
        ]
        for selector in dangerous_selectors:
            for el in body.select(selector):
                el.decompose()

        for el in body.find_all(True):
            attrs_to_remove = []
            for attr_name, attr_value in list(el.attrs.items()):
                name_lower = attr_name.lower()
                if name_lower.startswith("on"):
                    attrs_to_remove.append(attr_name)
                elif name_lower == "srcdoc":
                    attrs_to_remove.append(attr_name)
                elif name_lower in ("href", "src", "action", "formaction", "xlink:href"):
                    if isinstance(attr_value, str) and is_dangerous_url(attr_value):
                        attrs_to_remove.append(attr_name)
            for attr_name in attrs_to_remove:
                del el[attr_name]

    def _sanitize_schema_text_content(self, schema_text: str) -> str:
        fragment = BeautifulSoup(schema_text, "lxml")
        root = fragment.body if fragment.body is not None else fragment

        dangerous_selectors = [
            "script:not([type^='math/'])",
            "style",
            "noscript",
            "frame",
            "frameset",
            "object",
            "embed",
            "applet",
            "base",
        ]
        for selector in dangerous_selectors:
            for el in root.select(selector):
                el.decompose()

        for el in root.find_all(True):
            attrs_to_remove = []
            for attr_name, attr_value in list(el.attrs.items()):
                name_lower = attr_name.lower()
                if name_lower.startswith("on"):
                    attrs_to_remove.append(attr_name)
                elif name_lower == "srcdoc":
                    attrs_to_remove.append(attr_name)
                elif name_lower in ("href", "src", "action", "formaction", "xlink:href"):
                    if isinstance(attr_value, str) and is_dangerous_url(attr_value):
                        attrs_to_remove.append(attr_name)
            for attr_name in attrs_to_remove:
                del el[attr_name]

        if hasattr(root, "body") and root.body is not None:
            return root.body.decode_contents()
        return root.decode_contents() if hasattr(root, "decode_contents") else schema_text

    def _deduplicate_images(self, body: Tag) -> None:
        for figure in body.find_all("figure"):
            fig_imgs = [
                img for img in figure.find_all("img") if not closest(img, "noscript") and img.parent is not None
            ]
            if len(fig_imgs) < 2:
                continue

            groups: Dict[Optional[str], List[Tag]] = {}
            for img in fig_imgs:
                src = img.get("src", "")
                if not src or src.startswith("data:"):
                    continue
                alt_val = (img.get("alt") or "").strip() or None
                group = groups.get(alt_val, [])
                group.append(img)
                groups[alt_val] = group

            for key, group in groups.items():
                if len(group) < 2:
                    continue
                if key is not None and all(img.get("src") == group[0].get("src") for img in group):
                    continue
                self._keep_best_image(group)

        imgs = list(body.find_all("img"))
        for i, img in enumerate(imgs):
            if closest(img, "noscript") or closest(img, "figure"):
                continue
            if img.parent is None:
                continue

            alt = (img.get("alt") or "").strip()
            if not alt:
                continue
            src = img.get("src", "")
            if not src or src.startswith("data:"):
                continue

            for j in range(i + 1, len(imgs)):
                other = imgs[j]
                if closest(other, "noscript") or closest(other, "figure"):
                    continue
                if other.parent is None:
                    continue

                other_alt = (other.get("alt") or "").strip()
                if other_alt != alt:
                    break
                other_src = other.get("src", "")
                if not other_src or other_src.startswith("data:"):
                    continue
                if other_src == src:
                    break

                self._keep_best_image([img, other])
                if img.parent is None:
                    break

        for img in list(body.find_all("img")):
            if img.parent is None:
                continue
            if closest(img, "a") or closest(img, "figure") or closest(img, "noscript"):
                continue

            src = img.get("src", "")
            if not src or src.startswith("data:"):
                continue

            parent = img.parent
            if not isinstance(parent, Tag):
                continue

            normalized_src = self._normalize_src(src)
            for link in parent.find_all("a", href=True, recursive=False):
                if not link.find("img"):
                    continue
                href = link.get("href", "")
                if normalized_src == self._normalize_src(href):
                    img.decompose()
                    break

    def _keep_best_image(self, group: List[Tag]) -> None:
        best = group[0]
        for i in range(1, len(group)):
            winner = self._pick_best_image(best, group[i])
            loser = group[i] if winner is best else best
            if loser.parent:
                loser.decompose()
            best = winner

    @staticmethod
    def _normalize_src(url: str) -> str:
        return re.sub(r"^https?://", "", url).split("?")[0]

    def _pick_best_image(self, a: Tag, b: Tag) -> Tag:
        tier_a = 2 if a.get("srcset") else (1 if closest(a, "picture") else 0)
        tier_b = 2 if b.get("srcset") else (1 if closest(b, "picture") else 0)
        if tier_a != tier_b:
            return a if tier_a > tier_b else b

        width_a = self._url_width(a)
        width_b = self._url_width(b)
        if width_a != width_b:
            return a if width_a > width_b else b

        return a

    @staticmethod
    def _url_width(img: Tag) -> int:
        src = img.get("src", "")
        if not src:
            return 0
        m = _URL_WIDTH_PATTERN.search(src)
        return int(m.group(1)) if m else 0

    def _remove_cover_image(self, body: Tag, metadata_image: str) -> Optional[str]:
        if not metadata_image:
            return None

        meta_norm = self._normalize_src(metadata_image)

        for img in body.find_all("img"):
            src = img.get("src", "")
            if not src or src.startswith("data:"):
                continue
            if self._normalize_src(src) != meta_norm:
                continue

            best_url = self._get_largest_image_src(img)

            figure = closest(img, "figure")
            if figure and figure.find("figcaption"):
                return best_url

            img.decompose()
            return best_url

        return None

    def _get_largest_image_src(self, img: Tag) -> str:
        srcset = img.get("srcset", "")
        if not srcset:
            return img.get("src", "")

        entry_pattern = re.compile(r"(.+?)\s+(\d+(?:\.\d+)?)w")
        best_url = ""
        best_width = 0.0
        last_index = 0

        for match in entry_pattern.finditer(srcset):
            url = match.group(1).strip()
            if last_index > 0:
                url = re.sub(r"^,\s*", "", url)
            last_index = match.end()

            width = float(match.group(2))
            if url and width > best_width:
                best_width = width
                best_url = url

        url = best_url or img.get("src", "")
        url = re.sub(r",w_\d+", "", url)
        url = re.sub(r",c_\w+", "", url)
        return url

    def _find_main_content(
        self,
        doc: Tag,
        content_selector: Optional[str],
        schema_org_data: Any,
    ) -> Optional[Tag]:
        found: Optional[Tag] = None

        if content_selector:
            found = doc.select_one(content_selector)
            self._log("Using contentSelector:", content_selector, "found" if found else "not found")

        if not found:
            found = self._find_main_content_by_scoring(doc)

        if found:
            domdown_ancestor = closest(found, "[data-domdown]")
            if domdown_ancestor:
                found = domdown_ancestor

        if found and found.name == "body":
            schema_text = self._get_schema_text(schema_org_data)
            if schema_text:
                body = found
                schema_content = self._find_element_by_schema_text(body, schema_text)
                if schema_content:
                    self._log("Found content element via schema.org text")
                    found = schema_content

        return found

    def _find_main_content_by_scoring(self, doc: Tag) -> Optional[Tag]:
        candidates: List[Dict[str, Any]] = []

        for index, selector in enumerate(ENTRY_POINT_ELEMENTS):
            try:
                elements = doc.select(selector)
            except Exception:
                continue
            for element in elements:
                if not isinstance(element, Tag):
                    continue
                score = (len(ENTRY_POINT_ELEMENTS) - index) * 40
                score += ContentScorer.score_element(element)
                candidates.append({"element": element, "score": score, "selector_index": index})

        if not candidates:
            return self._find_content_by_scoring(doc)

        candidates.sort(key=lambda c: c["score"], reverse=True)

        if self.debug:
            self._log(
                "Content candidates:",
                [
                    {
                        "element": c["element"].name,
                        "selector": self._get_element_selector(c["element"]),
                        "score": c["score"],
                    }
                    for c in candidates
                ],
            )

        if len(candidates) == 1 and candidates[0]["element"].name == "body":
            table_content = self._find_table_based_content(doc)
            if table_content:
                return table_content

        top = candidates[0]
        best = top
        for i in range(1, len(candidates)):
            child = candidates[i]
            child_words = count_words(child["element"].get_text() or "")
            if (
                child["selector_index"] < best["selector_index"]
                and contains(best["element"], child["element"])
                and child_words > 50
            ):
                siblings_at_index = 0
                for c in candidates:
                    if c["selector_index"] == child["selector_index"] and contains(top["element"], c["element"]):
                        siblings_at_index += 1
                        if siblings_at_index > 1:
                            break
                if siblings_at_index > 1:
                    continue
                best = child

        if best is not top:
            return best["element"]

        return top["element"]

    def _find_table_based_content(self, doc: Tag) -> Optional[Tag]:
        tables = doc.find_all("table")
        has_table_layout = False
        for table in tables:
            width = int(table.get("width", "0") or "0")
            style = get_computed_style(table)
            table_class = get_class_name(table).lower()

            if width > 400:
                has_table_layout = True
                break
            style_width = style.get("width", "")
            if "px" in style_width:
                try:
                    if int(style_width.replace("px", "").strip()) > 400:
                        has_table_layout = True
                        break
                except (ValueError, TypeError):
                    pass
            if table.get("align") == "center":
                has_table_layout = True
                break
            if "content" in table_class or "article" in table_class:
                has_table_layout = True
                break

            for row in table.find_all("tr"):
                cells = [c for c in row.children if isinstance(c, Tag) and c.name == "td"]
                if len(cells) >= 2 and any(c.get("width") for c in cells):
                    has_table_layout = True
                    break
            if has_table_layout:
                break

        if not has_table_layout:
            return None

        cells = doc.find_all("td")
        best_cell = ContentScorer.find_best_element(cells)
        if not best_cell:
            return None

        best_cell_words = count_words(best_cell.get_text() or "")
        body_el = self._get_body()
        body_words = count_words((body_el or doc).get_text() or "")
        if best_cell_words * 2 < body_words:
            return None

        return best_cell

    def _find_content_by_scoring(self, doc: Tag) -> Optional[Tag]:
        candidates: List[Dict[str, Any]] = []

        for element in doc.select(BLOCK_ELEMENTS_SELECTOR):
            if not isinstance(element, Tag):
                continue
            score = ContentScorer.score_element(element)
            if score > 0:
                candidates.append({"score": score, "element": element})

        if not candidates:
            return None

        candidates.sort(key=lambda c: c["score"], reverse=True)
        return candidates[0]["element"]

    def _find_largest_hidden_content_selector(self) -> Optional[str]:
        body = self._get_body()
        if not body:
            return None

        candidates = []
        try:
            for el in body.select(HIDDEN_EXACT_SKIP_SELECTOR):
                if not isinstance(el, Tag):
                    continue
                class_name = el.get("class", "")
                if isinstance(class_name, list):
                    class_name = " ".join(class_name)
                if "math" in class_name:
                    continue
                candidates.append(el)
        except Exception:
            return None

        best: Optional[Tag] = None
        best_words = 0
        for el in candidates:
            words = count_words(el.get_text() or "")
            if words > best_words:
                best = el
                best_words = words

        if not best or best_words < 30:
            return None

        return self._get_element_selector(best)

    def _find_element_by_schema_text(self, root: Optional[Tag], schema_text: str) -> Optional[Tag]:
        if not root or not schema_text:
            return None

        paragraphs = schema_text.split("\n")
        first_para = ""
        for p in paragraphs:
            stripped = p.strip()
            if stripped:
                first_para = stripped
                break

        search_phrase = first_para[:100].strip()
        if not search_phrase:
            return None

        schema_word_count = count_words(schema_text)
        best_match: Optional[Tag] = None
        best_size = float("inf")

        for el in root.find_all(True):
            if el is root:
                continue
            el_text = el.get_text() or ""
            if search_phrase not in el_text:
                continue

            el_words = count_words(el_text)
            if el_words >= schema_word_count * 0.8 and el_words < best_size:
                best_size = el_words
                best_match = el

        return best_match

    def _get_schema_text(self, schema_org_data: Any, depth: int = 0) -> str:
        if not schema_org_data or depth > 10:
            return ""

        items = schema_org_data if isinstance(schema_org_data, list) else [schema_org_data]
        for item in items:
            if isinstance(item, list):
                found = self._get_schema_text(item, depth + 1)
                if found:
                    return found
                continue

            if isinstance(item, dict):
                if "text" in item and isinstance(item["text"], str):
                    return item["text"]
                if "articleBody" in item and isinstance(item["articleBody"], str):
                    return item["articleBody"]
                if "@graph" in item and isinstance(item["@graph"], list):
                    found = self._get_schema_text(item["@graph"], depth + 1)
                    if found:
                        return found

        return ""

    def _get_element_selector(self, element: Tag) -> str:
        parts: List[str] = []
        current: Optional[Tag] = element
        doc_el = self._get_document_element()

        while current is not None and current is not doc_el:
            selector = current.name
            el_id = current.get("id")
            if el_id and isinstance(el_id, str):
                selector += "#" + el_id
            else:
                cls = get_class_name(current)
                if cls:
                    safe = [c for c in cls.strip().split() if not UNSAFE_CSS_CLASS_RE.search(c)]
                    if safe:
                        selector += "." + ".".join(safe)
            parts.insert(0, selector)

            parent = current.parent
            if parent is None or not isinstance(parent, Tag):
                break
            current = parent

        return " > ".join(parts)

    def _adopt_external_footnotes(self, main_content: Tag, root: Tag) -> None:
        root_body = root.body if hasattr(root, "body") else root
        if root_body is None or main_content is root_body:
            return

        for el in root_body.find_all(["div", "section", "aside"]):
            class_name = get_class_name(el)
            el_id = el.get("id", "") or ""
            if not re.search(r"footnote", class_name, re.IGNORECASE) and not re.search(
                r"footnote", el_id, re.IGNORECASE
            ):
                continue

            if contains(main_content, el) or contains(el, main_content):
                continue

            heading = el.find(["h1", "h2", "h3", "h4", "h5", "h6"])
            if not heading:
                continue
            heading_text = heading.get_text().strip() if heading else ""
            if not FOOTNOTE_SECTION_RE.search(heading_text):
                continue

            main_content.append(el.extract())

    def _resolve_relative_urls(self, element: Tag) -> None:
        doc_url = self.options.url or self._get_doc_url()
        if not doc_url:
            return

        base_url = doc_url
        base_el = self.doc.select_one("base[href]")
        if base_el:
            base_href = base_el.get("href")
            if base_href:
                try:
                    base_url = urljoin(doc_url, base_href)
                except Exception:
                    pass

        def resolve(url: str) -> str:
            normalized = url.strip()
            normalized = re.sub(r'^\\?["\']+', "", normalized)
            normalized = re.sub(r'\\?["\']+$', "", normalized)
            if normalized.startswith("#"):
                return normalized
            try:
                return urljoin(base_url, normalized)
            except Exception:
                return normalized or url

        for el in element.select("[href]"):
            href = el.get("href")
            if href and isinstance(href, str):
                el["href"] = resolve(href)

        for el in element.select("[src]"):
            src = el.get("src")
            if src and isinstance(src, str):
                el["src"] = resolve(src)

        for el in element.select("[srcset]"):
            srcset = el.get("srcset", "")
            if not srcset or not isinstance(srcset, str):
                continue

            entry_pattern = re.compile(r"(.+?)\s+(\d+(?:\.\d+)?[wx])")
            entries: List[str] = []
            last_idx = 0

            for match in entry_pattern.finditer(srcset):
                url = match.group(1).strip()
                if last_idx > 0:
                    url = re.sub(r"^,\s*", "", url)
                last_idx = match.end()
                entries.append(f"{resolve(url)} {match.group(2)}")

            if entries:
                el["srcset"] = ", ".join(entries)
            else:
                resolved_parts = []
                for entry in srcset.split(","):
                    parts = entry.strip().split()
                    if parts:
                        parts[0] = resolve(parts[0])
                    resolved_parts.append(" ".join(parts))
                el["srcset"] = ", ".join(resolved_parts)

        for el in element.select("[poster]"):
            poster = el.get("poster")
            if poster and isinstance(poster, str):
                el["poster"] = resolve(poster)

    def _resolve_streamed_content(self, doc: Tag) -> None:
        scripts = doc.find_all("script")
        swaps: List[Dict[str, str]] = []
        rc_pattern = re.compile(r'\$RC\("(B:\d+)","(S:\d+)"\)')

        for script in scripts:
            text = script.string or ""
            if not text or "$RC(" not in text:
                continue
            for match in rc_pattern.finditer(text):
                swaps.append({"template_id": match.group(1), "content_id": match.group(2)})

        if not swaps:
            return

        swap_count = 0
        for swap in swaps:
            template_id = swap["template_id"]
            content_id = swap["content_id"]

            template = doc.find(id=template_id)
            content = doc.find(id=content_id)
            if not template or not content:
                continue

            parent = template.parent
            if not parent:
                continue

            next_sib = template.next_sibling
            found_marker = False
            while next_sib:
                following = next_sib.next_sibling
                if isinstance(next_sib, Comment) and next_sib == "/$":
                    next_sib.extract()
                    found_marker = True
                    break
                next_sib.extract()
                next_sib = following

            if not found_marker:
                continue

            children = list(content.children)
            for child in children:
                template.insert_before(child.extract())

            template.extract()
            content.extract()
            swap_count += 1

        if swap_count > 0:
            self._log("Resolved streamed content:", swap_count, "suspense boundaries")

    def _extract_schema_org_data(self, doc: Tag) -> List[Any]:
        schema_scripts = doc.select('script[type="application/ld+json"]')
        raw_schema_items: List[Any] = []

        for script in schema_scripts:
            json_content = script.string or ""
            if not json_content:
                continue

            try:
                json_content = re.sub(r"/\*[\s\S]*?\*/", "", json_content)
                json_content = re.sub(r"^\s*//.*$", "", json_content, flags=re.MULTILINE)
                json_content = re.sub(r"^\s*<!\[CDATA\[([\s\S]*?)\]\]>\s*$", r"\1", json_content)
                json_content = re.sub(r"^\s*(\*\/|\/\*)\s*|\s*(\*\/|\/\*)\s*$", "", json_content)
                json_content = json_content.strip()

                json_data = json.loads(json_content)

                if isinstance(json_data, dict) and "@graph" in json_data and isinstance(json_data["@graph"], list):
                    raw_schema_items.extend(json_data["@graph"])
                else:
                    raw_schema_items.append(json_data)
            except Exception as error:
                print(f"Domdown: Error parsing schema.org data: {error}")
                if self.debug:
                    print(f"Domdown: Problematic JSON content: {json_content[:200]}")

        def decode_strings_in_obj(item: Any) -> Any:
            if isinstance(item, str):
                return decode_html_entities(item)
            elif isinstance(item, list):
                return [decode_strings_in_obj(i) for i in item]
            elif isinstance(item, dict) and item is not None:
                return {k: decode_strings_in_obj(v) for k, v in item.items()}
            return item

        return [decode_strings_in_obj(item) for item in raw_schema_items]

    def _collect_meta_tags(self) -> List[MetaTagItem]:
        page_meta_tags: List[MetaTagItem] = []
        for meta in self.doc.select("meta"):
            name = meta.get("name")
            property_val = meta.get("property")
            content = meta.get("content")
            if content:
                page_meta_tags.append(
                    MetaTagItem(
                        name=name,
                        property=property_val,
                        content=decode_html_entities(content) if isinstance(content, str) else content,
                    )
                )
        return page_meta_tags

    def _resolve_content_urls(self, html_str: str) -> str:
        base_url = self.options.url or self._get_doc_url()
        if not base_url:
            return html_str

        soup = BeautifulSoup(html_str, "lxml")
        body = soup.body
        if body is None:
            container = soup
        else:
            container = body

        self._resolve_relative_urls_on_container(container, base_url)

        if body is not None:
            return body.decode_contents()
        return str(soup)

    def _resolve_relative_urls_on_container(self, container: Tag, base_url: str) -> None:
        def resolve(url: str) -> str:
            normalized = url.strip()
            if normalized.startswith("#"):
                return normalized
            try:
                return urljoin(base_url, normalized)
            except Exception:
                return url

        for el in container.find_all(True):
            href = el.get("href")
            if href and isinstance(href, str):
                el["href"] = resolve(href)
            src = el.get("src")
            if src and isinstance(src, str):
                el["src"] = resolve(src)

    def _remove_images(self, doc: Tag) -> None:
        for img in doc.find_all("img"):
            img.decompose()

    def _build_extractor_response(
        self,
        extracted: Dict[str, Any],
        metadata: DomdownMetadata,
        start_time: float,
        extractor: BaseExtractor,
        page_meta_tags: List[MetaTagItem],
    ) -> DomdownResponse:
        content_html = extracted.get("content_html", "")
        content_html = self._resolve_content_urls(content_html)
        variables = self._get_extractor_variables(extracted.get("variables"))
        ext_vars = extracted.get("variables") or {}

        extractor_type = type(extractor).__name__.replace("Extractor", "").lower()

        result = DomdownResponse(
            content=content_html,
            title=ext_vars.get("title") or metadata.title,
            description=ext_vars.get("description") or metadata.description,
            domain=metadata.domain,
            favicon=metadata.favicon,
            image=metadata.image,
            language=ext_vars.get("language") or metadata.language,
            published=ext_vars.get("published") or metadata.published,
            author=ext_vars.get("author") or metadata.author,
            site=ext_vars.get("site") or metadata.site,
            schema_org_data=metadata.schema_org_data,
            word_count=self._count_html_words(content_html),
            parse_time=time.time() - start_time,
            extractor_type=extractor_type,
            meta_tags=page_meta_tags,
        )
        if variables:
            result.variables = variables

        return result

    def _get_extractor_variables(self, variables: Optional[Dict[str, str]]) -> Optional[Dict[str, str]]:
        if not variables:
            return None
        custom: Dict[str, str] = {}
        has_custom = False
        for key, value in variables.items():
            if key not in STANDARD_VARIABLE_KEYS:
                custom[key] = value
                has_custom = True
        return custom if has_custom else None
