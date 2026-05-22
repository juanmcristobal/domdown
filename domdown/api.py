"""Public entry points for HTML to Markdown conversion."""

from .pipeline import HtmlToMarkdownPipeline
from .types import DomdownOptions


def html_to_markdown(html: str, options: DomdownOptions | None = None) -> str:
    """Convert raw HTML into cleaned Markdown text.

    This is the smallest public API surface for callers that only need the
    final markdown string and do not need to interact with the pipeline
    stages directly.
    """

    return HtmlToMarkdownPipeline(options=options).run(html).markdown
