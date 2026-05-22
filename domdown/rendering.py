"""Backwards-compatible facade for the extraction pipeline helpers."""

from .document import choose_root, clean_root, parse_html
from .frontmatter import compose_document, render_frontmatter
from .markdown import postprocess_markdown, render_markdown
from .metadata import extract_metadata
