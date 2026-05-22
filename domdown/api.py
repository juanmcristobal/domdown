from .pipeline import HtmlToMarkdownPipeline
from .types import DomdownOptions


def html_to_markdown(html: str, options: DomdownOptions | None = None) -> str:
    """Convert HTML into cleaned markdown."""

    return HtmlToMarkdownPipeline(options=options).run(html).markdown
