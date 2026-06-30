from __future__ import annotations

from .domain import DomainAdapterSpec, make_domain_adapter

CYBERSECURITYNEWS_SPEC = DomainAdapterSpec(
    name="cybersecuritynews",
    site_names=("Cyber Security News",),
    host_exact=("cybersecuritynews.com",),
    host_suffixes=(".cybersecuritynews.com",),
    remove_selectors=(
        ".td_module_wrap",
        ".td_block_related_posts",
        ".td-related-title",
        ".td-post-sharing",
        ".td-post-source-tags",
        "a[href*='accounts.google.com']",
        "a[href*='news.google.com/publications']",
    ),
    trim_before_first_heading=True,
    leading_noise_lines=("Follow on LinkedIn",),
    leading_noise_patterns=(
        r"^\[Follow on LinkedIn\]\(https://www\.linkedin\.com/company/cyber-news-live-/\)$",
        r"^\[!\[Google Prefered\].*$",
        r"^\[!\[Google news\].*$",
    ),
    trailing_noise_patterns=(
        r"^\*{8,}Follow us on .*$",
        r"^### .+$",
    ),
)

CyberSecurityNewsAdapter = make_domain_adapter(CYBERSECURITYNEWS_SPEC)
