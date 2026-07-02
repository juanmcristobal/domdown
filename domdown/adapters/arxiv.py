from __future__ import annotations

import re
from dataclasses import dataclass, replace
from urllib.parse import urlsplit

from bs4 import Tag

from .._core import PipelineContext

ARXIV_SITE_NAME = "arXiv.org"
ARXIV_HOST = "arxiv.org"
ARXIV_REMOVE_SELECTORS = (
    "div.extra-services",
    "div#search-result-wrapper",
    "div#bottom-pager",
    "aside",
    "footer",
    "nav",
    "#mask",
    "#notification",
)


@dataclass(slots=True)
class ArXivAdapter:
    """Family adapter that trims arXiv abstract pages to the paper summary."""

    name: str = "arxiv"

    def matches(self, context: PipelineContext) -> bool:
        """Return True when the parsed document looks like an arXiv abstract page."""

        if _site_name(context.document) != ARXIV_SITE_NAME:
            return False
        page_url = _page_url(context.document)
        if not page_url:
            return True
        path = urlsplit(page_url).path
        return path.startswith("/abs/")

    def preprocess(self, context: PipelineContext) -> PipelineContext:
        """Narrow arXiv pages to the abstract container and remove page chrome."""

        if context.options.base_url is None:
            context.options = replace(context.options, base_url=f"https://{ARXIV_HOST}")
        _remove_selectors(context.document, ARXIV_REMOVE_SELECTORS)
        return context

    def refine_metadata(self, context: PipelineContext) -> PipelineContext:
        """Prefer the paper title exposed in Open Graph metadata."""

        title = _meta_content(context.document, "meta[property='og:title']")
        if title and context.metadata is not None:
            context.metadata = replace(context.metadata, title=title)
        root = context.document.select_one("div#abs") if context.document is not None else None
        if isinstance(root, Tag):
            context.document = root
        return context

    def postprocess(self, context: PipelineContext) -> PipelineContext:
        """Clean arXiv-specific rendering artifacts after Markdown generation."""

        context.markdown = _clean_markdown(context.markdown)
        return context


def _site_name(document: Tag | None) -> str:
    """Read the Open Graph site name from the current document."""

    if document is None:
        return ""
    return _meta_content(document, "meta[property='og:site_name']")


def _page_url(document: Tag | None) -> str:
    """Read the canonical arXiv URL for the current page."""

    if document is None:
        return ""
    for selector in (
        "link[rel='canonical']",
        "meta[property='og:url']",
    ):
        node = document.select_one(selector)
        if not isinstance(node, Tag):
            continue
        url = str(node.get("href") or node.get("content") or "").strip()
        if url:
            return url
    return ""


def _meta_content(document: Tag | None, selector: str) -> str:
    """Read a meta content value from the parsed document."""

    if document is None:
        return ""
    node = document.select_one(selector)
    if node is None:
        return ""
    return str(node.get("content", "")).strip()


def _remove_selectors(document: Tag | None, selectors: tuple[str, ...]) -> None:
    """Remove a list of selectors from the parsed document in place."""

    if document is None:
        return
    for selector in selectors:
        for node in document.select(selector):
            if isinstance(node, Tag):
                node.decompose()


def _clean_markdown(markdown: str) -> str:
    """Remove arXiv chrome and normalize the rendered title line."""

    text = markdown.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.splitlines()
    cleaned: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped == "# Quantum Physics":
            continue
        if stripped.startswith("# Title:"):
            cleaned.append("# " + stripped.removeprefix("# Title:").lstrip())
            continue
        if stripped in {
            "Full-text links:",
            "Access Paper:",
            "Current browse context:",
            "References & Citations",
            "Bibliographic and Citation Tools",
            "Code, Data and Media Associated with this Article",
            "Demos",
            "Related Papers",
            "About arXivLabs",
            "arXivLabs: experimental projects with community collaborators",
            "Loading...",
            "BibTeX formatted citation",
            "Data provided by:",
            "Bookmark",
        }:
            continue
        cleaned.append(line)
    return _collapse_blank_lines(cleaned).strip()


def _collapse_blank_lines(lines: list[str]) -> str:
    """Collapse repeated blank lines without altering fenced code blocks."""

    collapsed: list[str] = []
    blank_count = 0
    in_code_block = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            blank_count = 0
            collapsed.append(line)
            continue
        if in_code_block:
            collapsed.append(line)
            continue
        if not stripped:
            blank_count += 1
            if blank_count <= 1:
                collapsed.append("")
            continue
        blank_count = 0
        collapsed.append(line)
    return "\n".join(collapsed)
