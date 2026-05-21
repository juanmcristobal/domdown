from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from bs4 import Tag

from domdown.extractors._base import BaseExtractor, ExtractorOptions
from domdown.types import ExtractorResult
from domdown.utils.transcript import TranscriptChapter, TranscriptSegment, build_transcript

CJK_SENTENCE_PUNCT = "\u3002\uff01\uff1f"
CJK_CLOSE_QUOTES = "\u300d\u300f\uff09"
CJK_CHAR_RANGES = "\u4e00-\u9fff\u3400-\u4dbf"

SENTENCE_END = re.compile(rf"[.!?{CJK_SENTENCE_PUNCT}][\"'\u2019\u201D\){CJK_CLOSE_QUOTES}]*\s*$")
QUESTION_END = re.compile(rf"[?\uFF1F][\"'\u2019\u201D\){CJK_CLOSE_QUOTES}]*\s*$")
SPEAKER_MARKER = re.compile(r"^(>>|-\s)")
SPEAKER_STRIP = re.compile(r"^(>>\s*|-\s+)")
TRAILING_COMMA = re.compile(r",\s*$")
TRANSCRIPT_GROUP_GAP_SECONDS = 20
TRANSCRIPT_MAX_GROUP_SECONDS = 30
TURN_MERGE_MAX_WORDS = 80
TURN_MERGE_MAX_SPAN_SECONDS = 45
SHORT_UTTERANCE_MAX_WORDS = 3
FIRST_GROUP_MERGE_MIN_WORDS = 8

FETCH_TIMEOUT_MS = 4000

INNERTUBE_API_URL = "https://www.youtube.com/youtubei/v1/player?prettyPrint=false"
INNERTUBE_CLIENT_VERSION = "20.10.38"
INNERTUBE_CONTEXT = {"client": {"clientName": "ANDROID", "clientVersion": INNERTUBE_CLIENT_VERSION}}
INNERTUBE_USER_AGENT = f"com.google.android.youtube/{INNERTUBE_CLIENT_VERSION} (Linux; U; Android 14)"
INNERTUBE_NEXT_URL = "https://www.youtube.com/youtubei/v1/next?prettyPrint=false"
INNERTUBE_IOS_CONTEXT = {"client": {"clientName": "IOS", "clientVersion": "20.10.3"}}
INNERTUBE_WEB_CONTEXT = {"client": {"clientName": "WEB", "clientVersion": "2.20240101.00.00"}}


@dataclass
class TranscriptResult:
    html: str
    text: str
    language_code: Optional[str] = None


@dataclass
class TranscriptSelectors:
    segments: str
    timestamp: str
    text: str
    chapters: Optional[str] = None


DESKTOP_TRANSCRIPT_SELECTORS = TranscriptSelectors(
    segments="ytd-transcript-segment-renderer", timestamp=".segment-timestamp", text=".segment-text"
)

MOBILE_TRANSCRIPT_SELECTORS = TranscriptSelectors(
    segments="transcript-segment-view-model",
    timestamp=".ytwTranscriptSegmentViewModelTimestamp",
    text="span.yt-core-attributed-string",
    chapters="timeline-chapter-view-model h3",
)


def count_words(text: str) -> int:
    return len(text.split())


