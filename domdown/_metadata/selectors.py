from __future__ import annotations

# Selectors for article title metadata.
TITLE_SELECTORS = (
    "meta[property='og:title']",
    "meta[name='twitter:title']",
    "meta[property='twitter:title']",
)

# Selectors for canonical or source URL metadata.
SOURCE_SELECTORS = (
    "link[rel='canonical']",
    "meta[property='og:url']",
)

# Selectors for author metadata.
AUTHOR_SELECTORS = (
    "meta[name='author']",
    "meta[property='article:author']",
)

# Selectors for publication date metadata.
PUBLISHED_SELECTORS = (
    "meta[itemprop='datePublished']",
    "meta[property='article:published_time']",
    "meta[name='date']",
)

# Selectors for description metadata.
DESCRIPTION_SELECTORS = (
    "meta[name='description']",
    "meta[property='og:description']",
)

# Selectors for preview image metadata.
IMAGE_SELECTORS = (
    "meta[property='og:image']",
)

# Selectors for tag/category metadata.
TAG_SELECTORS = (
    ".p-tags",
)
