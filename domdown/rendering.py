"""Backwards-compatible facade for the extraction pipeline helpers."""

from ._document import choose_root, clean_root, parse_html
from ._frontmatter import compose_document, render_frontmatter
from .markdown import postprocess_markdown, render_markdown
from ._metadata import extract_metadata
