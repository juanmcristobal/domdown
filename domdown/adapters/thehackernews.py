from __future__ import annotations

from .domain import DomainAdapterSpec, make_domain_adapter

THEHACKERNEWS_SPEC = DomainAdapterSpec(
    name="thehackernews",
    site_names=("The Hacker News",),
    host_exact=("thehackernews.com",),
    host_suffixes=(".thehackernews.com",),
    remove_selectors=(
        ".rightbx",
        ".side_res",
        ".PopularPosts",
        ".sidebar",
        "#sidebar",
    ),
    trailing_noise_prefixes=(
        "⭐ Featured Resources",
        "⚡ Top Stories",
    ),
)

TheHackerNewsAdapter = make_domain_adapter(THEHACKERNEWS_SPEC)
