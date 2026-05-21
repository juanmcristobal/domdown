from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, List, Optional

from bs4 import Tag

from domdown.extractors._base import BaseExtractor, ExtractorOptions
from domdown.types import ExtractorResult
from domdown.utils.comments import build_content_html
from domdown.utils.dom import escape_html, parse_html, serialize_html


@dataclass
class OembedResponse:
    html: str
    author_name: str
    author_url: str
    provider_name: str


@dataclass
class FxTwitterMediaItem:
    type: str
    id: str
    url: str
    width: int
    height: int


@dataclass
class FxTwitterFacet:
    type: str
    indices: List[int]
    id: Optional[str] = None
    display: Optional[str] = None
    original: Optional[str] = None
    replacement: Optional[str] = None
    text: Optional[str] = None


@dataclass
class FxTwitterResponse:
    code: int
    tweet: "FxTwitterTweet"


@dataclass
class FxTwitterTweet:
    text: str
    raw_text: Optional[Any] = None
    author: Optional[Any] = None
    created_at: Optional[str] = None
    media: Optional[Any] = None
    article: Optional[Any] = None


@dataclass
class DraftBlock:
    key: str
    text: str
    type: str
    inline_style_ranges: List[Any] = None
    entity_ranges: List[Any] = None
    data: Optional[Any] = None


@dataclass
class DraftEntityMapEntry:
    key: str
    value: Any


@dataclass
class Marker:
    offset: int
    type: str
    tag: str


