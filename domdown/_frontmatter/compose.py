from __future__ import annotations


def compose_document(frontmatter: str | None, markdown: str) -> str:
    """Combine frontmatter and Markdown body into a final document string."""

    if frontmatter:
        body = markdown.strip()
        return f"{frontmatter}\n{body}".strip()
    return markdown.strip()
