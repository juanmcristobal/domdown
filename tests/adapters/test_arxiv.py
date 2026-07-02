from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pytest

from domdown import html_to_markdown
from domdown._pipeline import HtmlToMarkdownPipeline
from domdown.adapters import ArXivAdapter

REAL_TESTS_DIR = Path(__file__).resolve().parents[1] / "real"
REAL_MANIFEST_PATH = REAL_TESTS_DIR / "manifest.json"


@dataclass(frozen=True, slots=True)
class RealExampleCase:
    """A real-world arXiv regression case stored under tests/real."""

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


def _arxiv_cases() -> list[RealExampleCase]:
    """Return the curated real-world arXiv regression cases."""

    return [case for case in load_real_cases(layer="adapter") if case.id.startswith("arxiv_")]


def _case_param(case: RealExampleCase) -> pytest.ParameterSet:
    """Attach a stable test id to each real-world arXiv regression case."""

    return pytest.param(case, id=case.id)


def test_arxiv_adapter_matches_abs_pages_and_cleans_title_chrome() -> None:
    """ArXiv abstract pages should render the paper title and abstract cleanly."""

    pipeline = HtmlToMarkdownPipeline(adapters=(ArXivAdapter(),))
    html = """
        <html>
          <head>
            <meta property="og:site_name" content="arXiv.org" />
            <meta property="og:url" content="https://arxiv.org/abs/2603.28627v1" />
            <meta property="og:title" content="Shor's algorithm is possible with as few as 10,000 reconfigurable atomic qubits" />
            <link rel="canonical" href="https://arxiv.org/abs/2603.28627" />
          </head>
          <body>
            <div id="abs">
              <div class="leftcolumn">
                <h1 class="title">Title:Shor's algorithm is possible with as few as 10,000 reconfigurable atomic qubits</h1>
                <blockquote class="abstract">Abstract: Quantum computers have the potential to perform computational tasks beyond the reach of classical machines.</blockquote>
              </div>
              <div class="extra-services">
                <nav>Related Papers</nav>
              </div>
            </div>
          </body>
        </html>
        """

    result = pipeline.run(html)

    assert result.metadata is not None
    assert result.metadata.title == "Shor's algorithm is possible with as few as 10,000 reconfigurable atomic qubits"
    assert "# Shor's algorithm is possible with as few as 10,000 reconfigurable atomic qubits" in result.markdown
    assert "# Quantum Physics" not in result.markdown
    assert "Related Papers" not in result.markdown


@pytest.mark.parametrize("case", [_case_param(case) for case in _arxiv_cases()])
def test_arxiv_adapter_matches_the_curated_snapshot(case: RealExampleCase) -> None:
    """ArXiv abstract pages should render to the curated Markdown snapshot."""

    assert ArXivAdapter().name == "arxiv"

    actual = html_to_markdown(case.html_text())
    expected = case.markdown_text()

    assert actual == expected
