from dataclasses import dataclass
from typing import List, Optional

from domdown.utils.dom import escape_html


@dataclass
class TranscriptSegment:
    start: float
    text: str
    speaker_change: bool
    speaker: Optional[int] = None


@dataclass
class TranscriptChapter:
    title: str
    start: float


@dataclass
class TranscriptResult:
    html: str
    text: str


def format_timestamp(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)

    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def build_transcript(
    site: str,
    segments: List[TranscriptSegment],
    chapters: Optional[List[TranscriptChapter]] = None,
) -> TranscriptResult:
    if chapters is None:
        chapters = []

    sorted_chapters = sorted(chapters, key=lambda c: c.start)
    chapter_idx = 0

    html_parts: List[str] = []
    text_parts: List[str] = []

    for segment in segments:
        while chapter_idx < len(sorted_chapters) and sorted_chapters[chapter_idx].start <= segment.start:
            title = sorted_chapters[chapter_idx].title
            html_parts.append(f"<h3>{escape_html(title)}</h3>")
            if text_parts:
                text_parts.append("")
            text_parts.append(f"### {title}")
            text_parts.append("")
            chapter_idx += 1

        timestamp = format_timestamp(segment.start)
        speaker_class = f" speaker-{segment.speaker}" if segment.speaker is not None else ""
        ts_html = f'<strong><span class="timestamp" data-timestamp="{segment.start}">{timestamp}</span></strong>'
        html_parts.append(f'<p class="transcript-segment{speaker_class}">{ts_html} · {escape_html(segment.text)}</p>')

        if segment.speaker_change and text_parts:
            text_parts.append("")
        text_parts.append(f"**{timestamp}** · {segment.text}")

    return TranscriptResult(
        html=f'<div class="{site} transcript">\n<h2>Transcript</h2>\n' + "\n".join(html_parts) + "\n</div>",
        text="\n".join(text_parts),
    )
