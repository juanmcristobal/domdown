"""Helper utilities for domdown tests."""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup, Tag


def get_fixtures() -> List[Dict[str, Any]]:
    """Return list of fixture files from the test fixtures directory."""
    from pathlib import Path

    fixtures_dir = Path(__file__).parent / "fixtures"
    fixtures = []
    for file_path in sorted(fixtures_dir.glob("*.html")):
        fixtures.append(
            {
                "name": file_path.stem,
                "path": file_path,
            }
        )
    return fixtures


def parse_document(html: str, url: Optional[str] = None) -> BeautifulSoup:
    """Parse HTML into a BeautifulSoup document element."""
    soup = BeautifulSoup(html, "lxml")
    if url:
        html_el = soup.find("html")
        if html_el is not None:
            html_el["data-url"] = url
        if hasattr(soup, "URL"):
            soup.URL = url
    return soup


def create_extractor(
    html: str = "<html><body></body></html>",
    url: str = "https://www.youtube.com/watch?v=test123",
    options: Optional[Dict[str, Any]] = None,
) -> Tag:
    """Create a document for testing extractors."""
    doc = parse_document(html, url)
    body = doc.body
    if body is not None:
        return body
    return doc


def extract_frontmatter_url(html: str) -> Optional[str]:
    """Extract URL from HTML frontmatter comment."""
    match = re.search(r'<!--\s*(\{"url":.*?\})\s*-->', html)
    if match:
        try:
            data = json.loads(match.group(1))
            return data.get("url")
        except json.JSONDecodeError:
            pass
    return None


def load_fixture_file(name: str) -> Optional[str]:
    """Load a fixture HTML file by name."""
    fixture_path = Path(__file__).parent / "fixtures" / f"{name}.html"
    if fixture_path.exists():
        return fixture_path.read_text(encoding="utf-8")
    return None


def load_expected_file(name: str, extension: str = "md") -> Optional[str]:
    """Load an expected output file by name."""
    expected_path = Path(__file__).parent / "expected" / f"{name}.{extension}"
    if expected_path.exists():
        return expected_path.read_text(encoding="utf-8")
    return None


def get_transcript_panel_html() -> str:
    """Return HTML for a YouTube transcript panel."""
    return """
        <ytd-engagement-panel-section-list-renderer target-id="engagement-panel-searchable-transcript">
            <div id="segments-container">
                <ytd-transcript-segment-renderer>
                    <div class="segment-timestamp">0:00</div>
                    <div class="segment-text">Hello world.</div>
                </ytd-transcript-segment-renderer>
                <ytd-transcript-segment-renderer>
                    <div class="segment-timestamp">0:05</div>
                    <div class="segment-text">Second line.</div>
                </ytd-transcript-segment-renderer>
            </div>
            <div id="footer">
                <yt-sort-filter-sub-menu-renderer>
                    <yt-dropdown-menu>
                        <button>English (auto-generated)</button>
                    </yt-dropdown-menu>
                </yt-sort-filter-sub-menu-renderer>
            </div>
        </ytd-engagement-panel-section-list-renderer>
    """


def get_transcript_panel_html_without_language_button() -> str:
    """Return HTML for a YouTube transcript panel without language selector."""
    return """
        <ytd-engagement-panel-section-list-renderer target-id="engagement-panel-searchable-transcript">
            <div id="segments-container">
                <ytd-transcript-segment-renderer>
                    <div class="segment-timestamp">0:00</div>
                    <div class="segment-text">Hello world.</div>
                </ytd-transcript-segment-renderer>
            </div>
        </ytd-engagement-panel-section-list-renderer>
    """
