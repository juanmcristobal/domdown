from __future__ import annotations

from .arxiv import ArXivAdapter
from .base import ArticleAdapter
from .bleepingcomputer import BleepingComputerAdapter
from .cybersecuritynews import CyberSecurityNewsAdapter
from .domain import DeclarativeDomainAdapter, DomainAdapterSpec, make_domain_adapter
from .gbhackers import GBHackersAdapter
from .github import GitHubAdapter
from .medium import MediumAdapter
from .registry import AdapterRegistry, build_default_registry
from .thehackernews import TheHackerNewsAdapter
from .wikipedia import WikipediaAdapter

__all__ = [
    "AdapterRegistry",
    "ArticleAdapter",
    "ArXivAdapter",
    "BleepingComputerAdapter",
    "CyberSecurityNewsAdapter",
    "DeclarativeDomainAdapter",
    "DomainAdapterSpec",
    "GBHackersAdapter",
    "GitHubAdapter",
    "MediumAdapter",
    "TheHackerNewsAdapter",
    "WikipediaAdapter",
    "build_default_registry",
    "make_domain_adapter",
]
