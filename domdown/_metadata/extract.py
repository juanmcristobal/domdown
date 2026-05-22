from __future__ import annotations

from bs4 import BeautifulSoup

from .._core.metadata import HtmlMetadata
from .._core.options import DomdownOptions
from .helpers import (
    collect_texts,
    collect_meta_contents,
    first_image_src,
    first_list,
    first_text,
    looks_like_date,
    looks_like_url,
    meta_content,
    normalize_source,
    normalize_title,
    split_tags,
    tag_text,
)
from .selectors import (
    AUTHOR_META_SELECTORS,
    AUTHOR_VISIBLE_SELECTORS,
    DESCRIPTION_SELECTORS,
    IMAGE_SELECTORS,
    PUBLISHED_SELECTORS,
    SOURCE_SELECTORS,
    SITE_NAME_SELECTORS,
    TAG_META_SELECTORS,
    TAG_VISIBLE_SELECTORS,
    TITLE_SELECTORS,
)


def extract_tags(soup: BeautifulSoup) -> tuple[str, ...]:
    """Extract article tags from visible tags or metadata selectors."""

    visible_tags = split_tags(collect_texts(soup, TAG_VISIBLE_SELECTORS))
    if visible_tags:
        return visible_tags
    return split_tags(collect_meta_contents(soup, TAG_META_SELECTORS))


def extract_metadata(soup: BeautifulSoup, options: DomdownOptions) -> HtmlMetadata:
    """Extract normalized article metadata from parsed HTML."""

    html_tag = soup.find("html")
    site_name = first_text(*(meta_content(soup, selector) for selector in SITE_NAME_SELECTORS))
    title = normalize_title(
        first_text(
            *(meta_content(soup, selector) for selector in TITLE_SELECTORS),
            tag_text(soup.select_one("h1.story-title")),
            tag_text(soup.title),
        ),
        site_name,
    )
    source = normalize_source(first_text(*(meta_content(soup, selector) for selector in SOURCE_SELECTORS)), options.base_url)
    visible_author = collect_texts(soup, AUTHOR_VISIBLE_SELECTORS)
    meta_author = tuple(
        value
        for value in (meta_content(soup, selector) for selector in AUTHOR_META_SELECTORS)
        if value
    )
    author_sources = (meta_author, visible_author) if options.author_priority == "metadata" else (visible_author, meta_author)
    author = first_list(*author_sources)
    author = tuple(item for item in author if item and not looks_like_date(item) and not looks_like_url(item))
    published = first_text(*(meta_content(soup, selector) for selector in PUBLISHED_SELECTORS))
    description = first_text(*(meta_content(soup, selector) for selector in DESCRIPTION_SELECTORS))
    tags = options.frontmatter_tags
    language = html_tag.get("lang") if html_tag and html_tag.get("lang") else None
    canonical_url = normalize_source(first_text(*(meta_content(soup, selector) for selector in SOURCE_SELECTORS)), options.base_url)
    image = first_text(*(meta_content(soup, selector) for selector in IMAGE_SELECTORS), first_image_src(soup))
    return HtmlMetadata(
        title=title or None,
        site_name=site_name or None,
        source=source or None,
        author=author,
        published=published or None,
        created=options.created,
        description=description or None,
        tags=tags,
        language=language,
        canonical_url=canonical_url or None,
        image=image or None,
    )
