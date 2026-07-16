from __future__ import annotations

from domdown._core import HtmlMetadata
from domdown._frontmatter import compose_document, render_frontmatter


def test_render_frontmatter_serializes_metadata_in_document_order() -> None:
    """Frontmatter serialization should be stable and YAML-like."""

    metadata = HtmlMetadata(
        title="Example Article",
        source="https://example.com/posts/example-article",
        site_name="Example Platform",
        canonical_url="https://example.com/posts/example-article",
        language="en",
        image="https://example.com/image.png",
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
        "site_name: Example Platform\n"
        'canonical_url: "https://example.com/posts/example-article"\n'
        "language: en\n"
        "domdown_version: 0.3.5\n"
        'image: "https://example.com/image.png"\n'
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


def test_render_frontmatter_uses_fallback_fields_for_missing_metadata() -> None:
    """Frontmatter serialization should backfill missing fields from fallback options."""

    metadata = HtmlMetadata()

    assert render_frontmatter(
        metadata,
        {
            "title": "Fallback Title",
            "source": "https://example.com/posts/fallback-title",
            "canonical_url": "https://example.com/posts/fallback-title",
            "author": ("Fallback Author",),
            "tags": ("Threat Intelligence", "Campaign Analysis"),
        },
    ) == (
        "---\n"
        "title: Fallback Title\n"
        'source: "https://example.com/posts/fallback-title"\n'
        'canonical_url: "https://example.com/posts/fallback-title"\n'
        "domdown_version: 0.3.5\n"
        "author:\n"
        '  - "Fallback Author"\n'
        "tags:\n"
        "  - Threat Intelligence\n"
        "  - Campaign Analysis\n"
        "---"
    )


def test_render_frontmatter_accepts_list_and_string_fallbacks() -> None:
    """Fallback lists and strings should be normalized consistently."""

    metadata = HtmlMetadata()

    assert render_frontmatter(
        metadata,
        {
            "author": ["Fallback Author", " ", 123],
            "tags": "Threat Intelligence",
        },
    ) == (
        "---\n"
        "domdown_version: 0.3.5\n"
        "author:\n"
        '  - "Fallback Author"\n'
        "tags:\n"
        "  - Threat Intelligence\n"
        "---"
    )


def test_compose_document_combines_frontmatter_and_body() -> None:
    """Document composition should prepend frontmatter only when present."""

    assert compose_document("---\na: b\n---", "\nBody\n") == "---\na: b\n---\nBody"
    assert compose_document(None, " Body ") == "Body"
