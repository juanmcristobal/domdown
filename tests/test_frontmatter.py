from __future__ import annotations

from domdown._core import HtmlMetadata
from domdown._frontmatter import compose_document, render_frontmatter


def test_render_frontmatter_serializes_metadata_in_document_order() -> None:
    """Frontmatter serialization should be stable and YAML-like."""

    metadata = HtmlMetadata(
        title="Example Article",
        source="https://example.com/posts/example-article",
        author=("The Hacker News",),
        published="2025-12-29T15:14:00+05:30",
        created="2026-05-15",
        description="Example description.",
        tags=("Threat Intelligence", "Cloud Security"),
    )

    assert render_frontmatter(metadata) == (
        "---\n"
        "title: Example Article\n"
        'source: "https://example.com/posts/example-article"\n'
        "author:\n"
        '  - "The Hacker News"\n'
        'published: "2025-12-29T15:14:00+05:30"\n'
        "created: 2026-05-15\n"
        "description: Example description.\n"
        "tags:\n"
        "  - Threat Intelligence\n"
        "  - Cloud Security\n"
        "---"
    )


def test_compose_document_combines_frontmatter_and_body() -> None:
    """Document composition should prepend frontmatter only when present."""

    assert compose_document("---\na: b\n---", "\nBody\n") == "---\na: b\n---\nBody"
    assert compose_document(None, " Body ") == "Body"
