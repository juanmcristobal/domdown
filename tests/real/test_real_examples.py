from __future__ import annotations

import pytest

from domdown import html_to_markdown
from . import RealExampleCase, load_real_cases


def _case_param(case: RealExampleCase) -> pytest.ParameterSet:
    """Attach a stable test id to each real-world regression case."""

    return pytest.param(case, id=case.id)


@pytest.mark.parametrize("case", [_case_param(case) for case in load_real_cases()])
def test_real_example_cases_match_the_expected_markdown_snapshot(case: RealExampleCase) -> None:
    """Real HTML fixtures should match the Markdown snapshot stored in tests/real/raw."""

    actual = html_to_markdown(case.html_text())
    expected = case.markdown_text()

    assert actual == expected
