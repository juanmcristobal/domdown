from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pytest

from domdown import html_to_markdown
from domdown.adapters import WikipediaAdapter

REAL_TESTS_DIR = Path(__file__).resolve().parents[1] / "real"
REAL_MANIFEST_PATH = REAL_TESTS_DIR / "manifest.json"


@dataclass(frozen=True, slots=True)
class RealExampleCase:
    """A real-world Wikipedia regression case stored under tests/real."""

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


def _wikipedia_cases() -> list[RealExampleCase]:
    """Return the curated real-world Wikipedia regression cases."""

    return [case for case in load_real_cases(layer="adapter") if case.id.startswith("wikipedia_")]


def _case_param(case: RealExampleCase) -> pytest.ParameterSet:
    """Attach a stable test id to each real-world Wikipedia regression case."""

    return pytest.param(case, id=case.id)


@pytest.mark.parametrize("case", [_case_param(case) for case in _wikipedia_cases()])
def test_wikipedia_adapter_matches_the_curated_snapshot(case: RealExampleCase) -> None:
    """Wikipedia pages should render to the curated Markdown snapshot."""

    assert WikipediaAdapter().name == "wikipedia"

    actual = html_to_markdown(case.html_text())
    expected = case.markdown_text()

    assert actual == expected
