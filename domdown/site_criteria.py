"""Portable CSS extraction rules for sites verified against real fixtures.

Each registry value contains ``include``, ``exclude`` and ``unwrap`` plus the
optional ``drop_text`` regex filters supported by ``ExtractionCriteria``.
Host patterns stay separate so the rule data remains criteria-only.
"""

from __future__ import annotations

import re
from urllib.parse import urlsplit

from bs4 import Tag

from ._core import ExtractionCriteria

_SITE_RULES_BY_HOST: dict[str, dict[str, list[str]]] = {
    r"(?:[a-z0-9-]+\.)*wikipedia\.org": {
        "include": ["#mw-content-text"],
        "exclude": [
            "header",
            "nav",
            "footer",
            "aside",
            "#siteSub",
            "#contentSub",
            ".shortdescription",
            ".hatnote",
            ".mw-editsection",
            ".mw-jump-link",
            ".infobox",
            ".navbox",
            ".mw-references-wrap",
            ".reflist",
            ".catlinks",
            ".printfooter",
        ],
        "unwrap": [],
    },
    r"(?:www\.)?theregister\.com": {
        "include": ["main"],
        "exclude": [
            ".toplist",
            "section.related",
            ".google-ad",
            "a.lab-article-section-link",
            "p.kicker:has(a[href*='/tag/'])",
        ],
        "unwrap": [],
        "drop_text": [r"placeholder\(#1\)"],
    },
    r"(?:www\.)?cyberscoop\.com": {
        "include": ["div.single-article__container.js-single-article-content"],
        "exclude": [
            "ul.single-article__eyebrow",
            "div.single-article__excerpt",
            "div.single-article__meta",
            "footer.single-article__footer",
            "[class*='share']",
        ],
        "unwrap": [],
    },
    r"(?:www\.)?darkreading\.com": {
        "include": ["h1", "div.TwoColumnLayout-Body"],
        "exclude": [
            ".ArticleBase-Contributors",
            ".ArticleBase-ContributorsWrapper",
            ".ArticleBase-More",
            ".EventsPromotions",
            ".RelatedArticle",
            ".Resources",
        ],
        "unwrap": [],
    },
    r"(?:www\.)?securityweek\.com": {
        "include": ["h1", "div.zox-post-body"],
        "exclude": [
            ".zox-post-ad-wrap",
            'p:-soup-contains("Related:")',
            ':is(h2, h3, h4, h5, h6):-soup-contains("Trending"), '
            ':is(h2, h3, h4, h5, h6):-soup-contains("Trending") ~ *',
        ],
        "unwrap": [],
    },
    r"(?:www\.)?securityaffairs\.com": {
        "include": [".article-details-block"],
        "exclude": [
            "div.cta-tags",
            "div.post-time",
            "[class*='share']",
            "p:has(a[href*='twitter.com/securityaffairs'])",
            "p:has(a[href*='linkedin.com/pub/pierluigi'])",
            "p:has(a[href*='securityaffairs.co/wordpress'])",
        ],
        "unwrap": [],
    },
    r"(?:www\.)?wiz\.io": {
        "include": ["h1", "div.prose"],
        "exclude": ["a.ease-spring-button"],
        "unwrap": [],
    },
    r"(?:[a-z0-9-]+\.)*railway\.com": {
        "include": ["article"],
        "exclude": ['h3:-soup-contains("Continue Reading..."), h3:-soup-contains("Continue Reading...") ~ *'],
        "unwrap": [],
    },
    r"(?:www\.)?blog\.google": {
        "include": ["article.uni-article-wrapper"],
        "exclude": [
            ".audio-player-tts",
            ".uni-article-hero__authors-actions",
            'p:has(> i:-soup-contains("Last updated"))',
        ],
        "unwrap": [],
    },
    r"(?:www\.)?gbhackers\.com": {
        "include": ["article"],
        "exclude": [
            ".td-post-sharing",
            ".tdb-author-box",
            ".tdb_single_reading_time",
            ".tdb_single_author",
            ".tdb_single_categories",
            ".tdb-post-meta",
            ".td_module_wrap",
            ".td-related-title",
            ".td-next-prev-wrap",
            'p.has-background:-soup-contains("Follow us on")',
        ],
        "unwrap": [],
    },
    r"(?:[a-z0-9-]+\.)*thehackernews\.com": {
        "include": ["main"],
        "exclude": [".rightbx", ".side_res", ".PopularPosts", ".sidebar", "#sidebar"],
        "unwrap": [],
    },
    r"(?:www\.)?cybersecuritynews\.com": {
        "include": ["article"],
        "exclude": [
            ".td_module_wrap",
            ".td_block_related_posts",
            ".td-related-title",
            ".td-post-sharing",
            ".td-post-source-tags",
            'a[href*="accounts.google.com"]',
            'a[href*="news.google.com/publications"]',
            'p:-soup-contains("Follow on LinkedIn")',
            'p:-soup-contains("Follow us on")',
        ],
        "unwrap": [],
    },
    r"(?:[a-z0-9-]+\.)*bleepingcomputer\.com": {
        "include": [".article_section", "h1", "div.articleBody", "article.articleBody"],
        "exclude": [
            "#pop_stories",
            "#nfeatured",
            "#comment_form",
            ".cz-newz-comment-wrapp",
            "div.cz-news-title-right-area",
            "div.cz-news-title-left-area",
            ".article-callout",
            "div.cz-related-article-wrapp",
            'a[href*="wiz.io/lp/"][href*="utm_source=bleepingcomputer" i][href*="utm_medium=display" i]:has(img[src*="bleepstatic.com/c/w/"])',
        ],
        "unwrap": [],
    },
    r"(?:www\.)?dailysecu\.com": {
        "include": ["#article-view"],
        "exclude": [
            ".section-name",
            ".helper-tool-group",
            ".fontsize-title",
            ".fontsize-preview",
            ".reveal-title",
            ".article-writer",
            ".box-skin",
            ".ad-template",
            ".ad-view",
        ],
        "unwrap": [],
        "drop_text": [
            r"M .+//",
            r"AD Manager \| AD\d+ //",
            r"// AD Manager \| AD\d+",
            r"글자크기 설정",
            r"가",
            r"기사의 본문 내용은 이 글자크기로 변경됩니다\.",
            r"이 기사를 공유합니다",
        ],
    },
    r"(?:www\.)?arxiv\.org": {
        "include": ["#abs"],
        "exclude": [
            "div.extra-services",
            "div#search-result-wrapper",
            "div#bottom-pager",
            "aside",
            "footer",
            "nav",
            "#mask",
            "#notification",
            ".dateline",
            ".authors",
            "#download-button-info",
            ".metatable",
        ],
        "unwrap": [],
    },
    r"(?:[a-z0-9-]+\.)*medium\.com": {
        "include": ["article"],
        "exclude": [
            "header",
            "nav",
            "footer",
            "aside",
            "article > :not(h1):has(~ h1)",
            'p:has(a[href*="source=post_page---byline--"])',
            'p:has(a[href*="source=post_page---post_author_info--"]), '
            'p:has(a[href*="source=post_page---post_author_info--"]) ~ p',
            'p:has(a[href*="source=post_page---post_publication_info--"]), '
            'p:has(a[href*="source=post_page---post_publication_info--"]) ~ p',
            'p:has(a[href*="source=post_page---user_mention--"]):-soup-contains("Author:")',
            'p:has(img):has(a[href*="medium.com/@"])',
            'p:has(a[href*="medium.com/@"]):has(+ p:-soup-contains("min read"))',
            'p:-soup-contains("**Help:**")',
            'p:has(a[href*="help.medium.com"])',
            'p:-soup-contains("**Status:**")',
            'p:-soup-contains("**About:**")',
            'p:-soup-contains("**Careers:**")',
            'p:-soup-contains("**Press:**")',
            'p:-soup-contains("**Blog:**")',
            'p:-soup-contains("**Store:**")',
            'p:-soup-contains("**Privacy:**")',
            'p:has(a[href*="policy.medium.com"])',
            'p:-soup-contains("**Rules:**")',
            'p:-soup-contains("**Terms:**")',
            'p:-soup-contains("**Text to speech:**")',
        ],
        "unwrap": [],
        "drop_text": [
            r"(?i)press enter or click to view image in full size",
            "·",
            "--",
            r"^\d+\s+min read$",
            r"^Just now$",
            r"^(?:\d+\s+)?(?:second|minute|hour|day|week|month|year)s? ago$",
            r"^[A-Z][a-z]{2,8} \d{1,2}, \d{4}$",
            r"^Access Control Vulnerabilities\s+[—-]\s+APPRENTICE$",
            r"^Lab-[A-Za-z0-9].*$",
            r"(?i)^(?:bug bounty|writeup|cybersecurity|penetration testing|web penetration testing)$",
        ],
    },
}

