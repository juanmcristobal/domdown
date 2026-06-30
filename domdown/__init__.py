from __future__ import annotations

from ._constants import DOMDOWN_VERSION
from ._core import DomdownOptions, HtmlMetadata, HtmlToMarkdownResult
from ._pipeline import HtmlToMarkdownPipeline
from .api import html_to_markdown

__version__ = DOMDOWN_VERSION

__all__ = [
    "__version__",
    "DomdownOptions",
    "HtmlMetadata",
    "HtmlToMarkdownResult",
    "HtmlToMarkdownPipeline",
    "html_to_markdown",
]
