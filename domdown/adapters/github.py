from __future__ import annotations

import json
from dataclasses import dataclass, replace
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup, Tag

from .._core import PipelineContext

GITHUB_SITE_NAME = "GitHub"
GITHUB_BASE_URL = "https://github.com"

# Common GitHub chrome that should not survive into article-like output.
GITHUB_REMOVE_SELECTORS = (
    ".Overlay",
    ".Overlay-body",
    ".Overlay-header",
    ".Overlay-headerFilter",
    ".Overlay-footer",
    ".Banner",
    ".SelectPanel-loadingPanel",
    "nav[aria-label='Global']",
    "header[role='banner']",
    "footer",
)

# Repo and file-view chrome that should not be rendered as content.
GITHUB_REPOSITORY_REMOVE_SELECTORS = (
    ".Header",
    ".site-header",
    ".js-header-wrapper",
    ".UnderlineNav",
    ".file-navigation",
    ".file-header",
    ".repohead",
    ".repository-content > nav",
)

# Blob pages need to be narrowed to the file contents wrapper before selection.
GITHUB_BLOB_ROOT_SELECTORS = (
    ".react-code-file-contents",
    ".CodeBlob-module__codeBlobInner__tfjuQ",
    ".CodeBlob-module__codeBlobWrapper__RS6In",
    "section.BlobContent-module__blobContentSection__VOgZq",
    ".BlobViewContent-module__blobContentWrapper__JS0W6",
)


@dataclass(slots=True)
class GitHubAdapter:
    """Family adapter that removes GitHub chrome and normalizes GitHub pages."""

    name: str = "github"

    def matches(self, context: PipelineContext) -> bool:
        """Return True when the parsed document looks like a GitHub page."""

        return _site_name(context.document) == GITHUB_SITE_NAME

    def preprocess(self, context: PipelineContext) -> PipelineContext:
        """Normalize GitHub-specific source resolution and remove common chrome."""

        context.options = replace(
            context.options,
            base_url=context.options.base_url or GITHUB_BASE_URL,
        )
        _remove_selectors(context.document, GITHUB_REMOVE_SELECTORS + GITHUB_REPOSITORY_REMOVE_SELECTORS)
        return context

    def refine_metadata(self, context: PipelineContext) -> PipelineContext:
        """Refine metadata and, for blob pages, narrow the document to file contents."""

        kind = _page_kind(context.document)
        if kind == "blob":
            raw_text = _raw_blob_text(context.document)
            if raw_text:
                context.markdown = raw_text
                context.document = None
                return context
            blob_root = _select_first(context.document, GITHUB_BLOB_ROOT_SELECTORS)
            if blob_root is not None:
                context.document = blob_root
        if kind == "release":
            _expand_release_assets(context.document, context.options.base_url or GITHUB_BASE_URL)
        if kind == "issue":
            issue_author = _meta_content(context.document, "meta[property='og:author:username']")
            issue_root = _select_first(context.document, (".repository-content", ".js-repo-pjax-container"))
            if issue_root is not None:
                context.document = issue_root
            if context.metadata is not None:
                if issue_author:
                    context.metadata = replace(context.metadata, author=(issue_author,))
        return context

    def postprocess(self, context: PipelineContext) -> PipelineContext:
        """Normalize GitHub-specific rendered output after the core pipeline."""

        if _page_kind(context.document) == "blob":
            raw_text = _raw_blob_text(context.document)
            if raw_text:
                context.markdown = raw_text
        return context


def _site_name(document: Tag | None) -> str:
    """Read the GitHub site name from Open Graph metadata."""

    if document is None:
        return ""
    return _meta_content(document, "meta[property='og:site_name']")


def _page_kind(document: Tag | None) -> str:
    """Classify a GitHub page into a small set of variants."""

    url = _meta_content(document, "meta[property='og:url']")
    route = _meta_content(document, "meta[name='route-controller']")
    if "/blob/" in url or route == "blob":
        return "blob"
    if "/issues/" in url or route == "issues":
        return "issue"
    if "/releases/tag/" in url or route == "releases":
        return "release"
    if "/security/advisories" in url or route == "security":
        return "security"
    return "generic"


def _remove_selectors(document: Tag | None, selectors: tuple[str, ...]) -> None:
    """Remove a list of selectors from the parsed document in place."""

    if document is None:
        return
    for selector in selectors:
        for node in document.select(selector):
            if isinstance(node, Tag):
                node.decompose()


def _select_first(document: Tag | None, selectors: tuple[str, ...]) -> Tag | None:
    """Return the first matching GitHub subtree for a specific page variant."""

    if document is None:
        return None
    for selector in selectors:
        node = document.select_one(selector)
        if isinstance(node, Tag):
            return node
    return None


def _meta_content(document: Tag | None, selector: str) -> str:
    """Read a meta content value from the parsed document."""

    if document is None:
        return ""
    node = document.select_one(selector)
    if node is None:
        return ""
    return str(node.get("content", "")).strip()


def _raw_blob_text(document: Tag | None) -> str:
    """Extract exact file text from GitHub's embedded blob payload when present."""

    if document is None:
        return ""
    for node in document.select("script[data-target='react-app.embeddedData']"):
        try:
            payload = json.loads(node.get_text("", strip=False))
        except json.JSONDecodeError:
            continue
        raw_lines = (
            payload.get("payload", {})
            .get("blob", {})
            .get("rawLines")
            or payload.get("payload", {})
            .get("codeViewBlobLayoutRoute", {})
            .get("blob", {})
            .get("rawLines")
            or payload.get("payload", {})
            .get("codeViewBlobLayoutRoute.StyledBlob", {})
            .get("rawLines")
        )
        if isinstance(raw_lines, list) and all(isinstance(line, str) for line in raw_lines):
            return "\n".join(raw_lines).strip()
    return ""


def _expand_release_assets(document: Tag | None, base_url: str) -> None:
    """Inline GitHub's lazy-loaded release assets fragment into the release body."""

    if document is None:
        return
    include_fragment = document.select_one("include-fragment[src*='/releases/expanded_assets/']")
    if not isinstance(include_fragment, Tag):
        return
    src = str(include_fragment.get("src", "")).strip()
    if not src:
        return
    fragment_url = urljoin(base_url or GITHUB_BASE_URL, src)
    try:
        request = Request(fragment_url, headers={"User-Agent": "domdown/1.0"})
        with urlopen(request, timeout=10) as response:
            fragment_html = response.read().decode("utf-8", errors="replace")
    except OSError:
        return
    fragment_document = BeautifulSoup(fragment_html, "html.parser")
    fragment_root = fragment_document.select_one("div.Box.Box--condensed") or fragment_document.select_one("ul")
    if fragment_root is None:
        return
    body_root = _select_first(document, ("div[data-pjax='true'][data-test-selector='body-content']",))
    if body_root is None:
        return
    markdown_body = body_root.select_one(".markdown-body")
    if not isinstance(markdown_body, Tag):
        markdown_body = body_root

    assets_soup = BeautifulSoup("", "html.parser")
    assets_container = assets_soup.new_tag("section")
    heading = assets_soup.new_tag("h3")
    heading.string = "Assets"
    assets_container.append(heading)
    assets_container.append(fragment_root)
    markdown_body.append(assets_container)
    include_fragment.decompose()
