from __future__ import annotations

from bs4 import BeautifulSoup

from .._core.metadata import HtmlMetadata
from .._core.options import DomdownOptions
from .helpers import (
    first_image_src,
    first_list,
    first_text,
    looks_like_date,
    meta_content,
    select_texts,
    split_tags,
    tag_text,
)
from .selectors import (
    AUTHOR_SELECTORS,
    DESCRIPTION_SELECTORS,
    IMAGE_SELECTORS,
    PUBLISHED_SELECTORS,
    SOURCE_SELECTORS,
    TAG_SELECTORS,
    TITLE_SELECTORS,
)


def extract_metadata(soup: BeautifulSoup, options: DomdownOptions) -> HtmlMetadata:
    html_tag = soup.find("html")
    title = first_text(
        *(meta_content(soup, selector) for selector in TITLE_SELECTORS),
        tag_text(soup.select_one("h1.story-title")),
        tag_text(soup.title),
    )
    source = first_text(*(meta_content(soup, selector) for selector in SOURCE_SELECTORS), options.base_url)
    author = first_list(
        *(meta_content(soup, selector) for selector in AUTHOR_SELECTORS),
        *select_texts(soup, ".postmeta .p-author .author"),
        *select_texts(soup, ".postmeta .author"),
    )
    author = tuple(item for item in author if item and not looks_like_date(item))
    published = first_text(*(meta_content(soup, selector) for selector in PUBLISHED_SELECTORS))
    description = first_text(*(meta_content(soup, selector) for selector in DESCRIPTION_SELECTORS))
    categories = select_texts(soup, TAG_SELECTORS[0])
    tags = split_tags(categories) if categories else ()
    if options.frontmatter_tags:
        tags = options.frontmatter_tags
    language = html_tag.get("lang") if html_tag and html_tag.get("lang") else None
    canonical_url = first_text(*(meta_content(soup, selector) for selector in SOURCE_SELECTORS))
    image = first_text(*(meta_content(soup, selector) for selector in IMAGE_SELECTORS), first_image_src(soup))
    return HtmlMetadata(
        title=title or None,
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
