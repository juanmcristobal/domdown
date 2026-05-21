from __future__ import annotations

import re
from typing import Any, Optional

from bs4 import NavigableString, Tag

from domdown.extractors._base import BaseExtractor, ExtractorOptions
from domdown.types import ExtractorResult
from domdown.utils.dom import escape_html, serialize_html

SELECTORS = {
    "article_container": '[data-testid="twitterArticleRichTextView"]',
    "title": '[data-testid="twitter-article-title"]',
    "author": '[itemprop="author"]',
    "author_name": 'meta[itemprop="name"]',
    "author_handle": 'meta[itemprop="additionalName"]',
    "images": '[data-testid="tweetPhoto"] img',
    "draft_paragraphs": ".longform-unstyled, .public-DraftStyleDefault-block",
    "bold_spans": 'span[style*="font-weight: bold"]',
    "draft_attributes": "[data-offset-key]",
    "embedded_tweet": '[data-testid="simpleTweet"]',
    "tweet_text": '[data-testid="tweetText"]',
    "user_name": "[data-testid=User-Name]",
    "code_block": '[data-testid="markdown-code-block"]',
    "article_read_view": '[data-testid="twitterArticleReadView"]',
}


class XArticleExtractor(BaseExtractor):
    def __init__(
        self,
        document: Tag,
        url: str,
        schema_org_data: Any = None,
        options: Optional[ExtractorOptions] = None,
    ):
        super().__init__(document, url, schema_org_data, options)
        self.article_container = self.document.select_one(SELECTORS["article_container"])

    def can_extract(self) -> bool:
        return self.article_container is not None

    def extract(self) -> ExtractorResult:
        title = self._extract_title()
        author = self._extract_author()
        content_html = self._extract_content()
        description = self._create_description()

        return ExtractorResult(
            content=content_html,
            content_html=content_html,
            extracted_content={"article_id": self._get_article_id()},
            variables={
                "title": title,
                "author": author,
                "site": "X (Twitter)",
                "description": description,
            },
        )

    def _extract_title(self) -> str:
        title_el = self.document.select_one(SELECTORS["title"])
        if title_el:
            text = title_el.get_text().strip()
            if text:
                return text
        return "Untitled X Article"

    def _extract_author(self) -> str:
        author_container = self.document.select_one(SELECTORS["author"])
        if not author_container:
            return self._get_author_from_url()

        name_el = author_container.select_one(SELECTORS["author_name"])
        handle_el = author_container.select_one(SELECTORS["author_handle"])

        name = name_el.get("content", "") if name_el else ""
        handle = handle_el.get("content", "") if handle_el else ""

        if name and handle:
            return f"{name} (@{handle})"
        return name or handle or self._get_author_from_url()

    def _get_author_from_url(self) -> str:
        match = re.search(r"/([a-zA-Z0-9_][a-zA-Z0-9_]{0,14})/(article|status)/\d+", self.url)
        if match:
            return f"@{match.group(1)}"
        return self._get_author_from_og_title()

    def _get_author_from_og_title(self) -> str:
        og_title_el = self.document.select_one('meta[property="og:title"]')
        og_title = og_title_el.get("content", "") if og_title_el else ""
        match = re.search(r"^(?:\(\d+\)\s+)?(.+?)\s+on\s+X\s*:", og_title)
        return match.group(1).strip() if match else "Unknown"

    def _get_article_id(self) -> str:
        match = re.search(r"article/(\d+)", self.url)
        return match.group(1) if match else ""

    def _extract_content(self) -> str:
        if not self.article_container:
            return ""

        import copy

        clone = copy.copy(self.article_container)

        self._clean_content(clone)

        header_image = self._extract_header_image()
        content = serialize_html(clone)
        return f'<article class="x-article">{header_image}{content}</article>'

    def _extract_header_image(self) -> str:
        read_view = self.document.select_one(SELECTORS["article_read_view"])
        if not read_view:
            return ""

        header_photo = read_view.select_one(SELECTORS["images"])
        if not header_photo:
            return ""

        if self.article_container and header_photo:
            if self.article_container.find_parent(header_photo):
                return ""

        src = header_photo.get("src", "")
        if not src:
            return ""

        alt = re.sub(r"\s+", " ", header_photo.get("alt", "Image")).strip()

        return f'<img src="{self._upgrade_image_src(src)}" alt="{escape_html(alt)}">'

    def _clean_content(self, container: Tag) -> None:
        self._convert_embedded_tweets(container)
        self._convert_code_blocks(container)
        self._convert_headers(container)
        self._unwrap_linked_images(container)
        self._upgrade_image_quality(container)
        self._convert_bold_spans(container)
        self._convert_draft_paragraphs(container)
        self._remove_draft_attributes(container)

    def _convert_embedded_tweets(self, container: Tag) -> None:
        for tweet in container.select(SELECTORS["embedded_tweet"]):
            blockquote = Tag(name="blockquote")
            blockquote["class"] = "embedded-tweet"

            user_name_el = tweet.select_one(SELECTORS["user_name"])
            if user_name_el:
                author_links = user_name_el.select("a")
                full_name = author_links[0].get_text().strip() if len(author_links) > 0 else ""
                handle = author_links[1].get_text().strip() if len(author_links) > 1 else ""

                if full_name or handle:
                    cite = Tag(name="cite")
                    cite.string = f"{full_name} {handle}" if handle else full_name
                    blockquote.append(cite)

            tweet_text_el = tweet.select_one(SELECTORS["tweet_text"])
            if tweet_text_el:
                tweet_text = tweet_text_el.get_text().strip()
                if tweet_text:
                    p = Tag(name="p")
                    p.string = tweet_text
                    blockquote.append(p)

            tweet.replace_with(blockquote)

    def _convert_code_blocks(self, container: Tag) -> None:
        for block in container.select(SELECTORS["code_block"]):
            pre = block.select_one("pre")
            code = block.select_one("code")
            if not pre or not code:
                continue

            language = ""
            lang_match = re.search(r"language-(\w+)", code.get("class", ""))
            if lang_match:
                language = lang_match.group(1)
            else:
                lang_span = block.select_one("span")
                if lang_span:
                    language = lang_span.get_text().strip()

            new_pre = Tag(name="pre")
            new_code = Tag(name="code")
            if language:
                new_code["data-lang"] = language
                new_code["class"] = f"language-{language}"
            new_code.string = code.get_text() or ""
            new_pre.append(new_code)

            block.replace_with(new_pre)

    def _convert_headers(self, container: Tag) -> None:
        for header in container.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
            level = header.name
            text = header.get_text().strip()
            if not text:
                continue

            new_header = Tag(name=level)
            new_header.string = text
            header.replace_with(new_header)

    def _unwrap_linked_images(self, container: Tag) -> None:
        from ..utils.dom import closest

        for img in container.select(SELECTORS["images"]):
            anchor = closest(img, "a")
            if not anchor or not container.find_parent(anchor):
                continue

            src = img.get("src", "")
            alt = re.sub(r"\s+", " ", img.get("alt", "Image")).strip()

            clean_img = Tag(name="img")
            clean_img["src"] = self._upgrade_image_src(src)
            clean_img["alt"] = alt

            anchor.replace_with(clean_img)

    def _upgrade_image_quality(self, container: Tag) -> None:
        for img in container.select(SELECTORS["images"]):
            src = img.get("src")
            if src:
                img["src"] = self._upgrade_image_src(src)

    def _upgrade_image_src(self, src: str) -> str:
        if "&name=" in src:
            return re.sub(r"&name=\w+", "&name=large", src)
        elif "?" in src:
            return f"{src}&name=large"
        return f"{src}?name=large"

    def _convert_draft_paragraphs(self, container: Tag) -> None:
        for div in container.select(SELECTORS["draft_paragraphs"]):
            p = Tag(name="p")

            for child in div.children:
                if isinstance(child, NavigableString):
                    p.append(NavigableString(child.string or ""))
                elif isinstance(child, Tag):
                    tag = child.name.lower()

                    if tag == "strong":
                        strong = Tag(name="strong")
                        strong.string = child.get_text() or ""
                        p.append(strong)
                    elif tag == "a":
                        link = Tag(name="a")
                        link["href"] = child.get("href", "")
                        link.string = child.get_text() or ""
                        p.append(link)
                    elif tag == "code":
                        code = Tag(name="code")
                        code.string = child.get_text() or ""
                        p.append(code)
                    else:
                        for subchild in child.children:
                            if isinstance(subchild, NavigableString):
                                p.append(NavigableString(subchild.string or ""))
                            elif isinstance(subchild, Tag):
                                sub_tag = subchild.name.lower()
                                if sub_tag == "strong":
                                    strong = Tag(name="strong")
                                    strong.string = subchild.get_text() or ""
                                    p.append(strong)
                                elif sub_tag == "a":
                                    link = Tag(name="a")
                                    link["href"] = subchild.get("href", "")
                                    link.string = subchild.get_text() or ""
                                    p.append(link)
                                elif sub_tag == "code":
                                    code = Tag(name="code")
                                    code.string = subchild.get_text() or ""
                                    p.append(code)

            div.replace_with(p)

    def _convert_bold_spans(self, container: Tag) -> None:
        for span in container.select(SELECTORS["bold_spans"]):
            strong = Tag(name="strong")
            strong.string = span.get_text() or ""
            span.replace_with(strong)

    def _remove_draft_attributes(self, container: Tag) -> None:
        for el in container.select(SELECTORS["draft_attributes"]):
            if "data-offset-key" in el.attrs:
                del el["data-offset-key"]

    def _create_description(self) -> str:
        if self.article_container:
            text = self.article_container.get_text().strip()
            if len(text) > 140:
                return text[:140] + "..."
            return text
        return ""
