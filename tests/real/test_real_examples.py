from __future__ import annotations

from difflib import SequenceMatcher

import pytest

from domdown import html_to_markdown

from . import RealExampleCase, load_real_cases


def _case_param(case: RealExampleCase) -> pytest.ParameterSet:
    """Attach xfail marks only to cases that are intentionally tracked failures."""

    marks = [pytest.mark.xfail(reason=case.xfail_reason)] if case.xfail_reason else []
    return pytest.param(case, id=case.id, marks=marks)


@pytest.mark.parametrize("case", [_case_param(case) for case in load_real_cases()])
def test_real_example_cases_stay_above_their_threshold(case: RealExampleCase) -> None:
    """Real HTML fixtures should keep a stable similarity score against their reference Markdown."""

    actual = html_to_markdown(case.html_text())
    expected = case.markdown_text()
    ratio = SequenceMatcher(None, actual, expected).ratio()

    assert ratio >= case.min_ratio, f"{case.id} fell below {case.min_ratio:.2f} with ratio {ratio:.4f}"

