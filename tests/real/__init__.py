from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


REAL_TESTS_DIR = Path(__file__).resolve().parent
REAL_MANIFEST_PATH = REAL_TESTS_DIR / "manifest.json"


@dataclass(frozen=True, slots=True)
class RealExampleCase:
    """A real-world HTML-to-Markdown regression case."""

    id: str
    html_path: Path
    markdown_path: Path
    min_ratio: float
    xfail_reason: str | None = None
    description: str = ""

    def html_text(self) -> str:
        """Read the stored HTML fixture."""

        return self.html_path.read_text(encoding="utf-8")

    def markdown_text(self) -> str:
        """Read the stored expected Markdown fixture."""

        return self.markdown_path.read_text(encoding="utf-8")


def load_real_cases() -> list[RealExampleCase]:
    """Load the curated real-world regression cases from the manifest."""

    payload = json.loads(REAL_MANIFEST_PATH.read_text(encoding="utf-8"))
    cases: list[RealExampleCase] = []
    for item in payload.get("cases", []):
        cases.append(
            RealExampleCase(
                id=item["id"],
                html_path=REAL_TESTS_DIR / item["html"],
                markdown_path=REAL_TESTS_DIR / item["markdown"],
                min_ratio=float(item["min_ratio"]),
                xfail_reason=item.get("xfail_reason"),
                description=item.get("description", ""),
            )
        )
    return cases

