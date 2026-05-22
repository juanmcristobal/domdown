from __future__ import annotations

from dataclasses import fields

from domdown import DomdownOptions, HtmlMetadata, HtmlToMarkdownResult
from domdown._core import PipelineContext


def test_options_include_pipeline_controls() -> None:
    """DomdownOptions should expose the knobs required by the pipeline."""

    option_fields = {field.name for field in fields(DomdownOptions)}

    assert {
        "base_url",
        "created",
        "extract_metadata",
        "emit_frontmatter",
        "prefer_article_body",
        "frontmatter_tags",
        "preserve_images",
        "preserve_tables",
        "preserve_code_blocks",
        "strip_hidden",
        "remove_selectors",
        "keep_selectors",
        "unwrap_selectors",
    } <= option_fields


def test_metadata_result_and_context_surface() -> None:
    """Core result and context containers should expose all state slots."""

    metadata_fields = {field.name for field in fields(HtmlMetadata)}
    result_fields = {field.name for field in fields(HtmlToMarkdownResult)}
    context_fields = {field.name for field in fields(PipelineContext)}

    assert {"title", "source", "author", "published", "created", "description", "tags"} <= metadata_fields
    assert {"markdown", "cleaned_html", "metadata", "frontmatter", "document", "warnings"} <= result_fields
    assert {
        "html",
        "options",
        "document",
        "cleaned_html",
        "markdown",
        "metadata",
        "frontmatter",
        "rendered_document",
        "warnings",
    } <= context_fields
