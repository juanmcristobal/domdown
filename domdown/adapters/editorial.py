from __future__ import annotations

from .domain import DomainAdapterSpec, make_domain_adapter


THE_REGISTER_SPEC = DomainAdapterSpec(
    name="the-register",
    host_exact=("theregister.com",),
    post_clean_selectors=(".toplist",),
)
TheRegisterAdapter = make_domain_adapter(THE_REGISTER_SPEC)

SECURITYWEEK_SPEC = DomainAdapterSpec(
    name="securityweek",
    host_exact=("securityweek.com",),
    remove_selectors=(
        ".widget_sw_widget_moves",
        ".widget_sw_widget_industryexperts",
        ".zox-post-cat-link",
        ".zox-search-cont",
    ),
)
SecurityWeekAdapter = make_domain_adapter(SECURITYWEEK_SPEC)

SECURITY_AFFAIRS_SPEC = DomainAdapterSpec(
    name="security-affairs",
    host_exact=("securityaffairs.com",),
    remove_selectors=(".right-sidebar",),
)
SecurityAffairsAdapter = make_domain_adapter(SECURITY_AFFAIRS_SPEC)

CYBERSCOOP_SPEC = DomainAdapterSpec(
    name="cyberscoop",
    host_exact=("cyberscoop.com",),
    remove_selectors=(".popular-stories", ".latest-podcasts", ".top-categories", ".stickybar", ".ad__inner"),
)
CyberScoopEditorialAdapter = make_domain_adapter(CYBERSCOOP_SPEC)

CENSYS_SPEC = DomainAdapterSpec(
    name="censys",
    host_exact=("censys.com",),
    remove_selectors=("#header",),
)
CensysAdapter = make_domain_adapter(CENSYS_SPEC)

WIZ_SPEC = DomainAdapterSpec(
    name="wiz",
    host_exact=("wiz.io",),
    trailing_noise_lines=("## Continue reading", "## Ready to see Wiz in action?"),
)
WizAdapter = make_domain_adapter(WIZ_SPEC)

RAILWAY_SPEC = DomainAdapterSpec(
    name="railway",
    host_suffixes=(".railway.com",),
    trailing_noise_lines=("### Continue Reading...",),
)
RailwayAdapter = make_domain_adapter(RAILWAY_SPEC)
