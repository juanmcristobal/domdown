from __future__ import annotations

from pathlib import Path


def test_root_package_has_no_reexport_modules() -> None:
    """Only the public API module and package initializer should live at the root."""

    package_root = Path(__file__).resolve().parents[1] / "domdown"
    root_modules = sorted(
        path.name for path in package_root.glob("*.py") if path.name not in {"__init__.py", "api.py"}
    )

    assert root_modules == []