_SITE_NAMES_BY_HOST = {
    r"(?:[a-z0-9-]+\.)*wikipedia\.org": "wikipedia",
    r"(?:www\.)?theregister\.com": "the_register",
    r"(?:www\.)?cyberscoop\.com": "cyberscoop",
    r"(?:www\.)?darkreading\.com": "dark_reading",
    r"(?:www\.)?securityweek\.com": "securityweek",
    r"(?:www\.)?securityaffairs\.com": "security_affairs",
    r"(?:www\.)?wiz\.io": "wiz",
    r"(?:[a-z0-9-]+\.)*railway\.com": "railway",
    r"(?:www\.)?blog\.google": "google_blog",
    r"(?:www\.)?gbhackers\.com": "gbhackers",
    r"(?:[a-z0-9-]+\.)*thehackernews\.com": "the_hacker_news",
    r"(?:www\.)?cybersecuritynews\.com": "cybersecurity_news",
    r"(?:[a-z0-9-]+\.)*bleepingcomputer\.com": "bleepingcomputer",
    r"(?:www\.)?dailysecu\.com": "dailysecu",
    r"(?:www\.)?arxiv\.org": "arxiv",
    r"(?:[a-z0-9-]+\.)*medium\.com": "medium",
}

SITE_CRITERIA: dict[str, list[dict[str, object]]] = {}
for _host_pattern, _criteria in _SITE_RULES_BY_HOST.items():
    _site_name = _SITE_NAMES_BY_HOST[_host_pattern]
    _condition: dict[str, object] = {"host": _host_pattern}
    if _site_name == "medium":
        _condition = {"any_of": [{"host": _host_pattern}, {"site_name": "Medium"}]}
    SITE_CRITERIA.setdefault(_site_name, []).append({"match": _condition, **_criteria})

