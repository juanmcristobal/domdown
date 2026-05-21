"""Tests for YouTube transcript extraction.

Note: The YoutubeExtractor in domdown is not yet implemented.
These tests document the expected behavior based on the TypeScript implementation.
Many tests will be skipped or noted as requiring implementation.
"""

import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional

import pytest

from .helpers import create_extractor, get_transcript_panel_html


class TranscriptParser:
    """Helper class to parse YouTube transcript XML formats.

    This mimics the parseTranscriptXml method from the TypeScript implementation.
    """

    def __init__(self):
        self._segments: List[Dict[str, Any]] = []
        self._language_code: str = ""

    def parse(self, xml: str, language_code: str) -> Optional[Dict[str, Any]]:
        """Parse transcript XML and return transcript data."""
        self._language_code = language_code
        self._segments = []

        try:
            root = ET.fromstring(xml)
        except ET.ParseError:
            return None

        body = root.find(".//body") or root
        if body is None:
            body = root

        if root.tag == "transcript":
            self._parse_simple_format(root)
        else:
            self._parse_srv3_format(body)

        if not self._segments:
            return None

        text_output, html_output = self._format_output()
        return {
            "text": text_output,
            "html": html_output,
            "languageCode": self._language_code,
        }

    def _parse_simple_format(self, root: ET.Element) -> None:
        """Parse <text> format (simple format)."""
        for text_el in root.findall(".//text"):
            start = float(text_el.get("start", 0)) * 1000
            dur = float(text_el.get("dur", 0)) * 1000
            text = self._get_text_content(text_el)
            if text:
                self._segments.append(
                    {
                        "start": start,
                        "dur": dur,
                        "text": text,
                    }
                )

    def _parse_srv3_format(self, body: ET.Element) -> None:
        """Parse <p>/<s> format (srv3 format)."""
        for p_el in body.findall(".//p"):
            start = int(p_el.get("t", 0))
            dur = int(p_el.get("d", 0))
            text_parts = []
            for s_el in p_el.findall(".//s"):
                text_parts.append(self._get_text_content(s_el))
            if not text_parts:
                text_parts = [self._get_text_content(p_el)]
            if text_parts:
                self._segments.append(
                    {
                        "start": start,
                        "dur": dur,
                        "text": "".join(text_parts),
                    }
                )

    def _get_text_content(self, el: ET.Element) -> str:
        """Get text content, handling nested elements and entities."""
        import html

        text = ""
        if el.text:
            text += el.text
        for child in el:
            if child.tail:
                text += child.tail
        return html.unescape(text)

    def _format_output(self) -> tuple:
        """Format segments into text and HTML output."""
        from domdown.utils.dom import escape_html

        lines = []
        html_lines = ['<div class="youtube transcript"><h2>Transcript</h2>']

        for seg in self._segments:
            start_ms = seg["start"]
            text = seg["text"]

            if not text:
                continue

            timestamp = self._format_timestamp(start_ms)
            line = f"**{timestamp}** · {text}"
            lines.append(line)

            html_lines.append(
                f'<p class="transcript-segment">'
                f'<strong><span class="timestamp" data-timestamp="{start_ms}">{timestamp}</span></strong>'
                f" · {escape_html(text)}"
                f"</p>"
            )

        html_output = "\n".join(html_lines) + "\n</div>"
        return "\n".join(lines), html_output

    @staticmethod
    def _format_timestamp(start_ms: float) -> str:
        """Format milliseconds to timestamp string."""
        total_seconds = int(start_ms / 1000) if isinstance(start_ms, (int, float)) else 0
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"


