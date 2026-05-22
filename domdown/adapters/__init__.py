from __future__ import annotations

from .base import ArticleAdapter
from .github import GitHubAdapter
from .registry import AdapterRegistry, build_default_registry

__all__ = ["AdapterRegistry", "ArticleAdapter", "GitHubAdapter", "build_default_registry"]
