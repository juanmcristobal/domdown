from __future__ import annotations

from domdown import DomdownOptions, html_to_markdown
from tests.fixtures import ARTICLE_SHELL_HTML


def test_synthetic_article_renders_without_page_chrome() -> None:
    """A generic article shell should render without chrome in the output."""

    output = html_to_markdown(ARTICLE_SHELL_HTML, DomdownOptions(created="2026-05-15"))

    assert 'author:\n  - "Example Author"' in output
    assert "tags:" not in output
    assert "Share this article" not in output
    assert "author_debug_inline" not in output
    assert "example.com/share?text=Example" not in output
    assert "### Background:" in output
    assert "**Tool Name**" in output
    assert "**![Tool Name](https://example.com/tool.png)**" in output
    assert "Thanks to the researchers who worked on this example." in output


def test_synthetic_article_omits_page_chrome_when_rendered() -> None:
    """The article-like fixture should render only the body, not page chrome."""

    output = html_to_markdown(ARTICLE_SHELL_HTML, DomdownOptions(created="2026-05-15"))

    assert 'author:\n  - "Example Author"' in output
    assert "tags:" not in output
    assert "Share this article" not in output
    assert "author_debug_inline" not in output
    assert "example.com/share?text=Example" not in output
    assert "### Background:" in output
    assert "**Tool Name**" in output
