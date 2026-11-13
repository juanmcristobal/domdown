from __future__ import annotations

from urllib.parse import parse_qs, urlsplit

from bs4 import Tag

from .._core import PipelineContext
from .domain import DeclarativeDomainAdapter, DomainAdapterSpec

BLEEPINGCOMPUTER_SPEC = DomainAdapterSpec(
    name="bleepingcomputer",
    site_names=("BleepingComputer",),
    host_exact=("bleepingcomputer.com",),
    host_suffixes=(".bleepingcomputer.com",),
    remove_selectors=(
        ".bc_wrapper > header",
        ".bc_right_sidebar",
        "#pop_stories",
        "#nfeatured",
        "#comment_form",
        ".cz-newz-comment-wrapp",
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


class BleepingComputerAdapter(DeclarativeDomainAdapter):
    """Remove BleepingComputer chrome and specifically identified Wiz ads."""

    def __init__(self) -> None:
        super().__init__(spec=BLEEPINGCOMPUTER_SPEC)

    def preprocess(self, context: PipelineContext) -> PipelineContext:
        """Remove source modules and image-linked Wiz campaign banners."""

        context = super().preprocess(context)
        document = context.document
        if document is None:
            return context
        for anchor in list(document.select("a[href]")):
            if not isinstance(anchor, Tag) or not _is_wiz_campaign_banner(anchor):
                continue
            parent = anchor.parent
            anchor.decompose()
            while isinstance(parent, Tag) and parent is not document:
                if parent.name not in {"div", "span"} or parent.get_text(" ", strip=True):
                    break
                if parent.select("a, img, picture, video, iframe, pre, code, table"):
                    break
                next_parent = parent.parent
                parent.decompose()
                parent = next_parent
        return context


def _is_wiz_campaign_banner(anchor: Tag) -> bool:
    """Match only image banners linked to BleepingComputer-specific Wiz campaigns."""

    try:
        landing = urlsplit(str(anchor.get("href", "")))
    except ValueError:
        return False
    if _normalized_host(landing.hostname) != "wiz.io" or not landing.path.startswith("/lp/"):
        return False
    campaign = parse_qs(landing.query)
    if "bleepingcomputer" not in campaign.get("utm_source", [""])[0].lower():
        return False
    if "display" not in campaign.get("utm_medium", [""])[0].lower():
        return False
    for image in anchor.find_all("img", src=True):
        try:
            source = urlsplit(str(image.get("src", "")))
        except ValueError:
            continue
        if _normalized_host(source.hostname) == "bleepstatic.com" and source.path.startswith("/c/w/"):
            return True
    return False


def _normalized_host(host: str | None) -> str:
    """Normalize the optional www prefix for strict host comparisons."""

    value = (host or "").lower()
    return value[4:] if value.startswith("www.") else value
