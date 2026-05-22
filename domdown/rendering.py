from __future__ import annotations

import html as html_lib
import re
from typing import Iterable
from urllib.parse import urljoin

from bs4 import BeautifulSoup, NavigableString, Tag

from .types import DomdownOptions, HtmlMetadata

BLOCK_TAGS = {
    "article",
    "blockquote",
    "div",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "li",
    "ol",
    "p",
    "section",
    "table",
    "tbody",
    "td",
    "th",
    "thead",
    "tr",
    "ul",
}

SKIP_TAGS = {
    "aside",
    "button",
    "form",
    "iframe",
    "input",
    "link",
    "meta",
    "noscript",
    "script",
    "select",
    "style",
    "svg",
    "textarea",
}

REMOVE_SELECTORS = (
    ".float-share",
    ".mobile-share",
    ".post-head",
    ".sharebelow",
    ".schema_org",
    ".tags",
    ".story-title",
    ".postmeta",
)


def parse_html(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "lxml")


def choose_root(soup: BeautifulSoup, prefer_article_body: bool = True) -> Tag:
    selectors = [".post-body", ".articlebody", "article", "main", "body"] if prefer_article_body else [
        ".articlebody",
        ".post-body",
        "article",
        "main",
        "body",
    ]
    for selector in selectors:
        root = soup.select_one(selector)
        if isinstance(root, Tag):
            return root
    return soup.body if isinstance(soup.body, Tag) else soup


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
    if not author and html_tag and html_tag.get("lang"):
        author = ()
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


def clean_root(root: Tag) -> Tag:
    for selector in REMOVE_SELECTORS:
        for node in root.select(selector):
            node.decompose()
    for node in list(root.find_all(SKIP_TAGS)):
        node.decompose()
    for img in root.find_all("img"):
        data_src = img.get("data-src") or img.get("data-original") or img.get("data-lazy-src")
        if data_src and (not img.get("src") or str(img.get("src", "")).startswith("data:")):
            img["src"] = data_src
    return root


def render_markdown(root: Tag, options: DomdownOptions) -> str:
    parts = [part for part in (_render_block(child, options) for child in root.children) if part]
    return _normalize_markdown("\n\n".join(parts))


def render_frontmatter(metadata: HtmlMetadata) -> str:
    lines = ["---"]
    scalar_fields = [
        ("title", metadata.title),
        ("source", metadata.source),
    ]
    trailing_fields = [
        ("published", metadata.published),
        ("created", metadata.created),
        ("description", metadata.description),
    ]
    for key, value in scalar_fields:
        if value:
            lines.append(f"{key}: {_format_scalar(value)}")
    if metadata.author:
        lines.append("author:")
        for value in metadata.author:
            lines.append(f"  - {_quote_string(value)}")
    for key, value in trailing_fields:
        if value:
            lines.append(f"{key}: {_format_scalar(value)}")
    if metadata.tags:
        lines.append("tags:")
        for value in metadata.tags:
            lines.append(f"  - {_format_tag(value)}")
    lines.append("---")
    return "\n".join(lines)


def compose_document(frontmatter: str | None, markdown: str) -> str:
    if frontmatter:
        body = markdown.strip()
        return f"{frontmatter}\n{body}".strip()
    return markdown.strip()


def postprocess_markdown(markdown: str) -> str:
    text = markdown.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _render_block(node: object, options: DomdownOptions) -> str:
    if isinstance(node, NavigableString):
        text = _normalize_inline(str(node))
        return text
    if not isinstance(node, Tag):
        return ""
    name = node.name.lower()
    if name in SKIP_TAGS:
        return ""
    if name in {"h1", "h2", "h3", "h4", "h5", "h6"}:
        level = int(name[1])
        text = _render_inline_children(node, options)
        return f"{'#' * level} {text}".strip()
    if name == "img":
        return _render_image(node, options)
    if name == "a":
        return _render_link(node, options)
    if name == "br":
        return ""
    if name == "ul":
        return _render_list(node, options, ordered=False)
    if name == "ol":
        return _render_list(node, options, ordered=True)
    if name == "blockquote":
        content = _render_container(node, options)
        return "\n".join(f"> {line}" if line else ">" for line in content.splitlines())
    if name == "table":
        return _render_table(node, options)
    if name == "li":
        return _render_list_item(node, options, ordered=False)
    if name == "p":
        return _render_inline_children(node, options)
    return _render_container(node, options)


def _render_container(node: Tag, options: DomdownOptions) -> str:
    parts = [part for part in (_render_block(child, options) for child in node.children) if part]
    return _normalize_markdown("\n\n".join(parts))


def _render_inline_children(node: Tag, options: DomdownOptions) -> str:
    parts = []
    for child in node.children:
        rendered = _render_inline(child, options)
        if rendered:
            parts.append(rendered)
    return _normalize_inline("".join(parts))


