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

# Selectors for visible author metadata.
AUTHOR_VISIBLE_SELECTORS = (
    ".postmeta .p-author .author",
    ".postmeta .author",
    ".postmeta a[href*='/author']",
    ".postmeta a[href*='/authors']",
    ".p-author .author",
    ".p-author a",
    ".byline .author",
    ".byline a",
    "[rel='author']",
)

# Selectors for metadata-backed author fields.
AUTHOR_META_SELECTORS = (
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

# Selectors for visible tag/category metadata.
TAG_VISIBLE_SELECTORS = (
    ".p-tags",
    ".single-tags",
    ".post-tags",
    ".tags",
    ".tag-list",
    ".taglist",
    ".category-tags",
    ".categories",
    "[rel='tag']",
)

# Selectors for metadata-backed tag/category fields.
TAG_META_SELECTORS = (
    "meta[property='article:tag']",
    "meta[name='keywords']",
    "meta[name='news_keywords']",
)
