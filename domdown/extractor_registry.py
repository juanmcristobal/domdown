from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable, List, Optional, Pattern, Type, Union
from urllib.parse import urlparse

from bs4 import Tag

from domdown.extractors._base import BaseExtractor, ExtractorOptions


@dataclass
class ExtractorMapping:
    patterns: List[Union[str, Pattern[str]]]
    extractor_cls: Type[BaseExtractor]


class ExtractorRegistry:
    _mappings: List[ExtractorMapping] = []

    @classmethod
    def _ensure_initialized(cls) -> None:
        if not cls._mappings:
            cls.initialize()

    @classmethod
    def initialize(cls) -> None:
        from .extractors.bbcode_data import BbcodeDataExtractor
        from .extractors.bluesky import BlueskyExtractor
        from .extractors.c2_wiki import C2WikiExtractor
        from .extractors.chatgpt import ChatGPTExtractor
        from .extractors.claude import ClaudeExtractor
        from .extractors.discourse import DiscourseExtractor
        from .extractors.gemini import GeminiExtractor
        from .extractors.github import GitHubExtractor
        from .extractors.grok import GrokExtractor
        from .extractors.hackernews import HackerNewsExtractor
        from .extractors.leetcode import LeetCodeExtractor
        from .extractors.linkedin import LinkedInExtractor
        from .extractors.lwn import LwnExtractor
        from .extractors.mastodon import MastodonExtractor
        from .extractors.medium import MediumExtractor
        from .extractors.nytimes import NytimesExtractor
        from .extractors.reddit import RedditExtractor
        from .extractors.substack import SubstackExtractor
        from .extractors.threads import ThreadsExtractor
        from .extractors.twitter import TwitterExtractor
        from .extractors.wikipedia import WikipediaExtractor
        from .extractors.x_article import XArticleExtractor
        from .extractors.x_oembed import XOembedExtractor
        from .extractors.youtube import YoutubeExtractor

        cls._mappings = []

        cls.register(
            ExtractorMapping(
                patterns=["x.com", "twitter.com"],
                extractor_cls=XArticleExtractor,
            )
        )

        cls.register(
            ExtractorMapping(
                patterns=["twitter.com", re.compile(r"/x\.com/.*")],
                extractor_cls=TwitterExtractor,
            )
        )

        cls.register(
            ExtractorMapping(
                patterns=["x.com", "twitter.com"],
                extractor_cls=XOembedExtractor,
            )
        )

        cls.register(
            ExtractorMapping(
                patterns=[
                    "reddit.com",
                    "old.reddit.com",
                    "new.reddit.com",
                    re.compile(r"^https://[^/]+\.reddit\.com"),
                ],
                extractor_cls=RedditExtractor,
            )
        )

        cls.register(
            ExtractorMapping(
                patterns=[
                    "youtube.com",
                    "youtu.be",
                    re.compile(r"youtube\.com/watch\?v=.*"),
                    re.compile(r"youtu\.be/.*"),
                ],
                extractor_cls=YoutubeExtractor,
            )
        )

        cls.register(
            ExtractorMapping(
                patterns=["news.ycombinator.com"],
                extractor_cls=HackerNewsExtractor,
            )
        )

        cls.register(
            ExtractorMapping(
                patterns=[re.compile(r"^https?://chatgpt\.com/(c|share)/.*")],
                extractor_cls=ChatGPTExtractor,
            )
        )

        cls.register(
            ExtractorMapping(
                patterns=[
                    "claude.ai",
                    re.compile(r"^https?://claude\.ai/(chat|share)/.*"),
                ],
                extractor_cls=ClaudeExtractor,
            )
        )

        cls.register(
            ExtractorMapping(
                patterns=[re.compile(r"^https?://grok\.com/(chat|share)(/.*)?$")],
                extractor_cls=GrokExtractor,
            )
        )

        cls.register(
            ExtractorMapping(
                patterns=[re.compile(r"^https?://gemini\.google\.com/app/.*")],
                extractor_cls=GeminiExtractor,
            )
        )

        cls.register(
            ExtractorMapping(
                patterns=[
                    "github.com",
                    re.compile(r"^https?://github\.com/.*"),
                ],
                extractor_cls=GitHubExtractor,
            )
        )

        cls.register(
            ExtractorMapping(
                patterns=["linkedin.com"],
                extractor_cls=LinkedInExtractor,
            )
        )

        cls.register(
            ExtractorMapping(
                patterns=["threads.net", "www.threads.com", "threads.com"],
                extractor_cls=ThreadsExtractor,
            )
        )

        cls.register(
            ExtractorMapping(
                patterns=["bsky.app"],
                extractor_cls=BlueskyExtractor,
            )
        )

        cls.register(
            ExtractorMapping(
                patterns=["medium.com", re.compile(r"\.medium\.com")],
                extractor_cls=MediumExtractor,
            )
        )

        cls.register(
            ExtractorMapping(
                patterns=["wiki.c2.com"],
                extractor_cls=C2WikiExtractor,
            )
        )

        cls.register(
            ExtractorMapping(
                patterns=[
                    re.compile(r"^https?://substack\.com/@[^/]+/note/.+"),
                    re.compile(r"^https?://substack\.com/home/post/p-\d+"),
                    "substack.com",
                ],
                extractor_cls=SubstackExtractor,
            )
        )

        cls.register(
            ExtractorMapping(
                patterns=["nytimes.com"],
                extractor_cls=NytimesExtractor,
            )
        )

        cls.register(
            ExtractorMapping(
                patterns=["wikipedia.org"],
                extractor_cls=WikipediaExtractor,
            )
        )

        cls.register(
            ExtractorMapping(
                patterns=[re.compile(r"/@[^/]+/\d+")],
                extractor_cls=MastodonExtractor,
            )
        )

        cls.register(
            ExtractorMapping(
                patterns=[re.compile(r"/t/[^/]+/\d+")],
                extractor_cls=DiscourseExtractor,
            )
        )

        cls.register(
            ExtractorMapping(
                patterns=["leetcode.com"],
                extractor_cls=LeetCodeExtractor,
            )
        )

        cls.register(
            ExtractorMapping(
                patterns=["lwn.net"],
                extractor_cls=LwnExtractor,
            )
        )

        cls.register(
            ExtractorMapping(
                patterns=[re.compile(r".*")],
                extractor_cls=BbcodeDataExtractor,
            )
        )

    @classmethod
    def register(cls, mapping: ExtractorMapping) -> None:
        cls._mappings.append(mapping)

    @classmethod
    def find_extractor(
        cls,
        document: Tag,
        url: str,
        schema_org_data: Any = None,
        options: Optional[ExtractorOptions] = None,
    ) -> Optional[BaseExtractor]:
        cls._ensure_initialized()
        return cls._find_by_predicate(document, url, schema_org_data, lambda e: e.can_extract(), options)

    @classmethod
    def find_async_extractor(
        cls,
        document: Tag,
        url: str,
        schema_org_data: Any = None,
        options: Optional[ExtractorOptions] = None,
    ) -> Optional[BaseExtractor]:
        cls._ensure_initialized()
        return cls._find_by_predicate(document, url, schema_org_data, lambda e: e.can_extract_async(), options)

    @classmethod
    def find_preferred_async_extractor(
        cls,
        document: Tag,
        url: str,
        schema_org_data: Any = None,
        options: Optional[ExtractorOptions] = None,
    ) -> Optional[BaseExtractor]:
        cls._ensure_initialized()
        return cls._find_by_predicate(
            document,
            url,
            schema_org_data,
            lambda e: e.can_extract_async() and e.prefers_async(),
            options,
        )

    @classmethod
    def _find_by_predicate(
        cls,
        document: Tag,
        url: str,
        schema_org_data: Any,
        predicate: Callable[[BaseExtractor], bool],
        options: Optional[ExtractorOptions] = None,
    ) -> Optional[BaseExtractor]:
        try:
            domain = urlparse(url).hostname or ""

            for mapping in cls._mappings:
                matches = any(
                    pattern.search(url) if isinstance(pattern, re.Pattern) else domain.__contains__(pattern)
                    for pattern in mapping.patterns
                )

                if matches:
                    instance = mapping.extractor_cls(document, url, schema_org_data, options)
                    if predicate(instance):
                        return instance

            return None
        except Exception:
            return None
