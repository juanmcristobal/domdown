from __future__ import annotations

from .api import html_to_markdown
from .pipeline import HtmlToMarkdownPipeline
from .types import DomdownOptions, HtmlMetadata, HtmlToMarkdownResult

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "DomdownOptions",
    "HtmlMetadata",
    "HtmlToMarkdownPipeline",
    "HtmlToMarkdownResult",
    "html_to_markdown",
]
