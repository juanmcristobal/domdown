from __future__ import annotations

from .api import html_to_markdown
from ._core import DomdownOptions, HtmlMetadata, HtmlToMarkdownResult
from ._pipeline import HtmlToMarkdownPipeline

__version__ = "0.2.0"

__all__ = [
    "__version__",
    "DomdownOptions",
    "HtmlMetadata",
    "HtmlToMarkdownResult",
    "HtmlToMarkdownPipeline",
    "html_to_markdown",
]
