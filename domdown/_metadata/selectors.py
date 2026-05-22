from __future__ import annotations

TITLE_SELECTORS = (
    "meta[property='og:title']",
    "meta[name='twitter:title']",
    "meta[property='twitter:title']",
)

SOURCE_SELECTORS = (
    "link[rel='canonical']",
    "meta[property='og:url']",
)

AUTHOR_SELECTORS = (
    "meta[name='author']",
    "meta[property='article:author']",
)

PUBLISHED_SELECTORS = (
    "meta[itemprop='datePublished']",
    "meta[property='article:published_time']",
    "meta[name='date']",
)

DESCRIPTION_SELECTORS = (
    "meta[name='description']",
    "meta[property='og:description']",
)

IMAGE_SELECTORS = (
    "meta[property='og:image']",
)

TAG_SELECTORS = (
    ".p-tags",
)
