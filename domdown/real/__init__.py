from __future__ import annotations

import json
from dataclasses import dataclass
from importlib import resources


PACKAGE_ROOT = resources.files(__name__)
MANIFEST_NAME = "manifest.json"


@dataclass(frozen=True, slots=True)
class RealExampleCase:
    """A curated real-world HTML-to-Markdown regression case shipped with the package."""

    id: str
    html_resource: str
    markdown_resource: str
    min_ratio: float
    xfail_reason: str | None = None
    description: str = ""

    def html_text(self) -> str:
        """Read the stored HTML fixture from package resources."""

        return (PACKAGE_ROOT / self.html_resource).read_text(encoding="utf-8")

    def markdown_text(self) -> str:
        """Read the stored Markdown fixture from package resources."""

        return (PACKAGE_ROOT / self.markdown_resource).read_text(encoding="utf-8")


def load_real_cases() -> list[RealExampleCase]:
    """Load the curated real-world regression cases from the package manifest."""

    payload = json.loads((PACKAGE_ROOT / MANIFEST_NAME).read_text(encoding="utf-8"))
    cases: list[RealExampleCase] = []
    for item in payload.get("cases", []):
        cases.append(
            RealExampleCase(
                id=item["id"],
                html_resource=item["html"],
                markdown_resource=item["markdown"],
                min_ratio=float(item["min_ratio"]),
                xfail_reason=item.get("xfail_reason"),
                description=item.get("description", ""),
            )
        )
    return cases

