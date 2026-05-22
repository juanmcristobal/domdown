"""Public entry points for HTML to Markdown conversion."""

from .pipeline import HtmlToMarkdownPipeline
from .types import DomdownOptions


def html_to_markdown(html: str, options: DomdownOptions | None = None) -> str:
    """Convert raw HTML into a cleaned Markdown document.

    When frontmatter emission is enabled, the returned string includes the
    rendered frontmatter block followed by the cleaned Markdown body.
    """

    result = HtmlToMarkdownPipeline(options=options).run(html)
    return result.document or result.markdown
