"""Public entry points for HTML to Markdown conversion."""

from ._core import DomdownOptions, ExtractionCriteria
from ._pipeline import HtmlToMarkdownPipeline


def html_to_markdown(
    html: str,
    options: DomdownOptions | None = None,
    *,
    criteria: ExtractionCriteria | dict | str | None = None,
) -> str:
    """Convert raw HTML into a cleaned Markdown document.

    When frontmatter emission is enabled, the returned string includes the
    rendered frontmatter block followed by the cleaned Markdown body.
    """

    result = HtmlToMarkdownPipeline(options=options).run(html, criteria=criteria)
    return result.document or result.markdown
