from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pytest

from domdown import DomdownOptions, HtmlToMarkdownPipeline, html_to_markdown
from domdown.stages import prepare as document_preparation

REAL_TESTS_DIR = Path(__file__).resolve().parents[1] / "real"
REAL_MANIFEST_PATH = REAL_TESTS_DIR / "manifest.json"


@dataclass(frozen=True, slots=True)
class RealExampleCase:
    """A real-world GitHub regression case stored under tests/real."""

    id: str
    html_path: Path
    markdown_path: Path
    description: str = ""

    def html_text(self) -> str:
        return self.html_path.read_text(encoding="utf-8")

    def markdown_text(self) -> str:
        return self.markdown_path.read_text(encoding="utf-8")


def load_real_cases(layer: str | None = "core") -> list[RealExampleCase]:
    """Load the curated real-world regression cases from the manifest."""

    payload = json.loads(REAL_MANIFEST_PATH.read_text(encoding="utf-8"))
    cases: list[RealExampleCase] = []
    for item in payload.get("cases", []):
        if layer is not None and item.get("layer", "core") != layer:
            continue
        cases.append(
            RealExampleCase(
                id=item["id"],
                html_path=REAL_TESTS_DIR / item["html"],
                markdown_path=REAL_TESTS_DIR / item["markdown"],
                description=item.get("description", ""),
            )
        )
    return cases


def _github_cases() -> list[RealExampleCase]:
    """Return the curated real-world GitHub regression cases."""

    return [case for case in load_real_cases(layer="adapter") if case.id.startswith("github_")]


def _case_param(case: RealExampleCase) -> pytest.ParameterSet:
    """Attach a stable test id to each real-world GitHub regression case."""

    return pytest.param(case, id=case.id)


def _stub_release_assets(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep release fixtures deterministic without contacting GitHub."""

    fragment = (
        '<ul><li><a href="/nodejs/node/archive/refs/tags/v25.3.0.zip">Source code (zip)</a> '
        '2026-01-13T12:49:52Z</li><li><a href="/nodejs/node/archive/refs/tags/v25.3.0.tar.gz">'
        "Source code (tar.gz)</a> 2026-01-13T12:49:52Z</li></ul>"
    )
    monkeypatch.setattr(document_preparation, "_fetch_release_assets", lambda url: fragment)


@pytest.mark.parametrize("case", [_case_param(case) for case in _github_cases()])
def test_github_site_criteria_matches_the_curated_snapshot(
    case: RealExampleCase, monkeypatch: pytest.MonkeyPatch
) -> None:
    """GitHub selector rules and document preparation should match each snapshot."""

    if case.id == "node_release_tag_v2530":
        _stub_release_assets(monkeypatch)

    result = HtmlToMarkdownPipeline(DomdownOptions(emit_frontmatter=True)).run(case.html_text())
    actual = result.document
    expected = case.markdown_text()

    assert result.trace.to_dict()["criteria_source"] == "site"
    assert actual == expected


def test_github_blob_uses_embedded_raw_lines_without_line_numbers() -> None:
    """GitHub blob pages should render raw file lines instead of UI line numbers."""

    case = next(case for case in _github_cases() if case.id == "github_blob_release_notes")

    actual = html_to_markdown(case.html_text())
    body = actual.split("---\n", 2)[-1].lstrip()

    assert body.startswith("2025-12-03 (WEDNESDAY): RECENT SURGE IN CLICKFIX ACTIVITY")
    assert not body.startswith("1\n\n2\n\n3")
    assert "\n\n- https://x.com/Unit42_Intel/status/1996363155237187909\n\n" not in body
    assert '  -- Mimicking Google\'s "Aw Snap!" error' in body


def test_github_release_expands_lazy_asset_fragment(monkeypatch: pytest.MonkeyPatch) -> None:
    """GitHub release pages should include the expanded assets list."""

    case = next(case for case in load_real_cases(layer="adapter") if case.id == "node_release_tag_v2530")
    _stub_release_assets(monkeypatch)

    actual = html_to_markdown(case.html_text())

    assert "### Assets" in actual
    assert "https://github.com/nodejs/node/archive/refs/tags/v25.3.0.zip" in actual
    assert "https://github.com/nodejs/node/archive/refs/tags/v25.3.0.tar.gz" in actual


def test_github_issue_rule_selects_body_and_uses_generic_author_metadata() -> None:
    """Issue criteria select repository content; generic metadata reads the author."""

    html = """
        <html>
          <head>
            <meta property="og:site_name" content="GitHub" />
            <meta property="og:url" content="https://github.com/example/repo/issues/123" />
            <meta property="og:author:username" content="octocat" />
          </head>
          <body>
            <div class="repository-content">
              <article><h1>Issue title</h1><p>Issue body.</p></article>
            </div>
          </body>
        </html>
    """
    result = HtmlToMarkdownPipeline(DomdownOptions(emit_frontmatter=False)).run(html)
    assert result.metadata is not None
    assert result.metadata.author == ("octocat",)
    assert "Issue body." in result.markdown


def test_github_security_variant_uses_its_declarative_rule() -> None:
    """Security advisory pages are matched by a distinct declarative rule."""

    html = """
        <html>
          <head>
            <meta property="og:site_name" content="GitHub" />
            <meta property="og:url" content="https://github.com/security/advisories/GHSA-1234" />
          </head>
            <body><main>
            <article><h1>Advisory</h1><p>Body</p></article>
            </main></body>
        </html>
    """
    result = HtmlToMarkdownPipeline(DomdownOptions(emit_frontmatter=False)).run(html)
    assert result.trace.to_dict()["criteria_source"] == "site"
    assert "Advisory" in result.markdown
