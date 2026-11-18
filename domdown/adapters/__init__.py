from __future__ import annotations

from .base import ArticleAdapter
from .domain import DeclarativeDomainAdapter, DomainAdapterSpec, make_domain_adapter
from .registry import AdapterRegistry, build_default_registry

__all__ = [
    "AdapterRegistry",
    "ArticleAdapter",
    "DeclarativeDomainAdapter",
    "DomainAdapterSpec",
    "build_default_registry",
    "make_domain_adapter",
]
