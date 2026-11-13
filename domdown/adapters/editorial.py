from __future__ import annotations

from bs4 import Tag

from .._core import PipelineContext
from .domain import DeclarativeDomainAdapter, DomainAdapterSpec, make_domain_adapter


THE_REGISTER_SPEC = DomainAdapterSpec(
    name="the-register",
    host_exact=("theregister.com",),
    post_clean_selectors=(".toplist", "section.related", ".google-ad"),
)
TheRegisterAdapter = make_domain_adapter(THE_REGISTER_SPEC)

DARK_READING_SPEC = DomainAdapterSpec(
    name="dark-reading",
    host_exact=("darkreading.com",),
    post_clean_selectors=(".ArticleBase-ContributorsWrapper", ".ArticleBase-More"),
)
DarkReadingAdapter = make_domain_adapter(DARK_READING_SPEC)

SECURITYWEEK_SPEC = DomainAdapterSpec(
    name="securityweek",
    host_exact=("securityweek.com",),
    remove_selectors=(
        ".widget_sw_widget_moves",
        ".widget_sw_widget_industryexperts",
        ".zox-post-cat-link",
        ".zox-search-cont",
    ),
    post_clean_selectors=(".zox-post-ad-wrap",),
)
SecurityWeekAdapter = make_domain_adapter(SECURITYWEEK_SPEC)

SECURITY_AFFAIRS_SPEC = DomainAdapterSpec(
    name="security-affairs",
    host_exact=("securityaffairs.com",),
    remove_selectors=(".right-sidebar",),
)


class SecurityAffairsAdapter(DeclarativeDomainAdapter):
    """Remove the source's social follow footer while retaining author details."""

    def __init__(self) -> None:
        super().__init__(spec=SECURITY_AFFAIRS_SPEC)

    def post_clean(self, context: PipelineContext) -> PipelineContext:
        """Drop only the paragraph that promotes the Security Affairs social accounts."""

        context = super().post_clean(context)
        document = context.document
        if document is None:
            return context
        for paragraph in list(document.find_all("p")):
            text = " ".join(paragraph.stripped_strings).casefold()
            if text.startswith("follow me on twitter:"):
                paragraph.decompose()
        if context.document is not None:
            context.cleaned_html = str(context.document)
        return context


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
