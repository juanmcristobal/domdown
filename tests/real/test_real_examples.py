from __future__ import annotations

import pytest

from domdown import html_to_markdown
from domdown._core import DomdownOptions

from . import RealExampleCase, load_real_cases


def _case_param(case: RealExampleCase) -> pytest.ParameterSet:
    """Attach a stable test id to each real-world regression case."""

    return pytest.param(case, id=case.id)


@pytest.mark.parametrize("case", [_case_param(case) for case in load_real_cases()])
def test_real_example_cases_match_the_expected_markdown_snapshot(case: RealExampleCase) -> None:
    """Real HTML fixtures should match the Markdown snapshot stored in tests/real/raw."""

    options = DomdownOptions(base_url=case.base_url) if case.base_url else DomdownOptions()
    actual = html_to_markdown(case.html_text(), options)
    expected = case.markdown_text()

    assert actual == expected