_GITHUB_CHROME = [
    ".Overlay",
    ".Overlay-body",
    ".Overlay-header",
    ".Overlay-headerFilter",
    ".Overlay-footer",
    ".Banner",
    ".SelectPanel-loadingPanel",
    "nav[aria-label='Global']",
    "header[role='banner']",
    "footer",
    ".Header",
    ".site-header",
    ".js-header-wrapper",
    ".UnderlineNav",
    ".file-navigation",
    ".file-header",
    ".repohead",
    ".repository-content > nav",
]
_GITHUB_SITE_RULES = [
    {
        "match": {"site_name": "GitHub", "url": r"/blob/"},
        "include": [
            "pre.domdown-raw-lines, .react-code-file-contents, "
            ".CodeBlob-module__codeBlobInner__tfjuQ, .CodeBlob-module__codeBlobWrapper__RS6In, "
            "section.BlobContent-module__blobContentSection__VOgZq, "
            ".BlobViewContent-module__blobContentWrapper__JS0W6"
        ],
        "exclude": _GITHUB_CHROME.copy(),
        "unwrap": [],
    },
    {
        "match": {"site_name": "GitHub", "url": r"/issues/"},
        "include": [".repository-content, .js-repo-pjax-container:not(:has(.repository-content))"],
        "exclude": _GITHUB_CHROME.copy(),
        "unwrap": [],
    },
    {
        "match": {"site_name": "GitHub", "url": r"/releases/tag/"},
        "include": ["div[data-pjax='true'][data-test-selector='body-content']"],
        "exclude": _GITHUB_CHROME.copy(),
        "unwrap": [],
    },
    {
        "match": {"site_name": "GitHub", "url": r"/security/advisories"},
        "include": [".repository-content, main"],
        "exclude": _GITHUB_CHROME.copy(),
        "unwrap": [],
    },
    {
        "match": {"site_name": "GitHub"},
        "include": [".repository-content, main"],
        "exclude": _GITHUB_CHROME.copy(),
        "unwrap": [],
    },
]
SITE_CRITERIA["github"] = _GITHUB_SITE_RULES
SITE_CRITERIA["huggingface_blog"] = [
    {
        "match": {"host": r"(?:www\.)?huggingface\.co", "url": r"/blog/"},
        "include": [".blog-content"],
        "exclude": [
            ".blog-content > div.mb-4",
            '.blog-content > div:has(span:-soup-contains("Published"))',
            ".blog-content > div.not-prose",
        ],
        "unwrap": [],
    }
]
SITE_CRITERIA["techcrunch_articles"] = [
    {
        "match": {"host": r"(?:www\.)?techcrunch\.com", "url": r"/\d{4}/\d{2}/\d{2}/"},
        "include": [".seamless-scroll-container"],
        "exclude": [
            ".article-hero__bottom",
            ".wp-block-tc23-author-card",
            ".wp-block-techcrunch-social-share",
            ".affiliate-disclaimer-text",
            ".seamless-scroll",
            ".wp-block-tc23-post-relevant-terms",
        ],
        "unwrap": [],
    }
]
SITE_CRITERIA["deepmind_blog"] = [
    {
        "match": {"host": r"(?:www\.)?deepmind\.google", "url": r"/blog/"},
        "include": ["main#page-content"],
        "exclude": [
            ".cover__text--eyebrow__container",
            ".cover__text--authors",
            ".cover__button-group",
            ".share-list",
        ],
        "unwrap": [],
        "drop_text": [r"Your browser does not support the video tag\."],
    }
]


