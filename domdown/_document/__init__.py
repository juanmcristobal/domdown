from __future__ import annotations

from .clean import clean_root
from .parse import parse_html
from .select import choose_root

__all__ = ["choose_root", "clean_root", "parse_html"]
