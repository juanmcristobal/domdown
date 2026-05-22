from __future__ import annotations

import re


def postprocess_markdown(markdown: str) -> str:
    """Normalize Markdown spacing and strip outer whitespace."""

    text = markdown.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
