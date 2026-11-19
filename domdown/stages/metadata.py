"""Stage interface for metadata extraction."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, replace

from bs4 import BeautifulSoup, Tag

from .._core import PipelineContext
from .._core.selectors import normalize_selector
from .._metadata import extract_metadata
from .._metadata.helpers import first_image_src, normalize_source


@dataclass(slots=True)
class MetadataStage:
    """Extract normalized article metadata from the parsed document."""

    name: str = "metadata"

    def run(self, context: PipelineContext) -> PipelineContext:
        if context.document is None:
            return context
        context.metadata = extract_metadata(context.document, context.options)
        if context.site_criteria_scope and context.metadata is not None and context.metadata.image:
            base_url = context.options.base_url or context.metadata.canonical_url
            image = normalize_source(context.metadata.image, base_url)
            if image != context.metadata.image:
                context.metadata = replace(context.metadata, image=image)
        criteria = context.extraction_criteria
        if (
            context.site_criteria_scope
            and criteria is not None
            and context.document.select_one("meta[property='og:image']") is None
        ):
            content_view = _criteria_content_view(context.document, criteria.include, criteria.exclude)
            base_url = context.options.base_url or context.metadata.canonical_url
            image = normalize_source(first_image_src(content_view), base_url)
            if image and context.metadata is not None:
                context.metadata = replace(context.metadata, image=image)
        return context


def _criteria_content_view(document: Tag, include: tuple[str, ...], exclude: tuple[str, ...]) -> Tag:
    """Build a selector-scoped metadata view without mutating the source DOM."""

    view = BeautifulSoup("<div></div>", "lxml")
    root = view.div
    for selector in include:
        for node in document.select(normalize_selector(selector)):
            root.append(deepcopy(node))
    for selector in exclude:
        for node in list(root.select(normalize_selector(selector))):
            node.decompose()
    return root
