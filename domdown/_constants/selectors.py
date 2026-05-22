from __future__ import annotations

# Tags that should be dropped entirely during cleanup and rendering.
SKIP_TAGS = {
    "aside",
    "button",
    "form",
    "iframe",
    "input",
    "link",
    "meta",
    "noscript",
    "script",
    "select",
    "style",
    "svg",
    "textarea",
}

# Selectors that are typically noise in article-like pages.
SHARE_SELECTORS = (
    ".share-widget",
    ".heateor_sss_sharing_container",
    ".heateor_sss_more",
    ".more-link",
    "[class*='share']",
    "[id*='share']",
    "[class*='social']",
    "[id*='social']",
)

DEFAULT_REMOVE_SELECTORS = (
    ".float-share",
    ".mobile-share",
    ".post-head",
    ".sharebelow",
    ".schema_org",
    ".tags",
    ".story-title",
    ".postmeta",
    "[class*='follow']",
    "[class*='sponsored']",
    "[rel*='sponsored']",
    "[class*='note-b']",
    "[class*='dog_two']",
) + SHARE_SELECTORS

# Selectors that usually point at the content subtree inside a larger page shell.
# Exact selectors are preferred first because substring selectors can match chrome.
CONTENT_SELECTORS_EXACT = (
    ".articlebody",
    ".post-body",
    ".entry-content",
    ".content",
    "#content",
    ".content-body",
    ".post-content",
    ".post__body",
    ".post__content",
    ".s-blog-post__body",
    ".BodyText__content",
    ".hb-content__text",
    ".story-body",
    ".story-shell",
)

# Broad selectors are only used as a fallback when exact selectors do not find
# a confident content subtree.
CONTENT_SELECTORS_FALLBACK = (
    "[class*='body']",
    "[id*='body']",
    "[class*='entry']",
    "[id*='entry']",
)

CONTENT_SELECTORS = CONTENT_SELECTORS_EXACT + CONTENT_SELECTORS_FALLBACK

# Class or id markers that usually indicate page chrome, ads, or engagement widgets.
NOISE_MARKERS = (
    "share",
    "social",
    "breadcrumb",
    "related",
    "recommend",
    "newsletter",
    "subscribe",
    "promo",
    "debug",
    "cta",
    "widget",
    "sidebar",
    "nav",
    "footer",
    "tags",
    "postmeta",
    "story-title",
    "post-head",
    "navigation",
    "cookie",
    "consent",
    "popup",
    "modal",
    "advert",
    "sponsor",
    "follow",
    "sponsored",
    "note-b",
    "dog_two",
)

# Structural chrome markers for top-of-article wrappers that repeat metadata.
HEADER_MARKERS = (
    "hero",
    "meta",
    "byline",
    "author",
    "date",
    "time",
    "intro",
    "teaser",
    "kicker",
    "standfirst",
    "deck",
)

# Phrases commonly used to label related-link blocks.
RELATED_PHRASES = (
    "related categories",
    "related topics",
    "related articles",
    "related posts",
    "recommended",
    "you may also like",
    "more from",
)
