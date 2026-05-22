from __future__ import annotations

from dataclasses import dataclass, replace

from bs4 import Tag

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
            blob_root = _select_first(context.document, GITHUB_BLOB_ROOT_SELECTORS)
            if blob_root is not None:
                context.document = blob_root
        if kind == "issue" and context.metadata is not None:
            issue_author = _meta_content(context.document, "meta[property='og:author:username']")
            if issue_author:
                context.metadata = replace(context.metadata, author=(issue_author,))
        return context

    def postprocess(self, context: PipelineContext) -> PipelineContext:
        """Leave the core Markdown output untouched for GitHub pages."""

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
