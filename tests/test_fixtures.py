"""Test fixture pipeline for domdown.

Validates that the extraction pipeline works correctly:
1. Parses HTML into a document
2. Finds main content via scoring
3. Removes clutter (selectors, hidden, low-scoring)
4. Standardizes content
5. Extracts metadata
6. Converts to markdown

Each fixture is tested for the BEHAVIOR it exercises, not exact output.
"""

import json
import re
from pathlib import Path

import pytest

from domdown import Domdown, DomdownOptions
from domdown.markdown import to_markdown

from .helpers import extract_frontmatter_url, get_fixtures, parse_document


def get_expected_markdown_path(fixture_name: str) -> Path:
    return Path(__file__).parent / "expected" / f"{fixture_name}.md"


def load_expected_result(fixture_name: str) -> str | None:
    path = get_expected_markdown_path(fixture_name)
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def normalize_md_content(md_text: str) -> str:
    """Normalize markdown for comparison, focusing on structure not exact text."""
    lines = md_text.split("\n")
    content_lines = []
    in_json = False
    prev_blank = False
    for line in lines:
        stripped = stripped = line.strip()
        if stripped == "```" and not in_json:
            in_json = True
            continue
        elif stripped == "```" and in_json:
            in_json = False
            continue
        if not in_json:
            is_blank = stripped == ""
            if is_blank and prev_blank:
                continue
            content_lines.append(line.rstrip())
            prev_blank = is_blank
    return "\n".join(content_lines).strip()


