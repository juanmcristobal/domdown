from __future__ import annotations

import inspect

import domdown


def test_public_api_exports_pipeline_interfaces() -> None:
    assert hasattr(domdown, "DomdownOptions")
    assert hasattr(domdown, "HtmlToMarkdownResult")
    assert hasattr(domdown, "HtmlToMarkdownPipeline")
    assert hasattr(domdown, "html_to_markdown")


def test_html_to_markdown_signature_is_html_first() -> None:
    signature = inspect.signature(domdown.html_to_markdown)

    assert list(signature.parameters) == ["html", "options"]
    assert signature.parameters["html"].annotation is str

