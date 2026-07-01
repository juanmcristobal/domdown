from __future__ import annotations

from .domain import DomainAdapterSpec, make_domain_adapter

GBHACKERS_SPEC = DomainAdapterSpec(
    name="gbhackers",
    site_names=("GBHackers Security | #1 Globally Trusted Cyber Security News Platform",),
    host_exact=("gbhackers.com",),
    host_suffixes=(".gbhackers.com",),
    remove_selectors=(
        ".td-post-sharing",
        ".tdb-author-box",
        ".tdb_single_reading_time",
        ".tdb_single_author",
        ".tdb_single_categories",
        ".tdb-post-meta",
        ".td_module_wrap",
        ".td-related-title",
        ".td-next-prev-wrap",
    ),
    trim_before_first_heading=True,
    trailing_noise_prefixes=("Follow us on", "**Follow us on"),
    trailing_noise_patterns=(r"^Follow us on\b",),
)

GBHackersAdapter = make_domain_adapter(GBHACKERS_SPEC)