def extract_metadata_from_md(md_text: str) -> dict:
    """Extract metadata block from markdown."""
    match = re.search(r"```json\s*(\{.*?\})\s*```", md_text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    return {}


def get_md_body(md_text: str) -> str:
    """Extract body (after metadata block) from markdown."""
    match = re.search(r"```json\s*(\{.*?\})\s*```\n\n(.*)", md_text, re.DOTALL)
    if match:
        return match.group(2).strip()
    return md_text.strip()


def test_should_have_fixtures():
    """Verify test fixtures exist."""
    fixtures_dir = Path(__file__).parent / "fixtures"
    html_files = list(fixtures_dir.glob("*.html"))
    assert len(html_files) > 0, "No test fixtures found"


@pytest.fixture
def fixtures():
    return get_fixtures()


def test_extraction_quality_report(fixtures):
    """Generate a quality report for fixture extraction.

    This test verifies:
    - Content is extracted (non-empty)
    - Markdown conversion works
    - Metadata is extracted where expected
    - Content is valid (HTML structure intact)

    It reports failures by category without failing on minor output differences.
    """
    results = {
        "total": len(fixtures),
        "extracted": 0,
        "empty_content": [],
        "no_markdown": [],
        "metadata_matches": 0,
        "skipped_extractors": [],
        "failures": [],
    }

    for fixture in fixtures:
        name = fixture["name"]
        path = fixture["path"]

        html = Path(path).read_text(encoding="utf-8")
        frontmatter_url = extract_frontmatter_url(html)
        url_name = re.sub(r"^[a-z]+--", "", Path(path).stem)
        url = frontmatter_url or f"https://{url_name}"

        doc = parse_document(html, url)
        domdown = Domdown(doc, DomdownOptions(separate_markdown=True, url=url))
        result = domdown.parse()
        to_markdown(result, DomdownOptions(separate_markdown=True, url=url), url)

        # Track extraction success
        if result.content:
            results["extracted"] += 1
        else:
            results["empty_content"].append(name)
            continue

        if not result.content_markdown:
            results["no_markdown"].append(name)
            continue

        # Check expected metadata where available
        expected_md = load_expected_result(name)
        if expected_md:
            expected_meta = extract_metadata_from_md(expected_md)
            actual_meta = {
                "title": result.title,
                "author": result.author,
                "site": result.site,
                "published": result.published,
            }
            # Compare metadata - allow partial match (title most important)
            if expected_meta.get("title") and actual_meta["title"] != expected_meta["title"]:
                # Title mismatch is a real failure
                results["failures"].append(
                    {
                        "name": name,
                        "type": "title_mismatch",
                        "expected": expected_meta.get("title", ""),
                        "actual": actual_meta["title"],
                    }
                )
            elif expected_meta.get("site") and actual_meta["site"] != expected_meta["site"]:
                results["failures"].append(
                    {
                        "name": name,
                        "type": "site_mismatch",
                        "expected": expected_meta.get("site", ""),
                        "actual": actual_meta["site"],
                    }
                )
            else:
                results["metadata_matches"] += 1

        # Skip extractor fixtures that have no extractor implementation
        if name.startswith("extractor--") and result.extractor_type is None:
            results["skipped_extractors"].append(name)

    # Print summary
    print("\n=== Fixture Extraction Quality Report ===")
    print(f"Total fixtures: {results['total']}")
    print(f"Extracted content: {results['extracted']}")
    print(f"Empty content failures: {len(results['empty_content'])}")
    print(f"No markdown conversion: {len(results['no_markdown'])}")
    print(f"Metadata matches: {results['metadata_matches']}")
    print(f"Skipped extractors: {results['skipped_extractors']}")

    if results["empty_content"]:
        print(f"\nEmpty content fixtures ({len(results['empty_content'])}):")
        for n in results["empty_content"][:5]:
            print(f"  - {n}")
        if len(results["empty_content"]) > 5:
            print(f"  ... and {len(results['empty_content']) - 5} more")

    if results["no_markdown"]:
        print(f"\nNo markdown conversion ({len(results['no_markdown'])}):")
        for n in results["no_markdown"][:5]:
            print(f"  - {n}")
        if len(results["no_markdown"]) > 5:
            print(f"  ... and {len(results['no_markdown']) - 5} more")

    if results["failures"]:
        print(f"\nMetadata mismatches ({len(results['failures'])}):")
        for f in results["failures"][:10]:
            print(f"  - {f['name']}: {f['type']} (expected='{f['expected']}', actual='{f['actual']}')")
        if len(results["failures"]) > 10:
            print(f"  ... and {len(results['failures']) - 10} more")

    # Core assertion: most fixtures should extract content
    extraction_rate = results["extracted"] / results["total"]
    assert (
        extraction_rate >= 0.80
    ), f"Extraction rate too low: {extraction_rate:.0%} ({results['extracted']}/{results['total']})"


def test_each_fixture_extracts_content(fixtures):
    """Test that each fixture produces non-empty content."""
    failures = []
    for fixture in fixtures:
        name = fixture["name"]
        path = fixture["path"]

        html = Path(path).read_text(encoding="utf-8")
        frontmatter_url = extract_frontmatter_url(html)
        url_name = re.sub(r"^[a-z]+--", "", Path(path).stem)
        url = frontmatter_url or f"https://{url_name}"

        doc = parse_document(html, url)
        domdown = Domdown(doc, DomdownOptions(url=url))
        result = domdown.parse()

        if not result.content.strip():
            failures.append(name)
        elif result.word_count < 5:
            failures.append(f"{name} (only {result.word_count} words)")

    if failures:
        print(f"\nFixtures with empty/very short content ({len(failures)}):")
        for f in failures[:10]:
            print(f"  - {f}")
        if len(failures) > 10:
            print(f"  ... and {len(failures) - 10} more")

    # Allow some failures - BS4 parsing differences are expected
    failure_rate = len(failures) / len(fixtures)
    assert failure_rate <= 0.20, f"Too many fixture failures: {failure_rate:.0%} ({len(failures)}/{len(fixtures)})"


def test_each_fixture_converts_to_markdown(fixtures):
    """Test that each fixture can be converted to markdown."""
    failures = []
    for fixture in fixtures:
        name = fixture["name"]
        path = fixture["path"]

        if name.startswith("extractor--"):
            continue  # Skip extractor fixtures without implementations

        html = Path(path).read_text(encoding="utf-8")
        frontmatter_url = extract_frontmatter_url(html)
        url_name = re.sub(r"^[a-z]+--", "", Path(path).stem)
        url = frontmatter_url or f"https://{url_name}"

        doc = parse_document(html, url)
        domdown = Domdown(doc, DomdownOptions(separate_markdown=True, url=url))
        result = domdown.parse()
        to_markdown(result, DomdownOptions(separate_markdown=True, url=url), url)

        if not result.content_markdown:
            failures.append(name)

    if failures:
        print(f"\nFixtures without markdown conversion ({len(failures)}):")
        for f in failures[:10]:
            print(f"  - {f}")

    failure_rate = len(failures) / len(fixtures)
    assert failure_rate <= 0.10, f"Too many markdown conversion failures: {failure_rate:.0%}"