def criteria_for_document(document: Tag | None) -> ExtractionCriteria | None:
    """Return the first declarative rule whose document condition matches."""

    for rules in SITE_CRITERIA.values():
        for rule in rules:
            match = rule.get("match")
            if not isinstance(match, dict) or not _matches_rule(document, match):
                continue
            return ExtractionCriteria(
                include=tuple(rule["include"]),
                exclude=tuple(rule["exclude"]),
                unwrap=tuple(rule["unwrap"]),
                drop_text=tuple(rule.get("drop_text", ())),
            )
    return None


def canonical_url_for_document(document: Tag | None) -> str | None:
    """Return an absolute canonical document URL when one is present."""

    if document is None:
        return None
    for selector in (
        "link[rel='canonical']",
        "meta[property='og:url']",
        "meta[property='twitter:url']",
    ):
        node = document.select_one(selector)
        if node is None:
            continue
        value = str(node.get("href") or node.get("content") or "").strip()
        try:
            parts = urlsplit(value)
        except ValueError:
            continue
        if parts.scheme and parts.hostname:
            return value
    return None


def _document_host(document: Tag | None) -> str:
    value = canonical_url_for_document(document)
    if value is None:
        return ""
    return (urlsplit(value).hostname or "").lower()


def _matches_rule(document: Tag | None, condition: dict[str, object]) -> bool:
    if document is None:
        return False
    any_of = condition.get("any_of")
    if isinstance(any_of, list):
        return any(isinstance(item, dict) and _matches_rule(document, item) for item in any_of)
    host_pattern = condition.get("host")
    if isinstance(host_pattern, str) and re.fullmatch(host_pattern, _document_host(document), re.IGNORECASE) is None:
        return False
    site_name = condition.get("site_name")
    if isinstance(site_name, str):
        node = document.select_one("meta[property='og:site_name'], meta[name='application-name']")
        if node is None or str(node.get("content", "")).strip().casefold() != site_name.casefold():
            return False
    url_pattern = condition.get("url")
    if isinstance(url_pattern, str) and re.search(url_pattern, _document_url(document), re.IGNORECASE) is None:
        return False
    return bool(condition)


def _document_url(document: Tag) -> str:
    absolute = canonical_url_for_document(document)
    if absolute:
        return absolute
    for selector in ("meta[property='og:url']", "meta[property='twitter:url']"):
        node = document.select_one(selector)
        if node is not None:
            value = str(node.get("content", "")).strip()
            if value:
                return value
    return ""
