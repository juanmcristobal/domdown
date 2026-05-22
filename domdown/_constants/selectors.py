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

# Direct children that are still broad enough to be considered content shells
# during subtree refinement.
REFINABLE_CHILD_TAGS = (
    "article",
    "aside",
    "blockquote",
    "div",
    "figure",
    "main",
    "ol",
    "section",
    "table",
    "ul",
)

DEFAULT_REMOVE_SELECTORS = (
    ".ad-fixed__wrapper",
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
    ".markdown-body",
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

# Root selectors used to choose the most relevant content shell before cleanup.
ROOT_SELECTORS = (
    "article",
    "main",
    "[role='article']",
    "[role='main']",
    ".post-body",
    ".articlebody",
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
    ".markdown-body",
    ".story-body",
    ".story-shell",
    "[class*='body']",
    "[id*='body']",
    "[class*='entry']",
    "[id*='entry']",
    "body",
)

# Class or id markers that usually indicate page chrome, ads, or engagement widgets.
NOISE_MARKERS = (
    "announcement",
    "banner",
    "brand",
    "author",
    "bio",
    "cookie",
    "share",
    "social",
    "breadcrumb",
    "hero",
    "lead",
    "deck",
    "standfirst",
    "teaser",
    "excerpt",
    "related",
    "recommend",
    "feedback",
    "newsletter",
    "subscribe",
    "promo",
    "toolbar",
    "pagination",
    "pager",
    "toc",
    "table-of-contents",
    "debug",
    "cta",
    "widget",
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
    "logo",
    "masthead",
    "notice",
    "overlay",
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
    "latest news",
    "you may also like",
    "more from",
)

# Common boilerplate phrases that appear in documentation and feedback shells.
BOILERPLATE_PHRASES = (
    "thanks for letting us know this page needs work",
    "we're sorry we let you down",
    "help improve",
    "learn how to contribute",
    "view this page on github",
    "report a problem with this content",
    "if you've got a moment",
    "how we can make the documentation better",
    "search results",
    "no results found",
)

# Placeholder phrases used by portal-style shells that require JavaScript
# before the real body is rendered.
JS_SHELL_PHRASES = (
    "this app needs javascript to run",
    "please enable javascript in your browser and try again",
    "javascript is required",
)
