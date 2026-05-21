from __future__ import annotations

import re
from typing import Any, List, Optional

from bs4 import Tag

from domdown.extractors._conversation import ConversationExtractor
from domdown.utils.dom import serialize_html


class GrokExtractor(ConversationExtractor):
    def __init__(
        self,
        document: Tag,
        url: str,
        schema_org_data: Any = None,
        options: Optional[Any] = None,
    ):
        super().__init__(document, url, schema_org_data, options)
        self.message_container_selector = ".relative.group.flex.flex-col.justify-center.w-full"
        self.message_bubbles = self.document.select(self.message_container_selector)
        self.footnotes: List[dict] = []
        self.footnote_counter = 0

    def can_extract(self) -> bool:
        return bool(self.message_bubbles) and len(self.message_bubbles) > 0

    def extract_messages(self) -> List[dict]:
        messages = []
        self.footnotes = []
        self.footnote_counter = 0

        if not self.message_bubbles or len(self.message_bubbles) == 0:
            return messages

        for container in self.message_bubbles:
            class_list = container.get("class", [])

            is_user_message = "items-end" in class_list
            is_grok_message = "items-start" in class_list

            if not is_user_message and not is_grok_message:
                continue

            message_bubble = container.select_one(".message-bubble")
            if not message_bubble:
                continue

            content = ""
            role = ""
            author = ""

            if is_user_message:
                content = message_bubble.get_text() or ""
                role = "user"
                author = "You"
            elif is_grok_message:
                role = "assistant"
                author = "Grok"

                cloned_bubble = message_bubble.clone()

                deep_search = cloned_bubble.select_one(".relative.border.border-border-l1.bg-surface-base")
                if deep_search:
                    deep_search.decompose()

                content = serialize_html(cloned_bubble)

                content = self._process_footnotes(content)

            if content.strip():
                messages.append(
                    {
                        "author": author,
                        "content": content.strip(),
                        "metadata": {"role": role},
                    }
                )

        return messages

    def get_footnotes(self) -> List[dict]:
        return self.footnotes

    def get_metadata(self) -> dict:
        title = self._get_title()
        message_count = len(self.message_bubbles) if self.message_bubbles else 0

        return {
            "title": title,
            "site": "Grok",
            "url": self.url,
            "message_count": message_count,
            "description": f"Grok conversation with {message_count} messages",
        }

    def _get_title(self) -> str:
        page_title = self.document.title.strip() if self.document.title else ""
        if page_title and page_title != "Grok" and not page_title.startswith("Grok by "):
            return re.sub(r"\s-\s*Grok$", "", page_title).strip()

        first_user_container = self.document.select_one(f"{self.message_container_selector}.items-end")
        if first_user_container:
            message_bubble = first_user_container.select_one(".message-bubble")
            if message_bubble:
                text = message_bubble.get_text("") or ""
                if len(text) > 50:
                    return text[:50] + "..."
                return text

        return "Grok Conversation"

    def _process_footnotes(self, content: str) -> str:
        link_pattern = re.compile(r'<a\s+(?:[^>]*?\s+)?href="([^"]*)"[^>]*>(.*?)</a>', re.IGNORECASE)

        def replace_link(match):
            url = match.group(1)
            link_text = match.group(2)

            if not url or url.startswith("#") or not re.match(r"^https?://", url, re.IGNORECASE):
                return match.group(0)

            footnote = next((fn for fn in self.footnotes if fn.get("url") == url), None)
            footnote_index = 0

            if not footnote:
                self.footnote_counter += 1
                footnote_index = self.footnote_counter

                try:
                    from urllib.parse import urlparse

                    domain = urlparse(url).netloc.replace("www.", "")
                    domain_text = f'<a href="{url}" target="_blank" rel="noopener noreferrer">{domain}</a>'
                except Exception:
                    domain_text = f'<a href="{url}" target="_blank" rel="noopener noreferrer">{url}</a>'

                self.footnotes.append({"url": url, "text": domain_text})
            else:
                for idx, fn in enumerate(self.footnotes):
                    if fn.get("url") == url:
                        footnote_index = idx + 1
                        break

            return f'{link_text}<sup id="fnref:{footnote_index}" class="footnote-ref"><a href="#fn:{footnote_index}" class="footnote-link">{footnote_index}</a></sup>'

        return link_pattern.sub(replace_link, content)
