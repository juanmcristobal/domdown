from __future__ import annotations

from .domain import DomainAdapterSpec, make_domain_adapter

BLEEPINGCOMPUTER_SPEC = DomainAdapterSpec(
    name="bleepingcomputer",
    site_names=("BleepingComputer",),
    host_exact=("bleepingcomputer.com",),
    host_suffixes=(".bleepingcomputer.com",),
    remove_selectors=(
        ".bc_right_sidebar",
        "#pop_stories",
        "#nfeatured",
        "#comment_form",
        ".article-callout",
        ".cz-related-article-wrapp",
    ),
    trailing_noise_prefixes=(
        "##### Post a Comment",
        "###### You need to login",
        "###### Comments have been disabled",
        "Not a member yet?",
        "Popular Stories",
        "Sponsor Posts",
        "Upcoming Webinar",
    ),
)

BleepingComputerAdapter = make_domain_adapter(BLEEPINGCOMPUTER_SPEC)
