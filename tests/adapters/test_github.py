from __future__ import annotations

import pytest

from domdown import html_to_markdown
from domdown.adapters import GitHubAdapter
from tests.real import RealExampleCase, load_real_cases


def _github_cases() -> list[RealExampleCase]:
    """Return the curated real-world GitHub regression cases."""

    return [case for case in load_real_cases(layer="adapter") if case.id.startswith("github_")]


def _case_param(case: RealExampleCase) -> pytest.ParameterSet:
    """Attach a stable test id to each real-world GitHub regression case."""

    return pytest.param(case, id=case.id)


@pytest.mark.parametrize("case", [_case_param(case) for case in _github_cases()])
def test_github_adapter_matches_the_curated_snapshot(case: RealExampleCase) -> None:
    """GitHub pages should render to the curated Markdown snapshot."""

    assert GitHubAdapter().name == "github"
    actual = html_to_markdown(case.html_text())
    expected = case.markdown_text()

    assert actual == expected


def test_github_blob_uses_embedded_raw_lines_without_line_numbers() -> None:
    """GitHub blob pages should render raw file lines instead of UI line numbers."""

    case = next(case for case in _github_cases() if case.id == "github_blob_release_notes")

    actual = html_to_markdown(case.html_text())
    body = actual.split("---\n", 2)[-1].lstrip()

    assert body.startswith("2025-12-03 (WEDNESDAY): RECENT SURGE IN CLICKFIX ACTIVITY")
    assert not body.startswith("1\n\n2\n\n3")
    assert "\n\n- https://x.com/Unit42_Intel/status/1996363155237187909\n\n" not in body
    assert "  -- Mimicking Google's \"Aw Snap!\" error" in body


def test_github_release_expands_lazy_asset_fragment() -> None:
    """GitHub release pages should include the expanded assets list."""

    case = next(case for case in load_real_cases(layer="adapter") if case.id == "node_release_tag_v2530")

    actual = html_to_markdown(case.html_text())

    assert "### Assets" in actual
    assert "https://github.com/nodejs/node/archive/refs/tags/v25.3.0.zip" in actual
    assert "https://github.com/nodejs/node/archive/refs/tags/v25.3.0.tar.gz" in actual