class YoutubeExtractor(BaseExtractor):
    def __init__(
        self,
        document: Tag,
        url: str,
        schema_org_data: Any = None,
        options: Optional[ExtractorOptions] = None,
    ):
        super().__init__(document, url, schema_org_data, options)
        self.video_element = self.document.select_one("video")
        self.inline_json_cache: Dict[str, Any] = {}
        self.schema_org_data = schema_org_data
        self._video_id: Optional[str] = None
        self.schema_org_data = schema_org_data

    def can_extract(self) -> bool:
        return True

    def can_extract_async(self) -> bool:
        return True

    def prefers_async(self) -> bool:
        return True

    def extract(self) -> ExtractorResult:
        return self._build_result(self._extract_transcript_from_existing_dom())

    async def extract_async(self) -> ExtractorResult:
        existing_transcript = self._extract_transcript_from_existing_dom()

        if self._should_use_existing_dom_transcript(existing_transcript):
            return self._build_result(existing_transcript)

        fetch = getattr(self.options, "fetch", None)
        if fetch:
            transcript = (
                (await self._fetch_transcript(fetch))
                or existing_transcript
                or (await self._extract_transcript_from_opened_dom())
            )
        else:
            transcript = existing_transcript
        return self._build_result(transcript)

    def _normalize_language_code(self, code: Optional[str]) -> str:
        if not code:
            return ""
        return code.strip().replace("_", "-").lower()

    def _language_code_matches_preference(self, language_code: Optional[str], preferred_lang: Optional[str]) -> bool:
        a = self._normalize_language_code(language_code)
        b = self._normalize_language_code(preferred_lang)
        if not a or not b:
            return False
        if a == b:
            return True
        a_base = a.split("-")[0]
        b_base = b.split("-")[0]
        return a_base == b_base and (a == a_base or b == b_base)

    def _should_use_existing_dom_transcript(self, transcript: Optional[TranscriptResult]) -> bool:
        if not transcript:
            return False
        if not self.options.language:
            return True
        return self._language_code_matches_preference(transcript.language_code, self.options.language)

    def _get_caption_tracks(self, player_data: Any) -> List[dict]:
        if not player_data:
            return []
        captions = player_data.get("captions", {})
        tracklist = captions.get("playerCaptionsTracklistRenderer", {})
        caption_tracks = tracklist.get("captionTracks", [])
        return caption_tracks if isinstance(caption_tracks, list) else []

    def _find_preferred_caption_track(
        self, caption_tracks: List[dict], preferred_lang: Optional[str]
    ) -> Optional[dict]:
        norm = self._normalize_language_code(preferred_lang)
        if not norm:
            return None
        base = norm.split("-")[0]

        normalized = [{"t": t, "code": self._normalize_language_code(t.get("languageCode"))} for t in caption_tracks]

        def find_best(predicate):
            matches = [item for item in normalized if predicate(item)]
            if matches:
                for m in matches:
                    if m["t"].get("kind") != "asr":
                        return m["t"]
                return matches[0]["t"]
            return None

        return (
            find_best(lambda item: item["code"] == norm)
            or find_best(lambda item: item["code"] == base)
            or find_best(lambda item: item["code"].split("-")[0] == base)
        )

    def _pick_caption_track(self, caption_tracks: List[dict]) -> Optional[dict]:
        preferred_lang = self.options.language if self.options else None
        if preferred_lang:
            match = self._find_preferred_caption_track(caption_tracks, preferred_lang)
            if match:
                return match

        non_asr = [t for t in caption_tracks if t.get("kind") != "asr"]
        pool = non_asr if non_asr else caption_tracks
        for track in pool:
            if track.get("languageCode") == "en":
                return track
        return pool[0] if pool else None

    def _get_track_display_name(self, track: dict) -> str:
        name = track.get("name", {})
        return name.get("simpleText", "") or "".join(run.get("text", "") for run in name.get("runs", []))

    def _normalize_language_label(self, label: str) -> str:
        return re.sub(r"\s*\([^)]*\)\s*", " ", label).replace(r"\s+", " ").strip().lower()

    def _get_transcript_language_code_from_dom(self) -> Optional[str]:
        lang_button = self.document.select_one(
            'ytd-engagement-panel-section-list-renderer[target-id="engagement-panel-searchable-transcript"] #footer '
            "yt-sort-filter-sub-menu-renderer yt-dropdown-menu button"
        )
        selected_label = lang_button.get_text().strip() if lang_button else ""
        caption_tracks = self._get_caption_tracks(self._get_validated_player_response())
        only_track = caption_tracks[0] if len(caption_tracks) == 1 else None

        if not selected_label:
            if only_track:
                return only_track.get("languageCode")
            return "en"

        normalized_selected_label = self._normalize_language_label(selected_label)
        for track in caption_tracks:
            if self._normalize_language_label(self._get_track_display_name(track)) == normalized_selected_label:
                return track.get("languageCode")

        if only_track:
            return only_track.get("languageCode")
        return "en"

    def _get_inline_chapters(self) -> List[Dict[str, Any]]:
        video_id = self._get_video_id()
        inline_data = self._parse_inline_json("ytInitialData")
        if not inline_data:
            return []

        if video_id:
            current_video_id = inline_data.get("currentVideoEndpoint", {}).get("watchEndpoint", {}).get("videoId")
            endpoint_video_id = inline_data.get("endpoint", {}).get("watchEndpoint", {}).get("videoId")
            if current_video_id != video_id and endpoint_video_id != video_id:
                return []

        chapters = self._extract_chapters_from_player_bar(inline_data)
        if chapters:
            return chapters

        return self._extract_chapters_from_engagement_panels(inline_data)

    def _get_transcript_container(self) -> Optional[Tag]:
        desktop = self.document.select_one(
            'ytd-engagement-panel-section-list-renderer[target-id="engagement-panel-searchable-transcript"] #segments-container'
        )
        if desktop:
            return desktop
        return self.document.select_one("ytm-macro-markers-list-renderer .ytm-macro-markers-list-container")

    def _get_transcript_selectors(self, container: Tag) -> Optional[TranscriptSelectors]:
        if container.select("ytd-transcript-segment-renderer"):
            return DESKTOP_TRANSCRIPT_SELECTORS
        if container.select("transcript-segment-view-model"):
            return MOBILE_TRANSCRIPT_SELECTORS
        return None

    def _get_video_data(self) -> dict:
        video_id = self._get_video_id()

        for script in self.document.select('script[type="application/ld+json"]'):
            try:
                text = script.get_text()
                if not text:
                    continue
                data = json.loads(text)
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if item.get("@type") != "VideoObject":
                        continue
                    if not video_id:
                        return item
                    item_id = item.get("@id") or item.get("url") or item.get("embedUrl") or ""
                    if video_id in item_id:
                        return item
            except json.JSONDecodeError:
                continue

        if video_id:
            og_url = self.document.select_one('meta[property="og:url"]')
            if og_url and og_url.get("content") and video_id in og_url["content"]:
                return {
                    "name": self._get_meta_content("og:title", ""),
                    "description": self._get_meta_content("og:description", ""),
                    "thumbnailUrl": self._get_meta_content("og:image", ""),
                }

        return {}

    def _get_meta_content(self, prop: str, default: str = "") -> str:
        el = self.document.select_one(f'meta[property="{prop}"]') or self.document.select_one(f'meta[name="{prop}"]')
        return el.get("content", default) if el else default

    def _get_channel_name(self, video_data: dict) -> str:
        from_dom = self._get_channel_name_from_dom()
        if from_dom:
            return from_dom

        from_player = self._get_channel_name_from_player_response()
        if from_player:
            return from_player

        return video_data.get("author", "")

    def _get_channel_name_from_dom(self) -> str:
        for selector in ['ytd-video-owner-renderer #channel-name a[href^="/@"]', "#owner-name a[href^='/@']"]:
            element = self.document.select_one(selector)
            if element:
                value = element.get_text().strip()
                if value:
                    return value

        return self._get_channel_name_from_microdata()

    def _get_channel_name_from_microdata(self) -> str:
        author_root = self.document.select_one('[itemprop="author"]')
        if not author_root:
            return ""

        meta_name = author_root.select_one('meta[itemprop="name"]')
        if meta_name and meta_name.get("content"):
            return meta_name["content"].strip()

        link_name = author_root.select_one('link[itemprop="name"]')
        if link_name and link_name.get("content"):
            return link_name["content"].strip()

        text_el = author_root.select_one('[itemprop="name"], a, span')
        return text_el.get_text().strip() if text_el else ""

    def _get_channel_name_from_player_response(self) -> str:
        data = self._get_validated_player_response()
        if not data:
            return ""
        return (
            data.get("videoDetails", {}).get("author")
            or data.get("videoDetails", {}).get("ownerChannelName")
            or data.get("microformat", {}).get("playerMicroformatRenderer", {}).get("ownerChannelName")
            or ""
        )

    def _get_validated_player_response(self) -> Optional[dict]:
        video_id = self._get_video_id()
        if not video_id:
            return None
        data = self._parse_inline_json("ytInitialPlayerResponse")
        if not data:
            return None
        detail_video_id = data.get("videoDetails", {}).get("videoId")
        microformat_video_id = data.get("microformat", {}).get("playerMicroformatRenderer", {}).get("externalVideoId")
        if detail_video_id == video_id or microformat_video_id == video_id:
            return data
        return None

    def _parse_inline_json(self, global_name: str) -> Optional[dict]:
        if global_name in self.inline_json_cache:
            return self.inline_json_cache[global_name]

        for script in self.document.select("script"):
            text = script.get_text()
            if not text or global_name not in text:
                continue

            start_index = text.find("{", text.find(global_name))
            if start_index == -1:
                continue

            depth = 0
            for i in range(start_index, len(text)):
                char = text[i]
                if char == "{":
                    depth += 1
                elif char == "}":
                    depth -= 1
                    if depth == 0:
                        json_text = text[start_index : i + 1]
                        try:
                            parsed = json.loads(json_text)
                            self.inline_json_cache[global_name] = parsed
                            return parsed
                        except json.JSONDecodeError:
                            break

        return None

    def _get_video_id(self) -> Optional[str]:
        if self._video_id is not None:
            return self._video_id

        try:
            parsed = urlparse(self.url)
            if parsed.netloc == "youtu.be":
                self._video_id = parsed.path[1:] if parsed.path else ""
            elif "/shorts/" in parsed.path:
                parts = parsed.path.split("/shorts/")
                if len(parts) > 1:
                    self._video_id = parts[1].split("/")[0]
                else:
                    self._video_id = ""
            else:
                from urllib.parse import parse_qs

                qs = parse_qs(parsed.query)
                self._video_id = qs.get("v", [""])[0]
        except Exception:
            self._video_id = ""

        return self._video_id

    def _build_transcript_from_container(
        self, container: Tag, chapters: List[Dict[str, Any]]
    ) -> Optional[TranscriptResult]:
        if not container.contents:
            return None

        selectors = self._get_transcript_selectors(container)
        if not selectors:
            return None

        segments = []

        dom_chapters = []
        if selectors.chapters:
            for ch in container.select(selectors.chapters):
                title = ch.get_text().strip()
                if not title:
                    continue

                next_timestamp = None
                next_segment = ch.find_next("transcript-segment-view-model")
                if next_segment:
                    next_timestamp = next_segment.select_one(selectors.timestamp)
                if not next_timestamp:
                    continue
                time_str = next_timestamp.get_text().strip()
                if not time_str:
                    continue
                seconds = self._parse_timestamp(time_str)
                if seconds is not None:
                    dom_chapters.append({"title": title, "start": seconds})

        for seg in container.select(selectors.segments):
            timestamp_el = seg.select_one(selectors.timestamp)
            text_el = seg.select_one(selectors.text)
            if not timestamp_el or not text_el:
                continue

            time_str = timestamp_el.get_text().strip()
            text = text_el.get_text().strip()
            if not text:
                continue

            seconds = self._parse_timestamp(time_str)
            if seconds is not None:
                segments.append({"start": seconds, "text": text})

        if not segments:
            return None

        effective_chapters = chapters if chapters else dom_chapters
        groups = self._group_transcript_segments(segments)
        result = build_transcript(
            "youtube", groups, [TranscriptChapter(c["title"], c["start"]) for c in effective_chapters]
        )

        return TranscriptResult(
            html=result.html, text=result.text, language_code=self._get_transcript_language_code_from_dom()
        )

    def _closest(self, el: Tag, selector: str) -> Optional[Tag]:
        current = el.parent
        while current:
            if isinstance(current, Tag):
                if current.name and selector in current.get("class", []):
                    return current
                if current.name == selector.split(".")[0].split("#")[0]:
                    try:
                        if selector.startswith("."):
                            if selector[1:] in current.get("class", []):
                                return current
                        elif selector.startswith("#"):
                            if current.get("id") == selector[1:]:
                                return current
                    except Exception:
                        pass
            current = current.parent if hasattr(current, "parent") else None
        return None

    def _extract_transcript_from_existing_dom(self) -> Optional[TranscriptResult]:
        try:
            container = self._get_transcript_container()
            if not container:
                return None

            return self._build_transcript_from_container(container, self._get_inline_chapters())
        except Exception as e:
            print(f"YoutubeExtractor: failed to extract transcript from existing DOM: {e}")
            return None

    def _build_result(self, transcript: Optional[TranscriptResult]) -> ExtractorResult:
        video_data = self._get_video_data()
        channel_name = self._get_channel_name(video_data)
        description = video_data.get("description", "")
        formatted_description = f"<p>{description.replace(chr(10), '<br>')}</p>"
        video_id = self._get_video_id() or ""
        content_html = f'<iframe width="560" height="315" src="https://www.youtube.com/embed/{video_id}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>{formatted_description}'

        if transcript and transcript.html:
            content_html += transcript.html

        variables: Dict[str, str] = {
            "title": video_data.get("name", ""),
            "author": channel_name,
            "site": "YouTube",
            "image": video_data.get("thumbnailUrl", ""),
            "published": video_data.get("uploadDate", ""),
            "description": description[:200].strip(),
        }

        if transcript and transcript.text:
            variables["transcript"] = transcript.text

        if transcript and transcript.language_code:
            variables["language"] = transcript.language_code

        return ExtractorResult(
            content=content_html,
            content_html=content_html,
            extracted_content={"video_id": video_id, "author": channel_name},
            variables=variables,
        )

    def _parse_timestamp(self, ts: str) -> Optional[float]:
        parts = [float(p) for p in ts.split(":")]
        if any(p != p or p != int(p) for p in parts):
            return None
        if len(parts) == 3:
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        if len(parts) == 2:
            return parts[0] * 60 + parts[1]
        return None

    async def _fetch_transcript(self, fetch) -> Optional[TranscriptResult]:
        try:
            video_id = self._get_video_id()
            if not video_id:
                return None

            chapters_promise = self._fetch_chapters(video_id, fetch)

            inline_track = self._get_inline_caption_track()
            inline_xml_promise = (
                self._fetch_caption_xml(inline_track, chapters_promise, fetch) if inline_track else None
            )

            player_data = await self._fetch_player_data(video_id, fetch)
            api_track = player_data._pick_caption_track(self._get_caption_tracks(player_data)) if player_data else None

            api_xml_promise = None
            if api_track and api_track.get("baseUrl") and api_track["baseUrl"] != inline_track.get("baseUrl"):
                api_xml_promise = self._fetch_caption_xml(api_track, chapters_promise, fetch)

            if api_xml_promise:
                api_result = await api_xml_promise
                if api_result:
                    return api_result

            if inline_xml_promise:
                return await inline_xml_promise

            return None
        except Exception as e:
            print(f"YoutubeExtractor: failed to fetch transcript: {e}")
            return None

    def _get_inline_caption_track(self) -> Optional[dict]:
        data = self._get_validated_player_response()
        tracks = self._get_caption_tracks(data)
        if not tracks:
            return None
        track = self._pick_caption_track(tracks)
        return track if track and track.get("baseUrl") else None

    async def _fetch_caption_xml(self, track: dict, chapters_promise, fetch) -> Optional[TranscriptResult]:
        try:
            caption_url = track.get("baseUrl", "")
            if not caption_url:
                return None

            parsed = urlparse(caption_url)
            if not parsed.netloc.endswith(".youtube.com"):
                return None

            headers = {"User-Agent": "Mozilla/5.0"}
            if self.options and self.options.language:
                headers["Accept-Language"] = self.options.language

            response = await fetch(caption_url, headers=headers)

            if not response.ok:
                return None

            try:
                xml = await response.text()
            except Exception:
                return None

            if not xml:
                return None

            chapters = await chapters_promise if chapters_promise else []
            return self._parse_transcript_xml(xml, track.get("languageCode", "en"), chapters)
        except Exception:
            return None

    async def _fetch_player_data(self, video_id: str, fetch) -> Optional[dict]:
        try:
            headers = {"Content-Type": "application/json"}
            if self.options and self.options.language:
                headers["Accept-Language"] = self.options.language

            resp = await fetch(
                INNERTUBE_API_URL,
                method="POST",
                headers=headers,
                body=json.dumps({"context": INNERTUBE_IOS_CONTEXT, "videoId": video_id}),
            )
            if resp.ok:
                data = await resp.json()
                if self._get_caption_tracks(data):
                    return data
        except Exception:
            pass

        try:
            headers = {"Content-Type": "application/json", "User-Agent": INNERTUBE_USER_AGENT}
            if self.options and self.options.language:
                headers["Accept-Language"] = self.options.language
            resp = await fetch(
                INNERTUBE_API_URL,
                method="POST",
                headers=headers,
                body=json.dumps({"context": INNERTUBE_CONTEXT, "videoId": video_id}),
            )
            if resp.ok:
                data = await resp.json()
                if self._get_caption_tracks(data):
                    return data
        except Exception:
            pass

        try:
            headers = {"Content-Type": "application/json"}
            if self.options and self.options.language:
                headers["Accept-Language"] = self.options.language
            resp = await fetch(
                INNERTUBE_API_URL,
                method="POST",
                headers=headers,
                body=json.dumps({"context": INNERTUBE_WEB_CONTEXT, "videoId": video_id}),
            )
            if resp.ok:
                data = await resp.json()
                if self._get_caption_tracks(data):
                    return data
        except Exception:
            pass

        fallback_data = self._parse_inline_json("ytInitialPlayerResponse")
        if fallback_data and self._get_caption_tracks(fallback_data):
            return fallback_data

        return None

    async def _fetch_chapters(self, video_id: str, fetch) -> List[Dict[str, Any]]:
        inline_chapters = self._get_inline_chapters()
        if inline_chapters:
            return inline_chapters

        try:
            headers = {"Content-Type": "application/json"}
            if self.options and self.options.language:
                headers["Accept-Language"] = self.options.language

            resp = await fetch(
                INNERTUBE_NEXT_URL,
                method="POST",
                headers=headers,
                body=json.dumps({"context": INNERTUBE_WEB_CONTEXT, "videoId": video_id}),
            )
            if not resp.ok:
                return []
            data = await resp.json()

            chapters = self._extract_chapters_from_player_bar(data)
            if chapters:
                return chapters

            return self._extract_chapters_from_engagement_panels(data)
        except Exception:
            return []

    def _extract_chapters_from_player_bar(self, data: dict) -> List[Dict[str, Any]]:
        chapters = []
        panels = (
            data.get("playerOverlays", {})
            .get("playerOverlayRenderer", {})
            .get("decoratedPlayerBarRenderer", {})
            .get("decoratedPlayerBarRenderer", {})
            .get("playerBar", {})
            .get("multiMarkersPlayerBarRenderer", {})
            .get("markersMap", [])
        )

        if not isinstance(panels, list):
            return chapters

        for panel in panels:
            markers = panel.get("value", {}).get("chapters", [])
            if not isinstance(markers, list):
                continue
            for marker in markers:
                ch = marker.get("chapterRenderer")
                if not ch:
                    continue
                title = ch.get("title", {}).get("simpleText", "")
                start_ms = ch.get("timeRangeStartMillis")
                if title and isinstance(start_ms, (int, float)):
                    chapters.append({"title": title, "start": start_ms / 1000})

        return chapters

    def _extract_chapters_from_engagement_panels(self, data: dict) -> List[Dict[str, Any]]:
        chapters = []
        panels = data.get("engagementPanels", [])
        if not isinstance(panels, list):
            return chapters

        for panel in panels:
            content = panel.get("engagementPanelSectionListRenderer", {}).get("content")
            items = content.get("macroMarkersListRenderer", {}).get("contents", [])
            if not isinstance(items, list):
                continue

            for item in items:
                renderer = item.get("macroMarkersListItemRenderer")
                if not renderer:
                    continue
                title = renderer.get("title", {}).get("simpleText", "")
                time_str = renderer.get("timeDescription", {}).get("simpleText", "")
                if not title or not time_str:
                    continue

                seconds = self._parse_timestamp(time_str)
                if seconds is not None:
                    chapters.append({"title": title, "start": seconds})

        return chapters

    def _parse_transcript_xml(
        self, xml: str, language_code: str, chapters: List[Dict[str, Any]] = None
    ) -> Optional[TranscriptResult]:
        if chapters is None:
            chapters = []

        segments = []

        p_regex = re.compile(r'<p\s+t="(\d+)"[^>]*>([\s\S]*?)</p>')
        for match in p_regex.finditer(xml):
            start_ms = int(match.group(1))
            inner = match.group(2)

            text = ""
            s_regex = re.compile(r"<s[^>]*>([^<]*)</s>")
            for s_match in s_regex.finditer(inner):
                text += s_match.group(1)

            if not text:
                text = re.sub(r"<[^>]+>", "", inner)

            text = text.replace("\n", " ").replace(r"\s{2,}", " ")
            text = self._decode_entities(text)

            if text.strip():
                segments.append({"start": start_ms / 1000, "text": text.strip()})

        if not segments:
            text_regex = re.compile(r'<text\s+start="([^"]*)"[^>]*>([\s\S]*?)</text>')
            for match in text_regex.finditer(xml):
                start = float(match.group(1))
                text = self._decode_entities(
                    match.group(2).replace("<[^>]+>", "").replace("\n", " ").replace(r"\s{2,}", " ")
                )
                if text.strip():
                    segments.append({"start": start, "text": text.strip()})

        if not segments:
            return None

        groups = self._group_transcript_segments(segments)
        result = build_transcript(
            "youtube",
            groups,
            [TranscriptChapter(c["title"], c["start"]) for c in chapters],
        )

        return TranscriptResult(html=result.html, text=result.text, language_code=language_code)

    def _decode_entities(self, text: str) -> str:
        text = text.replace("&amp;", "&")
        text = text.replace("&lt;", "<")
        text = text.replace("&gt;", ">")
        text = text.replace("&quot;", '"')
        text = text.replace("&#39;", "'")
        text = text.replace("&apos;", "'")
        text = re.sub(r"&#x([0-9a-fA-F]+);", lambda m: chr(int(m.group(1), 16)), text)
        text = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), text)
        return text

    def _extract_transcript_from_opened_dom(self) -> Optional[TranscriptResult]:
        return None

    def _group_transcript_segments(self, segments: List[Dict[str, Any]]) -> List[TranscriptSegment]:
        if not segments:
            return []

        has_speaker_markers = any(SPEAKER_MARKER.match(s["text"]) for s in segments)
        if has_speaker_markers:
            return self._group_by_speaker(segments)
        return self._group_by_sentence(segments)

    def _group_by_speaker(self, segments: List[Dict[str, Any]]) -> List[TranscriptSegment]:
        turns = []
        current_turn = None
        speaker_index = -1
        prev_seg_text = ""

        for seg in segments:
            is_speaker_change = bool(SPEAKER_MARKER.match(seg["text"]))
            clean_text = SPEAKER_STRIP.sub("", seg["text"])

            prev_ends_with_comma = bool(TRAILING_COMMA.search(prev_seg_text))
            prev_ended_sentence = bool(SENTENCE_END.search(prev_seg_text)) or not prev_seg_text
            is_real_speaker_change = is_speaker_change and prev_ended_sentence and not prev_ends_with_comma

            if is_real_speaker_change:
                if current_turn:
                    turns.append(current_turn)
                speaker_index = (speaker_index + 1) % 2
                current_turn = {
                    "start": seg["start"],
                    "segments": [{"start": seg["start"], "text": clean_text}],
                    "speaker_change": True,
                    "speaker": speaker_index,
                }
            else:
                if not current_turn:
                    current_turn = {"start": seg["start"], "segments": [], "speaker_change": False}
                current_turn["segments"].append({"start": seg["start"], "text": clean_text})

            prev_seg_text = clean_text

        if current_turn:
            turns.append(current_turn)

        self._split_affirmative_turns(turns)

        groups = []
        for turn in turns:
            sentence_groups = (
                self._merge_sentence_groups_within_turn(self._group_by_sentence(turn["segments"]))
                if turn.get("speaker") is not None
                else self._group_by_sentence(turn["segments"])
            )
            for i, sg in enumerate(sentence_groups):
                groups.append(
                    TranscriptSegment(
                        start=sg["start"],
                        text=sg["text"],
                        speaker_change=i == 0 and turn.get("speaker_change", False),
                        speaker=turn.get("speaker"),
                    )
                )

        return groups

    def _split_affirmative_turns(self, turns: List[dict]) -> None:
        affirmative_pattern = re.compile(
            r"^(mhm|yeah|yes|yep|right|okay|ok|absolutely|sure|exactly|uh-huh|mm-hmm)[.!,]?\s+", re.IGNORECASE
        )

        i = 0
        while i < len(turns):
            turn = turns[i]
            if turn.get("speaker") is None or not turn.get("segments"):
                i += 1
                continue

            first_seg = turn["segments"][0]
            match = affirmative_pattern.search(first_seg["text"])
            if not match:
                i += 1
                continue

            if re.search(r",\s*$", match.group(0)):
                i += 1
                continue

            remainder = first_seg["text"][match.end() :].strip()
            rest_segments = turn["segments"][1:]
            rest_words = count_words(remainder) + sum(count_words(s["text"]) for s in rest_segments)
            if rest_words < 30:
                i += 1
                continue

            affirmative_text = match.group(0).rstrip()
            new_rest_segments = (
                [{"start": first_seg["start"], "text": remainder}] + rest_segments if remainder else rest_segments
            )

            affirmative_turn = {
                "start": turn["start"],
                "segments": [{"start": first_seg["start"], "text": affirmative_text}],
                "speaker_change": turn.get("speaker_change"),
                "speaker": turn.get("speaker"),
            }
            rest_turn = {
                "start": new_rest_segments[0]["start"],
                "segments": new_rest_segments,
                "speaker_change": True,
                "speaker": 1 if turn.get("speaker") == 0 else 0,
            }

            turns[i : i + 1] = [affirmative_turn, rest_turn]
            i += 1

    def _merge_sentence_groups_within_turn(self, groups: List[dict]) -> List[dict]:
        if len(groups) <= 1:
            return groups

        merged = []
        current = dict(groups[0])
        current_is_first_in_turn = True

        for i in range(1, len(groups)):
            next_group = groups[i]
            if self._should_merge_sentence_groups(current, next_group, current_is_first_in_turn):
                current["text"] = f"{current['text']} {next_group['text']}"
            else:
                merged.append(current)
                current = dict(next_group)
                current_is_first_in_turn = False

        merged.append(current)
        return merged

    def _should_merge_sentence_groups(self, current: dict, next_group: dict, current_is_first_in_turn: bool) -> bool:
        current_words = count_words(current["text"])
        next_words = count_words(next_group["text"])

        if self._is_short_standalone_utterance(current["text"], current_words) or self._is_short_standalone_utterance(
            next_group["text"], next_words
        ):
            return False

        if current_is_first_in_turn and current_words < FIRST_GROUP_MERGE_MIN_WORDS:
            return False

        if QUESTION_END.search(current["text"]) or QUESTION_END.search(next_group["text"]):
            return False

        if current_words + next_words > TURN_MERGE_MAX_WORDS:
            return False

        if next_group["start"] - current["start"] > TURN_MERGE_MAX_SPAN_SECONDS:
            return False

        return True

    def _is_short_standalone_utterance(self, text: str, words: Optional[int] = None) -> bool:
        w = words if words is not None else count_words(text)
        return w > 0 and w <= SHORT_UTTERANCE_MAX_WORDS and bool(SENTENCE_END.search(text))

    def _group_by_sentence(self, segments: List[Dict[str, Any]]) -> List[TranscriptSegment]:
        groups = []
        pending = []

        def push_group(segs):
            text = " ".join(s["text"] for s in segs).strip()
            if text:
                groups.append(TranscriptSegment(start=segs[0]["start"], text=text, speaker_change=False))

        def flush_all():
            if pending:
                push_group(pending)
                pending.clear()

        for seg in segments:
            if pending and seg["start"] - pending[-1]["start"] > TRANSCRIPT_GROUP_GAP_SECONDS:
                flush_all()

            pending.append(seg)

            if SENTENCE_END.search(seg["text"]):
                flush_all()
                continue

            if seg["start"] - pending[0]["start"] >= TRANSCRIPT_MAX_GROUP_SECONDS:
                break_idx = self._find_natural_break(pending)
                if 0 < break_idx < len(pending):
                    push_group(pending[:break_idx])
                    pending = pending[break_idx:]
                else:
                    flush_all()

        flush_all()
        return groups

    def _find_natural_break(self, segments: List[Dict[str, Any]]) -> int:
        if len(segments) <= 1:
            return -1

        min_start = segments[0]["start"] + TRANSCRIPT_MAX_GROUP_SECONDS / 2

        for i in range(len(segments) - 1, -1, -1):
            if segments[i]["start"] < min_start:
                break
            match = re.search(
                rf"^(.*[.!?][\"'\u2019\u201D)]*)\\s+([A-Z].*)$|^(.*[{CJK_SENTENCE_PUNCT}][{CJK_CLOSE_QUOTES}]*)([{CJK_CHAR_RANGES}].*)$",
                segments[i]["text"],
            )
            if match:
                before = match.group(1) or match.group(3)
                after = match.group(2) or match.group(4)
                start = segments[i]["start"]
                segments[i : i + 1] = [{"start": start, "text": before}, {"start": start, "text": after}]
                return i + 1

        best_idx = -1
        best_gap = 0

        for i in range(1, len(segments)):
            if segments[i]["start"] < min_start:
                continue
            gap = segments[i]["start"] - segments[i - 1]["start"]
            if gap >= best_gap:
                best_gap = gap
                best_idx = i

        return best_idx