class XOembedExtractor(BaseExtractor):
    def __init__(
        self,
        document: Tag,
        url: str,
        schema_org_data: Any = None,
        options: Optional[ExtractorOptions] = None,
    ):
        super().__init__(document, url, schema_org_data, options)

    def can_extract(self) -> bool:
        return False

    def extract(self) -> ExtractorResult:
        return ExtractorResult(content="", content_html="")

    def can_extract_async(self) -> bool:
        return bool(re.search(r"/(status|article)/\d+", self.url))

    async def extract_async(self) -> ExtractorResult:
        fetch = self.options.fetch
        if not fetch:
            return ExtractorResult(content="", content_html="")

        fx_result = await self._try_extract_fx_twitter(fetch)
        if fx_result:
            return fx_result

        return await self._extract_oembed(fetch)

    async def _extract_oembed(self, fetch) -> ExtractorResult:
        oembed_url = f"https://publish.twitter.com/oembed?url={self.url}&omit_script=true"
        response = await fetch(oembed_url)

        if not response.ok:
            raise Exception(f"oEmbed request failed: {response.status}")

        data = await response.json()

        div = parse_html(data.get("html", ""))
        blockquote = div.select_one("blockquote")
        paragraphs = blockquote.select("p") if blockquote else []
        tweet_text = "".join(f"<p>{serialize_html(p)}</p>" for p in paragraphs)

        handle = ""
        if data.get("author_url"):
            handle = f"@{data['author_url'].split('/')[-1]}"

        content_html = build_content_html("twitter", tweet_text, "")

        author = handle or data.get("author_name", "")
        description = re.sub(r"<[^>]*>", "", tweet_text).strip()[:140].replace(r"\s+", " ")

        return ExtractorResult(
            content=content_html,
            content_html=content_html,
            variables={
                "title": self.post_title(author, "X"),
                "author": author,
                "site": "X (Twitter)",
                "description": description,
            },
        )

    async def _try_extract_fx_twitter(self, fetch) -> Optional[ExtractorResult]:
        match = re.search(r"/([a-zA-Z0-9_][a-zA-Z0-9_]{0,14})/(status|article)/(\d+)", self.url)
        if not match:
            return None

        try:
            data = await self._fetch_fx_twitter(match.group(1), match.group(3), fetch)
            if data.get("tweet", {}).get("article"):
                return self._build_article_result(data)
            if data.get("tweet", {}).get("text"):
                return self._build_tweet_result(data)
            return None
        except Exception:
            return None

    async def _fetch_fx_twitter(self, username: str, id: str, fetch) -> dict:
        api_url = f"https://api.fxtwitter.com/{username}/status/{id}"
        response = await fetch(
            api_url,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; Domdown/1.0; +https://domdown.md)",
            },
        )

        if not response.ok:
            raise Exception(f"FxTwitter API request failed: {response.status}")

        return await response.json()

    def _to_date_string(self, date_str: Optional[str]) -> Optional[str]:
        if not date_str:
            return None
        try:
            from datetime import datetime

            return datetime.fromisoformat(date_str.replace("Z", "+00:00")).strftime("%Y-%m-%d")
        except Exception:
            return None

    def _build_article_result(self, data: dict) -> ExtractorResult:
        article = data["tweet"]["article"]
        blocks = article.get("content", {}).get("blocks", [])
        entity_map = article.get("content", {}).get("entityMap", [])
        media_entities = article.get("media_entities", [])

        content_html = self._render_article(blocks, entity_map, article.get("cover_media"), media_entities)
        handle = f"@{data['tweet']['author']['screen_name']}"
        published = self._to_date_string(article.get("created_at")) or self._to_date_string(
            data["tweet"].get("created_at")
        )

        result = ExtractorResult(
            content=content_html,
            content_html=content_html,
            variables={
                "title": article.get("title", ""),
                "author": handle,
                "site": "X (Twitter)",
                "description": article.get("preview_text", ""),
            },
        )

        if published:
            result.variables["published"] = published

        return result

    def _build_tweet_result(self, data: dict) -> ExtractorResult:
        tweet = data["tweet"]
        handle = f"@{tweet['author']['screen_name']}"
        post_content = self._render_tweet(tweet)
        content_html = build_content_html("twitter", post_content, "")
        published = self._to_date_string(tweet.get("created_at"))
        description = (tweet.get("text", "")).strip()[:140].replace(r"\s+", " ")

        result = ExtractorResult(
            content=content_html,
            content_html=content_html,
            variables={
                "title": self.post_title(handle, "X"),
                "author": handle,
                "site": "X (Twitter)",
                "description": description,
            },
        )

        if published:
            result.variables["published"] = published

        return result

    def _render_tweet(self, tweet: dict) -> str:
        text = tweet.get("raw_text", {}).get("text") or tweet.get("text", "")
        raw_facets = tweet.get("raw_text", {}).get("facets", []) or []
        facets = [f for f in raw_facets if f.get("type") != "media"]

        paragraphs = re.split(r"\n\n+", text)
        html_parts = []
        offset = 0

        for para in paragraphs:
            para_start = text.index(para, offset)
            para_end = para_start + len(para)
            offset = para_end

            is_blockquote = para.lstrip().startswith(">")
            para_text = para.lstrip()[1:].lstrip() if is_blockquote else para

            para_text_start = para_start
            if is_blockquote:
                para_text_start = (
                    para_start
                    + (len(para) - len(para.lstrip()))
                    + 1
                    + (len(para.lstrip()[1:].lstrip()) - len(para.lstrip()[1:].lstrip()))
                )

            rendered = self._apply_facets(para_text, para_text_start, para_end, facets)
            with_breaks = rendered.replace("\n", "<br>")

            if is_blockquote:
                html_parts.append(f"<blockquote><p>{with_breaks}</p></blockquote>")
            elif with_breaks.strip():
                html_parts.append(f"<p>{with_breaks}</p>")

        if tweet.get("media", {}).get("photos"):
            for photo in tweet["media"]["photos"]:
                html_parts.append(f'<img src="{escape_html(photo["url"])}" alt="">')

        return "\n".join(html_parts)

    def _apply_markers(self, text: str, markers: List[Marker]) -> str:
        if not markers:
            return escape_html(text)

        sorted_markers = sorted(
            markers, key=lambda m: (m.offset, -1 if m.type == "close" else 1 if m.type == "open" else 0)
        )

        result = ""
        pos = 0
        for marker in sorted_markers:
            if marker.offset > pos:
                result += escape_html(text[pos : marker.offset])
            result += marker.tag
            pos = marker.offset

        if pos < len(text):
            result += escape_html(text[pos:])

        return result

    def _apply_facets(self, text: str, text_start: int, text_end: int, facets: List[dict]) -> str:
        markers: List[Marker] = []

        for facet in facets:
            f_start, f_end = facet.get("indices", [0, 0])
            if f_end <= text_start or f_start >= text_end:
                continue

            rel_start = max(0, f_start - text_start)
            rel_end = min(len(text), f_end - text_start)

            if facet.get("type") == "italic":
                markers.append(Marker(offset=rel_start, type="open", tag="<em>"))
                markers.append(Marker(offset=rel_end, type="close", tag="</em>"))
            elif facet.get("type") == "mention" and facet.get("text"):
                url = f"https://x.com/{escape_html(facet['text'])}"
                markers.append(Marker(offset=rel_start, type="open", tag=f'<a href="{url}">'))
                markers.append(Marker(offset=rel_end, type="close", tag="</a>"))
            elif facet.get("type") == "url" and facet.get("original"):
                url = escape_html(facet["original"])
                markers.append(Marker(offset=rel_start, type="open", tag=f'<a href="{url}">'))
                markers.append(Marker(offset=rel_end, type="close", tag="</a>"))

        return self._apply_markers(text, markers)

    def _render_article(
        self,
        blocks: List[dict],
        entity_map: List[dict],
        cover_media: Optional[dict] = None,
        media_entities: Optional[List[dict]] = None,
    ) -> str:
        parts = []

        if cover_media and cover_media.get("media_info", {}).get("original_img_url"):
            parts.append(f'<img src="{escape_html(cover_media["media_info"]["original_img_url"])}" alt="Cover image">')

        i = 0
        while i < len(blocks):
            block = blocks[i]

            if block.get("type") == "unordered-list-item":
                items = []
                while i < len(blocks) and blocks[i].get("type") == "unordered-list-item":
                    items.append(f"<li>{self._render_inline_content(blocks[i], entity_map)}</li>")
                    i += 1
                parts.append(f"<ul>{''.join(items)}</ul>")
                continue

            html = self._render_block(block, entity_map, media_entities)
            if html:
                parts.append(html)
            i += 1

        return f'<article class="x-article">{chr(10).join(parts)}</article>'

    def _render_block(self, block: dict, entity_map: List[dict], media_entities: Optional[List[dict]] = None) -> str:
        block_type = block.get("type", "")
        text = block.get("text", "")

        if block_type == "unstyled":
            if not text.strip():
                return ""
            return f"<p>{self._render_inline_content(block, entity_map)}</p>"
        elif block_type == "header-two":
            return f"<h2>{self._render_inline_content(block, entity_map)}</h2>"
        elif block_type == "header-three":
            return f"<h3>{self._render_inline_content(block, entity_map)}</h3>"
        elif block_type == "atomic":
            return self._render_atomic_block(block, entity_map, media_entities)
        else:
            if not text.strip():
                return ""
            return f"<p>{self._render_inline_content(block, entity_map)}</p>"

    def _render_atomic_block(
        self, block: dict, entity_map: List[dict], media_entities: Optional[List[dict]] = None
    ) -> str:
        entity_ranges = block.get("entityRanges", [])
        if not entity_ranges:
            return ""

        entity_entry = next((e for e in entity_map if str(e.get("key")) == str(entity_ranges[0].get("key"))), None)
        if not entity_entry:
            return ""

        entity = entity_entry.get("value", {})

        if entity.get("type") == "MEDIA":
            media_items = entity.get("data", {}).get("mediaItems", [])
            caption = entity.get("data", {}).get("caption", "")
            images = []

            for item in media_items:
                if media_entities:
                    media_entity = next(
                        (e for e in media_entities if str(e.get("media_id")) == str(item.get("mediaId"))),
                        None,
                    )
                    if media_entity:
                        info = media_entity.get("media_info", {})
                        if info.get("__typename") == "ApiImage" and info.get("original_img_url"):
                            images.append(
                                f'<img src="{escape_html(info["original_img_url"])}" alt="{escape_html(caption) if caption else ""}">'
                            )
                        elif info.get("__typename") == "ApiVideo" and info.get("preview_image", {}).get(
                            "original_img_url"
                        ):
                            variants = sorted(
                                [
                                    v
                                    for v in info.get("variants", [])
                                    if v.get("content_type") == "video/mp4" and v.get("bit_rate")
                                ],
                                key=lambda v: v.get("bit_rate", 0),
                                reverse=True,
                            )
                            video_url = variants[0].get("url") if variants else None
                            preview_url = info["preview_image"]["original_img_url"]
                            if video_url:
                                images.append(
                                    f'<video src="{escape_html(video_url)}" poster="{escape_html(preview_url)}" controls></video>'
                                )
                            else:
                                images.append(
                                    f'<img src="{escape_html(preview_url)}" alt="{escape_html(caption) if caption else ""}">'
                                )

            if images and caption:
                return f"<figure>{''.join(images)}<figcaption>{escape_html(caption)}</figcaption></figure>"
            elif images:
                return "".join(f"<figure>{img}</figure>" for img in images)
            elif caption:
                return f"<figure><figcaption>{escape_html(caption)}</figcaption></figure>"
            return ""

        elif entity.get("type") == "MARKDOWN":
            markdown = entity.get("data", {}).get("markdown", "")
            code_match = re.match(r"^```(\w*)\n([\s\S]*?)\n?```$", markdown)
            if code_match:
                lang = code_match.group(1)
                code = code_match.group(2)
                lang_attr = f' class="language-{escape_html(lang)}" data-lang="{escape_html(lang)}"' if lang else ""
                return f"<pre><code{lang_attr}>{escape_html(code)}</code></pre>"
            return f"<pre><code>{escape_html(markdown)}</code></pre>"

        return ""

    def _render_inline_content(self, block: dict, entity_map: List[dict]) -> str:
        text = block.get("text", "")
        if not text:
            return ""

        markers: List[Marker] = []

        for range_item in block.get("inlineStyleRanges", []):
            if range_item.get("style") == "Bold":
                markers.append(Marker(offset=range_item.get("offset", 0), type="open", tag="<strong>"))
                markers.append(
                    Marker(
                        offset=range_item.get("offset", 0) + range_item.get("length", 0),
                        type="close",
                        tag="</strong>",
                    )
                )

        for range_item in block.get("entityRanges", []):
            entity_entry = next(
                (e for e in entity_map if str(e.get("key")) == str(range_item.get("key"))),
                None,
            )
            if entity_entry and entity_entry.get("value", {}).get("type") == "LINK":
                url = escape_html(entity_entry["value"]["data"].get("url", ""))
                markers.append(Marker(offset=range_item.get("offset", 0), type="open", tag=f'<a href="{url}">'))
                markers.append(
                    Marker(
                        offset=range_item.get("offset", 0) + range_item.get("length", 0),
                        type="close",
                        tag="</a>",
                    )
                )

        block_data = block.get("data", {})
        if block_data:
            mentions = block_data.get("mentions", [])
            for mention in mentions:
                url = f"https://x.com/{escape_html(mention.get('text', ''))}"
                markers.append(Marker(offset=mention.get("fromIndex", 0), type="open", tag=f'<a href="{url}">'))
                markers.append(Marker(offset=mention.get("toIndex", 0), type="close", tag="</a>"))

            urls = block_data.get("urls", [])
            for url_data in urls:
                url = escape_html(url_data.get("text", ""))
                markers.append(Marker(offset=url_data.get("fromIndex", 0), type="open", tag=f'<a href="{url}">'))
                markers.append(Marker(offset=url_data.get("toIndex", 0), type="close", tag="</a>"))

        return self._apply_markers(text, markers)
