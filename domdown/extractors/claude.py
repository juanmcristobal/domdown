from __future__ import annotations

import re
from typing import Any, List, Optional

from bs4 import Tag

from domdown.extractors._conversation import ConversationExtractor
from domdown.utils.dom import serialize_html


class ClaudeExtractor(ConversationExtractor):
    def __init__(
        self,
        document: Tag,
        url: str,
        schema_org_data: Any = None,
        options: Optional[Any] = None,
    ):
        super().__init__(document, url, schema_org_data, options)
        self.articles = self.document.select(
            'div[data-testid="user-message"], div[data-testid="assistant-message"], div.font-claude-response'
        )

    def can_extract(self) -> bool:
        return bool(self.articles) and len(self.articles) > 0

    def extract_messages(self) -> List[dict]:
        messages = []

        if not self.articles:
            return messages

        for article in self.articles:
            role = None
            content = None

            if article.has_attr("data-testid"):
                if article.get("data-testid") == "user-message":
                    role = "you"
                    content = serialize_html(article)
                else:
                    continue
            elif "font-claude-response" in article.get("class", []):
                role = "assistant"
                assistant_body = article.select_one(".standard-markdown")
                if assistant_body:
                    content = serialize_html(assistant_body)
                else:
                    content = serialize_html(article)
            else:
                continue

            if content:
                content = content.replace("\u200b", "")
                content = re.sub(r"<p[^>]*>\s*<\/p>", "", content)
                messages.append(
                    {
                        "author": "You" if role == "you" else "Claude",
                        "content": content.strip(),
                        "metadata": {"role": role},
                    }
                )

        return messages

    def get_metadata(self) -> dict:
        title = self._get_title()
        messages = self.extract_messages()

        return {
            "title": title,
            "site": "Claude",
            "url": self.url,
            "message_count": len(messages),
            "description": f"Claude conversation with {len(messages)} messages",
        }

    def _get_title(self) -> str:
        page_title = self.document.title.strip() if self.document.title else ""
        if page_title and page_title != "Claude":
            return re.sub(r" - Claude$", "", page_title)

        header_title = self.document.select_one("header .font-tiempos")
        if header_title:
            text = header_title.get_text().strip()
            if text:
                return text

        if self.articles:
            first_article = self.articles[0]
            first_user_message = first_article.select_one('[data-testid="user-message"]')
            if first_user_message:
                text = first_user_message.get_text() or ""
                if len(text) > 50:
                    return text[:50] + "..."
                return text

        return "Claude Conversation"
