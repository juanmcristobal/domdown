from __future__ import annotations

from .arxiv import ArXivAdapter
from .base import ArticleAdapter
from .bleepingcomputer import BleepingComputerAdapter
from .cybersecuritynews import CyberSecurityNewsAdapter
from .dailysecu import DailySecuAdapter
from .domain import DeclarativeDomainAdapter, DomainAdapterSpec, make_domain_adapter
from .editorial import (
    CensysAdapter,
    CyberScoopEditorialAdapter,
    RailwayAdapter,
    SecurityAffairsAdapter,
    SecurityWeekAdapter,
    TheRegisterAdapter,
    WizAdapter,
)
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
    "CyberScoopEditorialAdapter",
    "CensysAdapter",
    "DailySecuAdapter",
    "DeclarativeDomainAdapter",
    "DomainAdapterSpec",
    "GBHackersAdapter",
    "GitHubAdapter",
    "MediumAdapter",
    "RailwayAdapter",
    "SecurityAffairsAdapter",
    "SecurityWeekAdapter",
    "TheRegisterAdapter",
    "TheHackerNewsAdapter",
    "WikipediaAdapter",
    "WizAdapter",
    "build_default_registry",
    "make_domain_adapter",
]
