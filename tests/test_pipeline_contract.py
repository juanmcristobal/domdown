from __future__ import annotations

from pathlib import Path
from dataclasses import fields

from domdown import DomdownOptions, HtmlMetadata, HtmlToMarkdownPipeline, HtmlToMarkdownResult


def test_pipeline_result_includes_metadata_and_frontmatter_slots() -> None:
    result_fields = {field.name for field in fields(HtmlToMarkdownResult)}

    assert "metadata" in result_fields
    assert "frontmatter" in result_fields
    assert "document" in result_fields


def test_options_include_metadata_and_frontmatter_controls() -> None:
    option_fields = {field.name for field in fields(DomdownOptions)}

    assert "extract_metadata" in option_fields
    assert "emit_frontmatter" in option_fields
    assert "prefer_article_body" in option_fields
    assert "created" in option_fields


def test_html_metadata_has_article_fields() -> None:
    metadata_fields = {field.name for field in fields(HtmlMetadata)}

    assert "title" in metadata_fields
    assert "source" in metadata_fields
    assert "description" in metadata_fields
    assert "published" in metadata_fields
    assert "tags" in metadata_fields
    assert "created" in metadata_fields


def test_pipeline_declares_metadata_and_frontmatter_stages() -> None:
    pipeline = HtmlToMarkdownPipeline()
    stage_names = [stage.name for stage in pipeline.stages]

    assert stage_names == [
        "parse",
        "metadata",
        "clean",
        "preserve",
        "markdown",
        "postprocess",
        "frontmatter",
    ]


def test_real_sample_file_is_supported_when_available() -> None:
    sample = Path(
        "/home/juanmcristobal/projects/llm-wiki-system/test_extract_html_raw/html/2025_12_27-malicious-npm-packages-used-as.html"
    )
    if not sample.exists():
        return

    from domdown import html_to_markdown

    html = sample.read_text(encoding="utf-8")
    output = html_to_markdown(html, DomdownOptions(created="2026-05-15"))

    assert "27 Malicious npm Packages Used as Phishing Infrastructure to Steal Login Credentials" in output
    assert "- secure-docs-app" in output
    assert "![Cybersecurity]" in output
