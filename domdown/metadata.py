from __future__ import annotations

from bs4 import BeautifulSoup, Tag

from .text_utils import normalize_inline_text
from .types import DomdownOptions, HtmlMetadata


def extract_metadata(soup: BeautifulSoup, options: DomdownOptions) -> HtmlMetadata:
    html_tag = soup.find("html")
    title = _first_text(
        _meta_content(soup, "meta[property='og:title']"),
        _meta_content(soup, "meta[name='twitter:title']"),
        _meta_content(soup, "meta[property='twitter:title']"),
        _tag_text(soup.select_one("h1.story-title")),
        _tag_text(soup.title),
    )
    source = _first_text(
        _meta_content(soup, "link[rel='canonical']"),
        _meta_content(soup, "meta[property='og:url']"),
        options.base_url,
    )
    author = _first_list(
        _meta_content(soup, "meta[name='author']"),
        _meta_content(soup, "meta[property='article:author']"),
        _select_texts(soup, ".postmeta .p-author .author"),
        _select_texts(soup, ".postmeta .author"),
    )
    author = tuple(item for item in author if item and not _looks_like_date(item))
    published = _first_text(
        _meta_content(soup, "meta[itemprop='datePublished']"),
        _meta_content(soup, "meta[property='article:published_time']"),
        _meta_content(soup, "meta[name='date']"),
    )
    description = _first_text(
        _meta_content(soup, "meta[name='description']"),
        _meta_content(soup, "meta[property='og:description']"),
    )
    categories = _select_texts(soup, ".p-tags")
    tags = _split_tags(categories) if categories else ()
    if options.frontmatter_tags:
        tags = options.frontmatter_tags
    language = html_tag.get("lang") if html_tag and html_tag.get("lang") else None
    canonical_url = _first_text(
        _meta_content(soup, "link[rel='canonical']"),
        _meta_content(soup, "meta[property='og:url']"),
    )
    image = _first_text(
        _meta_content(soup, "meta[property='og:image']"),
        _first_image_src(soup),
    )
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


def _meta_content(soup: BeautifulSoup, selector: str) -> str | None:
    tag = soup.select_one(selector)
    if not isinstance(tag, Tag):
        return None
    if tag.name == "link":
        return tag.get("href")
    return tag.get("content")


def _tag_text(tag: Tag | None) -> str | None:
    if not isinstance(tag, Tag):
        return None
    return normalize_inline_text(tag.get_text(" ", strip=True))


def _select_texts(soup: BeautifulSoup, selector: str) -> tuple[str, ...]:
    values = []
    for tag in soup.select(selector):
        if isinstance(tag, Tag):
            value = normalize_inline_text(tag.get_text(" ", strip=True))
            if value:
                values.append(value)
    return tuple(values)


def _first_text(*values: object) -> str:
    for value in values:
        if isinstance(value, tuple):
            if value:
                return value[0]
        elif isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _first_list(*values: object) -> tuple[str, ...]:
    for value in values:
        if isinstance(value, tuple) and value:
            return value
        if isinstance(value, str) and value.strip():
            return (value.strip(),)
    return ()


def _split_tags(values: tuple[str, ...]) -> tuple[str, ...]:
    tags: list[str] = []
    for value in values:
        for part in value.replace(",", "/").split("/"):
            part = part.strip()
            if part:
                tags.append(part)
    return tuple(tags)


def _looks_like_date(value: str) -> bool:
    return bool(__import__("re").match(r"^\w{3}\s+\d{1,2},\s+\d{4}$", value))


def _first_image_src(soup: BeautifulSoup) -> str | None:
    img = soup.find("img")
    if not isinstance(img, Tag):
        return None
    src = img.get("data-src") or img.get("data-original") or img.get("src")
    return src or None

