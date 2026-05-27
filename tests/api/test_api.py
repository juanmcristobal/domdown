from __future__ import annotations

import inspect

import domdown


def test_public_api_exports_minimal_surface() -> None:
    """The package should expose only the intended public entry points."""

    assert hasattr(domdown, "DomdownOptions")
    assert hasattr(domdown, "HtmlMetadata")
    assert hasattr(domdown, "HtmlToMarkdownResult")
    assert hasattr(domdown, "HtmlToMarkdownPipeline")
    assert hasattr(domdown, "html_to_markdown")


def test_html_to_markdown_signature_is_html_first() -> None:
    """The main helper must accept raw HTML as the first argument."""

    signature = inspect.signature(domdown.html_to_markdown)

    assert list(signature.parameters) == ["html", "options"]
    assert signature.parameters["html"].annotation is str
