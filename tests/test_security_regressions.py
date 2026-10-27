"""Regression tests for the issues reported by the security review (F1-F7)."""

from __future__ import annotations

import time

import pytest

from domdown import DomdownOptions, html_to_markdown
from domdown._text import format_scalar, safe_url
from domdown.adapters import github as github_adapter

GITHUB_RELEASE_PAGE = """
<html><head>
<meta property="og:site_name" content="GitHub">
<meta name="route-controller" content="releases">
</head><body><article>
<h1>Release</h1>
<div data-pjax="true" data-test-selector="body-content"><div class="markdown-body"><p>Notes</p></div></div>
<include-fragment src="{src}"></include-fragment>
</article></body></html>
"""


class _FakeResponse:
    def __init__(self, body: bytes | None = None, endless: bool = False) -> None:
        self.body = body or b""
        self.endless = endless

    def read(self, size: int = -1) -> bytes:
        if self.endless:
            return b"x" * size
        chunk, self.body = self.body[:size], self.body[size:]
        return chunk

    def __enter__(self) -> _FakeResponse:
        return self

    def __exit__(self, *exc: object) -> None:
        return None


class _FakeOpener:
    def __init__(self, response: _FakeResponse) -> None:
        self.response = response
        self.urls: list[str] = []

    def open(self, request, timeout: float):  # noqa: ANN001
        self.urls.append(request.full_url)
        return self.response


def _install_opener(monkeypatch: pytest.MonkeyPatch, response: _FakeResponse) -> _FakeOpener:
    opener = _FakeOpener(response)
    monkeypatch.setattr(github_adapter, "build_opener", lambda *handlers: opener)
    return opener


@pytest.mark.parametrize(
    "src",
    [
        "http://169.254.169.254/latest/meta-data/?a=/releases/expanded_assets/",
        "file:///etc/passwd#/releases/expanded_assets/",
        "https://evil.example/o/r/releases/expanded_assets/v1",
        "https://github.com.evil.example/o/r/releases/expanded_assets/v1",
        "https://user@github.com/o/r/releases/expanded_assets/v1",
        "https://github.com:8443/o/r/releases/expanded_assets/v1",
        "http://github.com/o/r/releases/expanded_assets/v1",
    ],
)
def test_release_assets_fetch_refuses_non_github_urls(monkeypatch: pytest.MonkeyPatch, src: str) -> None:
    opener = _install_opener(monkeypatch, _FakeResponse(b"<ul><li>secret</li></ul>"))

    markdown = html_to_markdown(GITHUB_RELEASE_PAGE.format(src=src))

    assert opener.urls == []
    assert "secret" not in markdown


def test_release_assets_fetch_allows_github_and_caps_size(monkeypatch: pytest.MonkeyPatch) -> None:
    src = "/nodejs/node/releases/expanded_assets/v25.3.0"
    opener = _install_opener(monkeypatch, _FakeResponse(b"<ul><li>node.tar.gz</li></ul>"))
    assert "node.tar.gz" in html_to_markdown(GITHUB_RELEASE_PAGE.format(src=src))
    assert opener.urls == ["https://github.com/nodejs/node/releases/expanded_assets/v25.3.0"]

    _install_opener(monkeypatch, _FakeResponse(endless=True))
    assert "Assets" not in html_to_markdown(GITHUB_RELEASE_PAGE.format(src=src))


def test_entity_escaped_text_does_not_become_raw_html() -> None:
    html = (
        "<article><h1>T</h1><p>Payload: &lt;img src=x onerror=alert(1)&gt; and &amp;lt;script&amp;gt;</p>"
        "<ul><li>&lt;svg onload=x&gt;</li></ul><p>Code <code>&lt;b&gt;</code> and a &lt; b</p></article>"
    )
    markdown = html_to_markdown(html, DomdownOptions(emit_frontmatter=False))

    assert "<img" not in markdown and "<svg" not in markdown and "<script" not in markdown
    assert "&lt;img src=x onerror=alert(1)>" in markdown
    assert "`<b>`" in markdown
    assert "a < b" in markdown


@pytest.mark.parametrize("href", ["javascript:alert(1)", " JaVa\tScRiPt:alert(1)", "vbscript:x", "data:text/html,x"])
def test_dangerous_link_schemes_are_dropped(href: str) -> None:
    markdown = html_to_markdown(
        f'<article><h1>T</h1><p>See <a href="{href}">report</a></p></article>',
        DomdownOptions(base_url="https://example.com/post", emit_frontmatter=False),
    )
    assert "script" not in markdown.lower().replace("report", "")
    assert "report" in markdown
    assert safe_url(href) == ""
    assert safe_url("https://example.com/a") == "https://example.com/a"
    assert safe_url("data:image/png;base64,AAAA") == "data:image/png;base64,AAAA"


def test_frontmatter_values_cannot_break_out_of_yaml() -> None:
    html = (
        '<html><head><title>null</title><meta name="description" content="Summary&#10;---&#10;injected: 1">'
        "</head><body><article><h1>null</h1><p>Body</p></article></body></html>"
    )
    document = html_to_markdown(html)
    frontmatter, _, _ = document.removeprefix("---\n").partition("\n---\n")

    lines = frontmatter.splitlines()
    assert "---" not in lines
    assert 'title: "null"' in lines
    assert 'description: "Summary\\n---\\ninjected: 1"' in lines
    assert not any(line.startswith("injected") for line in lines)
    assert format_scalar("@x") == '"@x"'


def test_medium_noise_patterns_do_not_backtrack_catastrophically() -> None:
    line = "[![" + "](https://miro.medium.com/)](https://medium.com/@a" * 4000
    html = f'<html><head><meta property="og:site_name" content="Medium"></head><body><article><h1>T</h1><p>{line}</p></article></body></html>'

    started = time.monotonic()
    html_to_markdown(html)
    assert time.monotonic() - started < 5


def test_nested_card_feed_check_is_not_cubic() -> None:
    from bs4 import BeautifulSoup

    from domdown._document.clean import _looks_like_article_feed_block

    depth = 200
    html = (
        "<article>"
        + f'<div class="xcardx">{"<b></b>" * 20}' * depth
        + "<h2>x</h2><p>" + "word " * 230 + "</p>"
        + "</div>" * depth
        + "</article>"
    )
    nodes = BeautifulSoup(html, "lxml").find_all("div")

    started = time.monotonic()
    for node in nodes:
        _looks_like_article_feed_block(node)
    # Was ~30s before the fix (cubic); now well under a second.
    assert time.monotonic() - started < 5