class TestTranscriptParsing:
    """Tests for transcript XML parsing."""

    def test_parses_srv3_format(self):
        """Test parsing srv3 format with <p>/<s> elements."""
        xml = """<?xml version="1.0" encoding="utf-8"?>
<timedtext>
<body>
<p t="0" d="5000"><s>Hello </s><s>world.</s></p>
<p t="5000" d="3000"><s>Second line.</s></p>
<p t="65000" d="2000"><s>After one minute</s></p>
</body>
</timedtext>"""

        parser = TranscriptParser()
        result = parser.parse(xml, "en")

        assert result is not None
        assert result["languageCode"] == "en"

        lines = result["text"].split("\n")
        assert lines[0] == "**0:00** · Hello world."
        assert lines[1] == "**0:05** · Second line."
        assert lines[2] == "**1:05** · After one minute"

        assert '<p class="transcript-segment">' in result["html"]
        assert '<span class="timestamp"' in result["html"]
        assert "<h2>Transcript</h2>" in result["html"]

    def test_parses_simple_format(self):
        """Test parsing simple format with <text> elements."""
        xml = """<?xml version="1.0" encoding="utf-8"?>
<transcript>
<text start="0" dur="5">Hello world.</text>
<text start="5.5" dur="3">Second line.</text>
<text start="3661" dur="2">Hour mark</text>
</transcript>"""

        parser = TranscriptParser()
        result = parser.parse(xml, "es")

        assert result is not None
        assert result["languageCode"] == "es"

        lines = result["text"].split("\n")
        assert lines[0] == "**0:00** · Hello world."
        assert lines[1] == "**0:05** · Second line."
        assert lines[2] == "**1:01:01** · Hour mark"

    def test_decodes_html_entities(self):
        """Test HTML entity decoding including numeric entities."""
        xml = """<timedtext><body>
<p t="0" d="1000"><s>it&apos;s &amp; that&#39;s &quot;quoted.&quot;</s></p>
<p t="1000" d="1000"><s>&#x2019;smart&#x2019; &#8212; dash</s></p>
</body></timedtext>"""

        parser = TranscriptParser()
        result = parser.parse(xml, "en")

        assert result is not None

        lines = result["text"].split("\n")
        assert lines[0] == "**0:00** · it's & that's \"quoted.\""
        assert "smart" in lines[1] and "dash" in lines[1]

    def test_returns_none_for_empty_transcript(self):
        """Test that empty transcript returns None."""
        xml = """<?xml version="1.0" encoding="utf-8"?><timedtext><body></body></timedtext>"""

        parser = TranscriptParser()
        result = parser.parse(xml, "en")

        assert result is None

    def test_falls_back_to_stripping_tags_when_no_s_elements(self):
        """Test fallback to stripping tags when no <s> elements."""
        xml = """<timedtext><body>
<p t="0" d="5000">Plain text without s tags</p>
</body></timedtext>"""

        parser = TranscriptParser()
        result = parser.parse(xml, "en")

        assert result is not None
        assert result["text"] == "**0:00** · Plain text without s tags"

    def test_escapes_html_in_output(self):
        """Test that HTML in transcript segments is escaped in HTML output."""
        xml = """<timedtext><body>
<p t="0" d="1000"><s>a &lt;script&gt; tag</s></p>
</body></timedtext>"""

        parser = TranscriptParser()
        result = parser.parse(xml, "en")

        assert result is not None
        assert "a &lt;script&gt; tag" in result["html"]
        assert "a <script> tag" in result["text"]

    def test_collapse_newlines_within_caption_segments(self):
        """Test that newlines within caption segments are collapsed to spaces."""
        xml = """<?xml version="1.0" encoding="utf-8"?>
<timedtext format="3">
<body>
<p t="0" d="2690">- The first time I tried to use Obsidian,</p>
<p t="6180" d="2960">I couldn&#39;t quite get
it to do what I wanted.</p>
<p t="9140" d="3010">And frankly, I just didn&#39;t
get all of the hype.</p>
</body>
</timedtext>"""

        parser = TranscriptParser()
        result = parser.parse(xml, "en")

        assert result is not None
        text = result["text"]
        assert "I couldn't quite get" in text
        assert "to do what I wanted" in text
        assert "And frankly, I just didn't" in text


