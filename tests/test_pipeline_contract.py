from __future__ import annotations

from dataclasses import fields

from domdown import DomdownOptions, HtmlMetadata, HtmlToMarkdownPipeline, HtmlToMarkdownResult


def test_pipeline_result_includes_metadata_and_frontmatter_slots() -> None:
    result_fields = {field.name for field in fields(HtmlToMarkdownResult)}

    assert "metadata" in result_fields
    assert "frontmatter" in result_fields


def test_options_include_metadata_and_frontmatter_controls() -> None:
    option_fields = {field.name for field in fields(DomdownOptions)}

    assert "extract_metadata" in option_fields
    assert "emit_frontmatter" in option_fields
    assert "prefer_article_body" in option_fields


def test_html_metadata_has_article_fields() -> None:
    metadata_fields = {field.name for field in fields(HtmlMetadata)}

    assert "title" in metadata_fields
    assert "source" in metadata_fields
    assert "description" in metadata_fields
    assert "published" in metadata_fields
    assert "tags" in metadata_fields


def test_pipeline_declares_metadata_and_frontmatter_stages() -> None:
    pipeline = HtmlToMarkdownPipeline()
    stage_names = [stage.name for stage in pipeline.stages]

    assert stage_names == [
        "parse",
        "metadata",
        "clean",
        "preserve",
        "markdown",
        "frontmatter",
        "postprocess",
    ]
