from __future__ import annotations

from .domain import DomainAdapterSpec, make_domain_adapter

WIKIPEDIA_SPEC = DomainAdapterSpec(
    name="wikipedia",
    site_names=("Wikipedia",),
    host_suffixes=(".wikipedia.org",),
    remove_selectors=(
        "header",
        "nav",
        "footer",
        "aside",
        "#siteSub",
        "#contentSub",
        ".shortdescription",
        ".hatnote",
        ".mw-editsection",
        ".mw-jump-link",
        ".infobox",
        ".navbox",
        ".mw-references-wrap",
        ".reflist",
        ".catlinks",
        ".printfooter",
    ),
)

WikipediaAdapter = make_domain_adapter(WIKIPEDIA_SPEC)
