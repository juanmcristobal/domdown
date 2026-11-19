"""Document preparation that makes embedded or lazy source content available to Apply."""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, replace
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from bs4 import BeautifulSoup, Tag

from .._core import PipelineContext

GITHUB_BASE_URL = "https://github.com"
GITHUB_RELEASE_ASSETS_PATH = re.compile(r"^/[^/]+/[^/]+/releases/expanded_assets/[^?#]+$")
GITHUB_FETCH_TIMEOUT = 10
GITHUB_FETCH_MAX_BYTES = 2 * 1024 * 1024
GITHUB_BLOB_ROOT_SELECTORS = (
    ".react-code-file-contents",
    ".CodeBlob-module__codeBlobInner__tfjuQ",
    ".CodeBlob-module__codeBlobWrapper__RS6In",
    "section.BlobContent-module__blobContentSection__VOgZq",
    ".BlobViewContent-module__blobContentWrapper__JS0W6",
)


@dataclass(slots=True)
class PrepareDocumentStage:
    """Normalize document structures before metadata extraction and selector Apply."""

    name: str = "prepare"

    def run(self, context: PipelineContext) -> PipelineContext:
        document = context.document
        if not isinstance(document, (BeautifulSoup, Tag)) or not _is_github_document(document):
            return context
        context.options = replace(context.options, base_url=context.options.base_url or GITHUB_BASE_URL)
        route = _github_route(document)
        if route == "blob":
            _prepare_github_blob(document)
        elif route == "release":
            if _has_release_assets(document):
                context.reproducibility_limitations.append(
                    "GitHub release assets are external; exact replay refetches the fragment and requires it to remain available and unchanged."
                )
            _expand_release_assets(document, context.options.base_url or GITHUB_BASE_URL)
        return context


def _is_github_document(document: Tag) -> bool:
    site_name = _meta_content(document, "meta[property='og:site_name']")
    if site_name.casefold() == "github":
        return True
    url = _canonical_or_og_url(document)
    try:
        return (urlsplit(url).hostname or "").lower() == "github.com"
    except ValueError:
        return False


def _github_route(document: Tag) -> str:
    url = _canonical_or_og_url(document)
    route = _meta_content(document, "meta[name='route-controller']").casefold()
    if "/blob/" in url or route == "blob":
        return "blob"
    if "/issues/" in url:
        return "issue"
    if "/releases/tag/" in url or route == "releases":
        return "release"
    if "/security/advisories" in url or route == "security":
        return "security"
    return "generic"


def _prepare_github_blob(document: Tag) -> None:
    raw_lines = _raw_blob_lines(document)
    if raw_lines is None:
        return
    root = _select_first(document, GITHUB_BLOB_ROOT_SELECTORS)
    if root is None:
        root = document.body or document
    root.clear()
    pre = document.new_tag("pre", attrs={"class": "domdown-raw-lines"})
    code = document.new_tag("code")
    code.string = raw_lines
    pre.append(code)
    root.append(pre)


def _raw_blob_lines(document: Tag) -> str | None:
    for node in document.select("script[data-target='react-app.embeddedData']"):
        try:
            payload = json.loads(node.get_text("", strip=False))
        except json.JSONDecodeError:
            continue
        blob = payload.get("payload", {}).get("blob", {})
        payload_data = payload.get("payload", {})
        route = payload_data.get("codeViewBlobLayoutRoute", {})
        raw_lines = blob.get("rawLines") if isinstance(blob, dict) else None
        if not raw_lines and isinstance(route, dict):
            route_blob = route.get("blob", {})
            raw_lines = route_blob.get("rawLines") if isinstance(route_blob, dict) else None
        if not raw_lines and isinstance(payload_data.get("codeViewBlobLayoutRoute.StyledBlob"), dict):
            raw_lines = payload_data["codeViewBlobLayoutRoute.StyledBlob"].get("rawLines")
        if isinstance(raw_lines, list) and all(isinstance(line, str) for line in raw_lines):
            return "\n".join(raw_lines).strip()
    return None


def _has_release_assets(document: Tag) -> bool:
    return document.select_one("include-fragment[src*='/releases/expanded_assets/']") is not None


def _release_assets_url(base_url: str | None, src: str) -> str | None:
    """Validate the fixed GitHub release endpoint before making a request."""

    try:
        parts = urlsplit(urljoin(base_url or GITHUB_BASE_URL, src))
        port = parts.port
    except ValueError:
        return None
    if parts.scheme != "https" or parts.hostname != "github.com" or port is not None or parts.username is not None:
        return None
    if not GITHUB_RELEASE_ASSETS_PATH.match(parts.path):
        return None
    return urlunsplit(("https", "github.com", parts.path, parts.query, ""))


class _NoRedirectHandler(HTTPRedirectHandler):
    """Refuse redirects so a validated URL cannot bounce to another host."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001, ANN201
        return None


def _fetch_release_assets(url: str) -> str:
    """Fetch a release-assets fragment with byte and wall-clock limits."""

    opener = build_opener(_NoRedirectHandler)
    request = Request(url, headers={"User-Agent": "domdown/1.0"})
    deadline = time.monotonic() + GITHUB_FETCH_TIMEOUT
    chunks: list[bytes] = []
    size = 0
    with opener.open(request, timeout=GITHUB_FETCH_TIMEOUT) as response:
        while chunk := response.read(64 * 1024):
            size += len(chunk)
            if size > GITHUB_FETCH_MAX_BYTES or time.monotonic() > deadline:
                raise OSError("release assets fragment exceeded size or time limit")
            chunks.append(chunk)
    return b"".join(chunks).decode("utf-8", errors="replace")


def _expand_release_assets(document: Tag, base_url: str) -> None:
    include_fragment = document.select_one("include-fragment[src*='/releases/expanded_assets/']")
    if not isinstance(include_fragment, Tag):
        return
    src = str(include_fragment.get("src", "")).strip()
    fragment_url = _release_assets_url(base_url, src) if src else None
    if fragment_url is None:
        return
    try:
        fragment_html = _fetch_release_assets(fragment_url)
    except OSError:
        return
    fragment_document = BeautifulSoup(fragment_html, "html.parser")
    fragment_root = fragment_document.select_one("div.Box.Box--condensed") or fragment_document.select_one("ul")
    body_root = document.select_one("div[data-pjax='true'][data-test-selector='body-content']")
    if fragment_root is None or not isinstance(body_root, Tag):
        return
    markdown_body = body_root.select_one(".markdown-body")
    if not isinstance(markdown_body, Tag):
        markdown_body = body_root
    assets_container = document.new_tag("section", attrs={"data-domdown-keep-assets": "true"})
    heading = document.new_tag("h3")
    heading.string = "Assets"
    assets_container.append(heading)
    assets_container.append(fragment_root)
    markdown_body.append(assets_container)
    include_fragment.decompose()


def _select_first(document: Tag, selectors: tuple[str, ...]) -> Tag | None:
    for selector in selectors:
        candidate = document.select_one(selector)
        if isinstance(candidate, Tag):
            return candidate
    return None


def _meta_content(document: Tag, selector: str) -> str:
    node = document.select_one(selector)
    return str(node.get("content", "")).strip() if node is not None else ""


def _canonical_or_og_url(document: Tag) -> str:
    for selector in ("link[rel='canonical']", "meta[property='og:url']"):
        node = document.select_one(selector)
        if node is None:
            continue
        value = str(node.get("href") or node.get("content") or "").strip()
        if value:
            return value
    return ""
