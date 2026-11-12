from __future__ import annotations

from ._core import CriteriaError, DomdownOptions, ExtractionCriteria, ExtractionPlan, ExtractionTrace, HtmlMetadata, HtmlToMarkdownResult
from ._pipeline import HtmlToMarkdownPipeline
from ._version import DOMDOWN_VERSION
from .api import html_to_markdown

__version__ = DOMDOWN_VERSION

__all__ = [
    "__version__",
    "DomdownOptions",
    "HtmlMetadata",
    "HtmlToMarkdownResult",
    "HtmlToMarkdownPipeline",
    "html_to_markdown",
    "CriteriaError",
    "ExtractionCriteria",
    "ExtractionPlan",
    "ExtractionTrace",
]
