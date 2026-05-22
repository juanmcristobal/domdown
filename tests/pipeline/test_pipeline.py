from __future__ import annotations

from domdown import DomdownOptions, HtmlToMarkdownPipeline, html_to_markdown


def test_pipeline_declares_stages_in_execution_order() -> None:
    """The pipeline should keep stage ordering explicit and stable."""

    pipeline = HtmlToMarkdownPipeline()

    assert [stage.name for stage in pipeline.stages] == [
        "parse",
        "metadata",
        "clean",
        "preserve",
        "markdown",
        "postprocess",
        "frontmatter",
    ]


def test_html_to_markdown_round_trip_uses_pipeline_output() -> None:
    """The public helper should return the rendered document string."""

    html = "<html><body><div class='articlebody'><p>Hello</p></div></body></html>"

    assert html_to_markdown(html, DomdownOptions(emit_frontmatter=False)) == "Hello"
