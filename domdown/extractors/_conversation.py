from __future__ import annotations

from typing import List

from domdown.extractors._base import BaseExtractor
from domdown.types import ExtractorResult
from domdown.utils.dom import parse_html


class ConversationExtractor(BaseExtractor):
    def extract_messages(self) -> List[dict]:
        raise NotImplementedError

    def get_metadata(self) -> dict:
        raise NotImplementedError

    def get_footnotes(self) -> List[dict]:
        return []

    def extract(self) -> ExtractorResult:
        messages = self.extract_messages()
        metadata = self.get_metadata()
        footnotes = self.get_footnotes()
        raw_content_html = self._create_content_html(messages, footnotes)

        temp_doc = parse_html(f"<article>{raw_content_html}</article>")
        container = temp_doc.find("article")
        if container:
            from ..domdown import Domdown

            domdownd = Domdown(temp_doc).parse()
            content_html = domdownd.content
        else:
            content_html = raw_content_html

        return ExtractorResult(
            content=content_html,
            content_html=content_html,
            extracted_content={"message_count": str(len(messages))},
            variables={
                "title": metadata.get("title", "Conversation"),
                "site": metadata.get("site", ""),
                "description": metadata.get(
                    "description", f"{metadata.get('site', '')} conversation with {len(messages)} messages"
                ),
                "word_count": str(metadata.get("word_count", 0)),
            },
        )

    def _create_content_html(self, messages: List[dict], footnotes: List[dict]) -> str:
        messages_html_parts = []
        for index, message in enumerate(messages):
            timestamp_html = (
                f'<div class="message-timestamp">{message.get("timestamp", "")}</div>'
                if message.get("timestamp")
                else ""
            )

            has_paragraphs = bool(message.get("content", ""))
            content_html = message.get("content", "")
            if not has_paragraphs:
                content_html = f"<p>{content_html}</p>"

            data_attrs = ""
            if message.get("metadata"):
                data_attrs = " ".join(f'data-{key}="{value}"' for key, value in message["metadata"].items())

            messages_html_parts.append(
                f'<div class="message message-{message.get("author", "").lower()}" {data_attrs}>\n'
                f'    <div class="message-header">\n'
                f'        <p class="message-author"><strong>{message.get("author", "")}</strong></p>\n'
                f"        {timestamp_html}\n"
                f"    </div>\n"
                f'    <div class="message-content">\n'
                f"        {content_html}\n"
                f"    </div>\n"
                f"</div>{'' if index == len(messages) - 1 else chr(10) + '<hr>'}"
            )

        messages_html = "\n".join(messages_html_parts).strip()

        footnotes_html = ""
        if footnotes:
            footnotes_list = "".join(
                f'<li class="footnote" id="fn:{index + 1}">\n'
                f"    <p>\n"
                f'        <a href="{footnote.get("url", "#")}" target="_blank">{footnote.get("text", "")}</a>&nbsp;<a href="#fnref:{index + 1}" class="footnote-backref">↩</a>\n'
                f"    </p>\n"
                f"</li>"
                for index, footnote in enumerate(footnotes)
            )
            footnotes_html = f'<div id="footnotes">\n    <ol>\n        {footnotes_list}\n    </ol>\n</div>'

        return f"{messages_html}\n{footnotes_html}".strip()
