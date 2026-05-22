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
