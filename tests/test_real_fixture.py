from __future__ import annotations

from pathlib import Path

from domdown import DomdownOptions, html_to_markdown


def test_real_sample_file_is_supported_when_available() -> None:
    """A real fixture should flow through the pipeline without crashing."""

    sample = Path(
        "/home/juanmcristobal/projects/llm-wiki-system/test_extract_html_raw/html/2025_12_27-malicious-npm-packages-used-as.html"
    )
    if not sample.exists():
        return

    html = sample.read_text(encoding="utf-8")
    output = html_to_markdown(html, DomdownOptions(created="2026-05-15"))

    assert "Malicious npm Packages Used as Phishing Infrastructure" in output
    assert "secure-docs-app" in output
    assert "Cybersecurity" in output