class TestYoutubeExtractorNotImplemented:
    """Tests documenting expected YouTube extractor behavior.

    These tests are skipped because the YouTubeExtractor is not yet implemented.
    They document the expected API and behavior from the TypeScript tests.
    """

    def test_extract_reads_existing_transcript_panel(self):
        """Test that extract reads existing transcript panel without opening it."""
        html = f"""
            <html>
                <body>
                    <ytd-video-description-transcript-section-renderer>
                        <button id="open-transcript">Show transcript</button>
                    </ytd-video-description-transcript-section-renderer>
                    {get_transcript_panel_html()}
                </body>
            </html>
        """

        doc = create_extractor(html, "https://www.youtube.com/watch?v=test123")

        from domdown.extractors.youtube import YoutubeExtractor

        extractor = YoutubeExtractor(doc, "https://www.youtube.com/watch?v=test123")

        result = extractor.extract()

        assert result.variables is not None
        assert result.variables.get("language") == "en"
        assert "**0:00** · Hello world." in (result.variables.get("transcript") or "")

    def test_extracts_mobile_youtube_dom(self):
        """Test transcript extraction from mobile YouTube DOM."""
        mobile_html = """
            <html>
                <body>
                    <ytm-macro-markers-list-renderer class="browsing-mode">
                        <div class="ytm-macro-markers-list-container">
                            <ytm-item-section-renderer>
                                <lazy-list>
                                    <macro-markers-panel-item-view-model>
                                        <timeline-chapter-view-model>
                                            <h3 class="ytwTimelineChapterViewModelTitle">Introduction</h3>
                                        </timeline-chapter-view-model>
                                    </macro-markers-panel-item-view-model>
                                    <macro-markers-panel-item-view-model>
                                        <timeline-item-view-model>
                                            <div class="ytwTimelineItemViewModelContentItems">
                                                <transcript-segment-view-model>
                                                    <div class="ytwTranscriptSegmentViewModelTimestamp">0:00</div>
                                                    <span class="yt-core-attributed-string" role="text">Hello and welcome to the show.</span>
                                                </transcript-segment-view-model>
                                            </div>
                                        </timeline-item-view-model>
                                    </macro-markers-panel-item-view-model>
                                </lazy-list>
                            </ytm-item-section-renderer>
                        </div>
                    </ytm-macro-markers-list-renderer>
                </body>
            </html>
        """

        doc = create_extractor(mobile_html, "https://m.youtube.com/watch?v=test123")

        from domdown.extractors.youtube import YoutubeExtractor

        extractor = YoutubeExtractor(doc, "https://m.youtube.com/watch?v=test123")

        result = extractor.extract()

        assert result.variables is not None
        assert result.variables.get("language") == "en"
        assert "**0:00** · Hello and welcome to the show." in (result.variables.get("transcript") or "")
        assert "Introduction" in result.content


class TestTimestampFormatting:
    """Tests for timestamp format parsing."""

    @pytest.mark.parametrize(
        "ms,expected",
        [
            (0, "0:00"),
            (5000, "0:05"),
            (60000, "1:00"),
            (65000, "1:05"),
            (3661000, "1:01:01"),
            (3599000, "59:59"),
        ],
    )
    def test_format_timestamp(self, ms: float, expected: str):
        """Test various timestamp formats."""
        result = TranscriptParser._format_timestamp(ms)
        assert result == expected


class TestCaptionTrackSelection:
    """Tests for caption track selection logic.

    These document the expected behavior for pickCaptionTrack.
    """

    def test_pick_caption_track_falls_back_from_regional_to_base(self):
        """Test fallback from regional language tags to base language tracks."""
        tracks = [
            {"languageCode": "en"},
            {"languageCode": "zh"},
            {"languageCode": "zh-Hant"},
        ]

        selected = self._pick_caption_track(tracks, "zh-CN")
        assert selected["languageCode"] == "zh"

    def test_pick_caption_track_prefers_exact_base_language(self):
        """Test that exact base-language track is preferred over regional variants."""
        tracks = [
            {"languageCode": "zh-Hant"},
            {"languageCode": "zh"},
            {"languageCode": "en"},
        ]

        selected = self._pick_caption_track(tracks, "zh")
        assert selected["languageCode"] == "zh"

    def test_pick_caption_track_prefers_non_asr_over_asr(self):
        """Test that non-ASR tracks are preferred over auto-generated ones."""
        tracks = [
            {"languageCode": "en", "kind": "asr"},
            {"languageCode": "en"},
        ]

        selected = self._pick_caption_track(tracks, "en")
        assert selected.get("kind") is None
        assert selected["languageCode"] == "en"

    def test_pick_caption_track_falls_back_to_asr_when_no_manual(self):
        """Test fallback to ASR when no manual tracks exist."""
        tracks = [
            {"languageCode": "en", "kind": "asr"},
        ]

        selected = self._pick_caption_track(tracks, "en")
        assert selected["kind"] == "asr"

    @staticmethod
    def _pick_caption_track(
        tracks: List[Dict[str, Any]],
        language: str,
    ) -> Optional[Dict[str, Any]]:
        """Pick the best caption track for a given language.

        This mimics the TypeScript pickCaptionTrack logic.
        """
        base_lang = language.split("-")[0]

        candidates = [t for t in tracks if t.get("languageCode") == language]
        if not candidates:
            candidates = [t for t in tracks if t.get("languageCode", "").startswith(base_lang)]
        if not candidates:
            candidates = list(tracks)

        non_asr = [t for t in candidates if t.get("kind") != "asr"]
        if non_asr:
            return non_asr[0]

        return candidates[0] if candidates else None