def _render_inline(node: object, options: DomdownOptions) -> str:
    if isinstance(node, NavigableString):
        return re.sub(r"\s+", " ", html_lib.unescape(str(node)))
    if not isinstance(node, Tag):
        return ""
    name = node.name.lower()
    if name in {"script", "style", "noscript"}:
        return ""
    if name == "br":
        return "\n"
    if name == "img":
        return _render_image(node, options)
    if name == "a":
        return _render_link(node, options)
    if name in {"code", "kbd", "samp"}:
        content = _render_inline_children(node, options)
        return f"`{content}`" if content else ""
    if name in {"strong", "b", "em", "i", "span"}:
        return _render_inline_children(node, options)
    if name in {"p", "div", "li"}:
        return _render_inline_children(node, options)
    return _render_inline_children(node, options)


def _render_link(node: Tag, options: DomdownOptions) -> str:
    href = _resolve_url(node.get("href"), options.base_url)
    content = "".join(_render_inline(child, options) for child in node.children).strip()
    if not content:
        return href or ""
    if content.startswith("![") and href:
        return f"[{content}]({href})"
    if href:
        return f"[{content}]({href})"
    return content


def _render_image(node: Tag, options: DomdownOptions) -> str:
    src = node.get("src") or node.get("data-src") or node.get("data-original") or ""
    src = _resolve_url(src, options.base_url)
    alt = node.get("alt") or node.get("title") or ""
    return f"![{alt}]({src})" if src else ""


def _render_list(node: Tag, options: DomdownOptions, ordered: bool) -> str:
    items = []
    for index, li in enumerate(node.find_all("li", recursive=False), 1):
        item = _render_list_item(li, options, ordered=ordered, index=index)
        if item:
            items.append(item)
    return "\n".join(items)


def _render_list_item(node: Tag, options: DomdownOptions, ordered: bool, index: int | None = None) -> str:
    prefix = f"{index}." if ordered and index is not None else "-"
    inline_parts = []
    nested_parts = []
    for child in node.children:
        if isinstance(child, Tag) and child.name and child.name.lower() in {"ul", "ol"}:
            nested_parts.append(_render_list(child, options, ordered=child.name.lower() == "ol"))
        else:
            rendered = _render_inline(child, options)
            if rendered:
                inline_parts.append(rendered)
    head = _normalize_inline("".join(inline_parts))
    blocks = [f"{prefix} {head}".rstrip() if head else prefix]
    blocks.extend(nested_parts)
    return "\n".join(blocks)


def _render_table(node: Tag, options: DomdownOptions) -> str:
    rows = []
    for tr in node.find_all("tr", recursive=True):
        cells = []
        for cell in tr.find_all(["th", "td"], recursive=False):
            cells.append(_normalize_inline(_render_inline_children(cell, options)))
        if cells:
            rows.append(cells)
    if not rows:
        return ""
    header = rows[0]
    divider = ["---" for _ in header]
    body = rows[1:]
    lines = ["| " + " | ".join(header) + " |", "| " + " | ".join(divider) + " |"]
    for row in body:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def _normalize_inline(text: str) -> str:
    text = html_lib.unescape(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _normalize_markdown(text: str) -> str:
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


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
    return _normalize_inline(tag.get_text(" ", strip=True))


def _select_texts(soup: BeautifulSoup, selector: str) -> tuple[str, ...]:
    values = []
    for tag in soup.select(selector):
        if isinstance(tag, Tag):
            value = _normalize_inline(tag.get_text(" ", strip=True))
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


def _split_tags(values: Iterable[str]) -> tuple[str, ...]:
    tags: list[str] = []
    for value in values:
        for part in re.split(r"\s*/\s*|\s*,\s*", value):
            part = part.strip()
            if part:
                tags.append(part)
    return tuple(tags)


def _looks_like_date(value: str) -> bool:
    return bool(re.match(r"^\w{3}\s+\d{1,2},\s+\d{4}$", value))


def _first_image_src(soup: BeautifulSoup) -> str | None:
    img = soup.find("img")
    if not isinstance(img, Tag):
        return None
    src = img.get("data-src") or img.get("data-original") or img.get("src")
    return src or None


def _resolve_url(url: str | None, base_url: str | None) -> str:
    if not url:
        return ""
    if base_url:
        return urljoin(base_url, url)
    return url


def _quote_string(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _format_scalar(value: str) -> str:
    if not value:
        return '""'
    if re.search(r"[:#\[\]{}&,*!?|>'\"\\]", value) or value.strip() != value or "\n" in value:
        return _quote_string(value)
    return value


def _format_tag(value: str) -> str:
    if not value:
        return '""'
    if re.search(r"[:#\[\]{}&,*!?|>'\"\\]", value) or "\n" in value:
        return _quote_string(value)
    return value
