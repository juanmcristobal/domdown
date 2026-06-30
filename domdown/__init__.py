from __future__ import annotations

from ._core import DomdownOptions, HtmlMetadata, HtmlToMarkdownResult
from ._pipeline import HtmlToMarkdownPipeline
from .api import html_to_markdown

__version__ = "0.3.0"

__all__ = [
    "__version__",
    "DomdownOptions",
    "HtmlMetadata",
    "HtmlToMarkdownResult",
    "HtmlToMarkdownPipeline",
    "html_to_markdown",
]
