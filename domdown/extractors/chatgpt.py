from __future__ import annotations

import re
from typing import Any, List, Optional

from bs4 import Tag

from domdown.extractors._conversation import ConversationExtractor
from domdown.utils.dom import parse_html, serialize_html


class ChatGPTExtractor(ConversationExtractor):
    def __init__(
        self,
        document: Tag,
        url: str,
        schema_org_data: Any = None,
        options: Optional[Any] = None,
    ):
        super().__init__(document, url, schema_org_data, options)
        self.turns = self.document.select('[data-testid^="conversation-turn-"]')
        self.footnotes: List[dict] = []
        self.footnote_counter = 0
        self.cached_messages: Optional[List[dict]] = None

    def can_extract(self) -> bool:
        return bool(self.turns) and len(self.turns) > 0

    def extract_messages(self) -> List[dict]:
        if self.cached_messages:
            return self.cached_messages

        messages = []
        self.footnotes = []
        self.footnote_counter = 0

        if not self.turns:
            return messages

        for turn in self.turns:
            author_element = turn.select_one("h4.sr-only, h5.sr-only, h6.sr-only")
            author_text = ""
            if author_element:
                author_text = author_element.get_text().strip()
                author_text = re.sub(r":\s*$", "", author_text)

            message_el = turn.select_one("[data-message-author-role]")

            current_author_role = message_el.get("data-message-author_role", "") if message_el else ""

            content_el = message_el.select_one(".markdown, .whitespace-pre-wrap") if message_el else turn

            message_content = serialize_html(content_el)
            message_content = message_content.replace("\u200b", "")

            temp_div = parse_html(message_content)
            for el in temp_div.select("h4.sr-only, h5.sr-only, h6.sr-only, span[data-state='closed']"):
                el.decompose()
            message_content = serialize_html(temp_div)

            citation_pattern = re.compile(
                r"(&ZeroWidthSpace;)?(<span[^>]*?>\s*<a(?=[^>]*?href=\"([^\"]+)\")(?=[^>]*?target=\"_blank\")(?=[^>]*?rel=\"noopener\")[^>]*?>[\s\S]*?<\/a>\s*<\/span>)",
                re.IGNORECASE,
            )

            def replace_citation(match):
                _zws = match.group(1) or ""
                _span_structure = match.group(2) or ""
                url = match.group(3) or ""

                domain = ""
                fragment_text = ""

                try:
                    from urllib.parse import urlparse

                    parsed = urlparse(url)
                    domain = parsed.netloc.replace("www.", "")

                    if "#:~:text=" in url:
                        hash_part = url.split("#:~:text=")[1]
                        fragment_text = decodeURIComponent(hash_part)
                        fragment_text = fragment_text.replace("%2C", ",")

                        parts = fragment_text.split(",")
                        if len(parts) > 1 and parts[0].strip():
                            fragment_text = f" — {parts[0].trim()}..."
                        elif parts[0].strip():
                            fragment_text = f" — {fragment_text.strip()}"
                        else:
                            fragment_text = ""
                except Exception:
                    domain = url

                footnote_index = -1
                for idx, fn in enumerate(self.footnotes):
                    if fn.get("url") == url:
                        footnote_index = idx
                        break

                if footnote_index == -1:
                    self.footnote_counter += 1
                    footnote_number = self.footnote_counter
                    self.footnotes.append({"url": url, "text": f'<a href="{url}">{domain}</a>{fragment_text}'})
                else:
                    footnote_number = footnote_index + 1

                return f'<sup id="fnref:{footnote_number}"><a href="#fn:{footnote_number}">{footnote_number}</a></sup>'

            message_content = citation_pattern.sub(replace_citation, message_content)

            message_content = re.sub(r"<p[^>]*>\s*<\/p>", "", message_content)

            messages.append(
                {
                    "author": author_text,
                    "content": message_content.strip(),
                    "metadata": {"role": current_author_role or "unknown"},
                }
            )

        self.cached_messages = messages
        return messages

    def get_footnotes(self) -> List[dict]:
        return self.footnotes

    def get_metadata(self) -> dict:
        title = self._get_title()
        messages = self.extract_messages()

        return {
            "title": title,
            "site": "ChatGPT",
            "url": self.url,
            "message_count": len(messages),
            "description": f"ChatGPT conversation with {len(messages)} messages",
        }

    def _get_title(self) -> str:
        page_title = self.document.title.strip() if self.document.title else ""
        if page_title and page_title != "ChatGPT":
            return page_title

        if self.turns:
            first_turn = self.turns[0]
            first_user_turn = first_turn.select_one(".text-message")
            if first_user_turn:
                text = first_user_turn.get_text() or ""
                if len(text) > 50:
                    return text[:50] + "..."
                return text

        return "ChatGPT Conversation"


def decodeURIComponent(s: str) -> str:
    from urllib.parse import unquote

    return unquote(s)
