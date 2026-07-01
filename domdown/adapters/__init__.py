from __future__ import annotations

from .base import ArticleAdapter
from .bleepingcomputer import BleepingComputerAdapter
from .cybersecuritynews import CyberSecurityNewsAdapter
from .gbhackers import GBHackersAdapter
from .domain import DeclarativeDomainAdapter, DomainAdapterSpec, make_domain_adapter
from .github import GitHubAdapter
from .medium import MediumAdapter
from .registry import AdapterRegistry, build_default_registry
from .thehackernews import TheHackerNewsAdapter

__all__ = [
    "AdapterRegistry",
    "ArticleAdapter",
    "BleepingComputerAdapter",
    "CyberSecurityNewsAdapter",
    "DeclarativeDomainAdapter",
    "DomainAdapterSpec",
    "GBHackersAdapter",
    "GitHubAdapter",
    "MediumAdapter",
    "TheHackerNewsAdapter",
    "build_default_registry",
    "make_domain_adapter",
]
