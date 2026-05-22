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
DEFAULT_REMOVE_SELECTORS = (
    ".float-share",
    ".mobile-share",
    ".post-head",
    ".sharebelow",
    ".schema_org",
    ".tags",
    ".story-title",
    ".postmeta",
)
