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
CONTENT_SELECTORS = (
    ".articlebody",
    ".post-body",
    ".entry-content",
    ".content",
    ".content-body",
    ".post-content",
    ".post__body",
    ".s-blog-post__body",
    "[class*='content']",
    "[id*='content']",
    "[class*='body']",
    "[id*='body']",
    "[class*='article']",
    "[id*='article']",
    "[class*='post']",
    "[id*='post']",
    "[class*='entry']",
    "[id*='entry']",
)

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
