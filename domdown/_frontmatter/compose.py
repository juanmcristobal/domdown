from __future__ import annotations


def compose_document(frontmatter: str | None, markdown: str) -> str:
    if frontmatter:
        body = markdown.strip()
        return f"{frontmatter}\n{body}".strip()
    return markdown.strip()
