"""Performance tests for domdown.

These tests measure DOM parsing time and Domdown parsing time per fixture.
They are informational - no assertions are made on specific timings.
"""

import time
from typing import Optional

import pytest
from bs4 import BeautifulSoup

from domdown.domdown import Domdown
from domdown.types import DomdownOptions

from .helpers import get_fixtures


def parse_document(html: str, url: Optional[str] = None) -> BeautifulSoup:
    """Parse HTML into a BeautifulSoup document."""
    soup = BeautifulSoup(html, "lxml")
    if url and hasattr(soup, "URL"):
        soup.URL = url
    return soup


class TestPerformance:
    """Performance measurement tests."""

    @pytest.fixture
    def fixtures(self):
        """Return list of test fixtures."""
        return get_fixtures()

    def test_parse_time_per_fixture(self, fixtures, capsys):
        """Measure parse time per fixture including DOM parsing.

        This test is informational - it collects and reports timing data
        but does not assert on specific performance requirements.
        """
        results = []

        for fixture in fixtures:
            html = fixture["path"].read_text(encoding="utf-8")
            name = fixture["name"]

            url = "https://" + name.replace("--", "/").replace(".html", "")

            total_start = time.perf_counter()

            dom_start = time.perf_counter()
            doc = parse_document(html, url)
            dom_time = (time.perf_counter() - dom_start) * 1000

            domdown_start = time.perf_counter()
            options = DomdownOptions(url=url, profile=True)
            domdown = Domdown(doc, options)
            result = domdown.parse()
            domdown_time = (time.perf_counter() - domdown_start) * 1000

            total_time = (time.perf_counter() - total_start) * 1000

            results.append(
                {
                    "name": name,
                    "parse_time": round(domdown_time, 2),
                    "dom_time": round(dom_time, 2),
                    "total_time": round(total_time, 2),
                    "size": len(html),
                    "profile": result.profile or {},
                }
            )

        results.sort(key=lambda r: r["total_time"], reverse=True)

        capsys.readouterr()
        print("\n=== Performance Breakdown (ms) ===")
        print("  Total    DOM  Parse  Size    Fixture")
        print("  -----  -----  -----  -----   -------")
        for r in results:
            size_kb = r["size"] / 1024
            print(
                f"  {r['total_time']:>5.1f}  {r['dom_time']:>5.1f}  "
                f"{r['parse_time']:>5.1f}  {size_kb:>5.0f}KB  {r['name']}"
            )

        total_parse = sum(r["parse_time"] for r in results)
        total_dom = sum(r["dom_time"] for r in results)
        total_all = sum(r["total_time"] for r in results)
        print(
            f"\n  Total:  {total_all:.1f}ms (DOM: {total_dom:.1f}ms, Parse: {total_parse:.1f}ms)  Count: {len(results)}"
        )
        if total_all > 0:
            print(f"  DOM is {(total_dom / total_all) * 100:.0f}% of total time")

        step_totals = {}
        for r in results:
            for step, ms in r["profile"].items():
                step_totals[step] = step_totals.get(step, 0) + ms

        steps = sorted(step_totals.items(), key=lambda x: x[1], reverse=True)
        profile_total = sum(ms for _, ms in steps)

        print("\n=== Per-Step Totals (across all fixtures) ===")
        print("    ms    %   Step")
        print("  ----  ---   ----")
        for step, ms in steps:
            pct = (ms / profile_total * 100) if profile_total > 0 else 0
            print(f"  {ms:>4.0f}  {pct:>3.0f}%  {step}")
        print(f"  {profile_total:>4.0f}       total")

        assert len(results) > 0, "Should have processed at least one fixture"

    def test_profile_data_collected(self, fixtures):
        """Test that profile data is collected when profile=True."""
        if not fixtures:
            pytest.skip("No fixtures available")

        fixture = fixtures[0]
        html = fixture["path"].read_text(encoding="utf-8")
        doc = parse_document(html)
        options = DomdownOptions(profile=True)
        domdown = Domdown(doc, options)
        result = domdown.parse()

        assert result.profile is not None
        assert isinstance(result.profile, dict)
