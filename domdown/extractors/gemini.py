from __future__ import annotations

from typing import Any, List, Optional

from bs4 import Tag

from domdown.extractors._conversation import ConversationExtractor
from domdown.utils.dom import parse_html, serialize_html


class GeminiExtractor(ConversationExtractor):
    def __init__(
        self,
        document: Tag,
        url: str,
        schema_org_data: Any = None,
        options: Optional[Any] = None,
    ):
        super().__init__(document, url, schema_org_data, options)
        self.conversation_containers = self.document.select("div.conversation-container")
        self.footnotes: List[dict] = []
        self.message_count: Optional[int] = None

    def can_extract(self) -> bool:
        return bool(self.conversation_containers) and len(self.conversation_containers) > 0

    def extract_messages(self) -> List[dict]:
        self.message_count = 0
        messages = []

        if not self.conversation_containers:
            return messages

        self._extract_sources()

        for container in self.conversation_containers:
            user_query = container.select_one("user-query")
            if user_query:
                query_text_el = user_query.query_selector(".query-text")
                if query_text_el:
                    content = serialize_html(query_text_el)
                    messages.append(
                        {
                            "author": "You",
                            "content": content.strip(),
                            "metadata": {"role": "user"},
                        }
                    )

            model_response = container.select_one("model-response")
            if model_response:
                regular_content = model_response.select_one(".model-response-text .markdown")
                extended_content = model_response.select_one("#extended-response-markdown-content")
                content_element = extended_content or regular_content

                if content_element:
                    content = serialize_html(content_element)

                    temp_div = parse_html(content)

                    for el in temp_div.select(".table-content"):
                        el["class"] = list(el.get("class", []))
                        if "table-content" in el["class"]:
                            el["class"].remove("table-content")

                    content = serialize_html(temp_div)

                    messages.append(
                        {
                            "author": "Gemini",
                            "content": content.strip(),
                            "metadata": {"role": "assistant"},
                        }
                    )

        self.message_count = len(messages)
        return messages

    def _extract_sources(self) -> None:
        browse_items = self.document.select("browse-item")

        if browse_items:
            for item in browse_items:
                link = item.select_one("a")
                if link:
                    url = link.get("href", "")
                    domain_el = link.select_one(".domain")
                    domain = domain_el.get_text().strip() if domain_el else ""
                    title_el = link.select_one(".title")
                    title = title_el.get_text().strip() if title_el else ""

                    if url and (domain or title):
                        self.footnotes.append({"url": url, "text": f"{domain}: {title}" if title else domain})

    def get_footnotes(self) -> List[dict]:
        return self.footnotes

    def get_metadata(self) -> dict:
        title = self._get_title()
        message_count = self.message_count if self.message_count is not None else len(self.extract_messages())
        return {
            "title": title,
            "site": "Gemini",
            "url": self.url,
            "message_count": message_count,
            "description": f"Gemini conversation with {message_count} messages",
        }

    def _get_title(self) -> str:
        page_title = self.document.title.strip() if self.document.title else ""
        if page_title and page_title != "Gemini" and "Gemini" not in page_title:
            return page_title

        research_title = self.document.select_one(".title-text")
        if research_title:
            text = research_title.get_text().strip()
            if text:
                return text

        if self.conversation_containers:
            first_container = self.conversation_containers[0]
            first_user_query = first_container.select_one(".query-text")
            if first_user_query:
                text = first_user_query.get_text() or ""
                if len(text) > 50:
                    return text[:50] + "..."
                return text

        return "Gemini Conversation"
