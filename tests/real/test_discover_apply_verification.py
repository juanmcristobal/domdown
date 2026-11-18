"""End-to-end Discover/Apply checks against the checked-in raw HTML corpus."""

from __future__ import annotations

import json
import re
from dataclasses import replace
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from domdown import DomdownOptions, ExtractionCriteria, HtmlToMarkdownPipeline, html_to_markdown
from domdown.stages import prepare as github_preparation

from . import load_real_cases

CASES = {case.id: case for case in load_real_cases(layer=None)}


def _pipeline(case_id: str) -> HtmlToMarkdownPipeline:
    case = CASES[case_id]
    return HtmlToMarkdownPipeline(DomdownOptions(base_url=case.base_url) if case.base_url else DomdownOptions())


@pytest.mark.parametrize("case_id", sorted(CASES))
def test_real_raw_automatic_discover_apply_are_exactly_equivalent(
    case_id: str,
    monkeypatch: pytest.MonkeyPatch,
    record_property: pytest.RecordProperty,
) -> None:
    """Compare complete public documents separately from body-only Markdown fields."""
    if case_id == "node_release_tag_v2530":
        monkeypatch.setattr(
            github_preparation, "_fetch_release_assets", lambda url: (_ for _ in ()).throw(OSError("network disabled"))
        )

    case = CASES[case_id]
    html = case.html_text()
    options = DomdownOptions(base_url=case.base_url) if case.base_url else DomdownOptions()

    automatic = html_to_markdown(html, options=options)
    discovered = HtmlToMarkdownPipeline(options=options).run(html)
    criteria_json = discovered.criteria.to_json()
    criteria_roundtrip = ExtractionCriteria.from_json(criteria_json)
    applied_result = HtmlToMarkdownPipeline(options=options).run(html, criteria=criteria_roundtrip)
    public_applied = html_to_markdown(html, options=options, criteria=criteria_roundtrip)
    applied_repeat = HtmlToMarkdownPipeline(options=options).run(html, criteria=criteria_roundtrip)

    assert automatic == discovered.document
    assert criteria_roundtrip.to_json() == criteria_json
    assert json.loads(criteria_json) == criteria_roundtrip.to_dict()

    observed_document_replay = automatic == applied_result.document
    observed_public_replay = automatic == public_applied
    observed_body_replay = discovered.markdown == applied_result.markdown
    observed_apply_determinism = applied_result.document == applied_repeat.document
    if discovered.criteria.replayable:
        assert observed_document_replay
        assert observed_public_replay
        assert observed_body_replay
        assert observed_apply_determinism
    else:
        record_property("non_replayable_document_match_observed", observed_document_replay)
        record_property("non_replayable_public_match_observed", observed_public_replay)
        record_property("non_replayable_body_match_observed", observed_body_replay)
        record_property("non_replayable_apply_determinism_observed", observed_apply_determinism)

    discovered_repeat = HtmlToMarkdownPipeline(options=options).run(html)
    assert discovered_repeat.markdown == discovered.markdown
    assert discovered_repeat.criteria.to_json() == criteria_json
    assert discovered_repeat.trace.to_dict() == discovered.trace.to_dict()


@pytest.mark.parametrize("case_id", sorted(CASES))
def test_raw_discover_json_replay_is_exact(case_id: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """Every manifest raw must survive a public JSON serialization/replay round trip."""
    if case_id == "node_release_tag_v2530":
        monkeypatch.setattr(
            github_preparation, "_fetch_release_assets", lambda url: (_ for _ in ()).throw(OSError("network disabled"))
        )
    case = CASES[case_id]
    pipeline = _pipeline(case_id)
    raw = case.html_text()
    first = pipeline.run(raw)
    second = pipeline.run(raw)
    criteria_json = first.criteria.to_json()
    restored = ExtractionCriteria.from_json(criteria_json)
    replay = pipeline.run(raw, criteria=restored)
    first_trace = first.trace.to_dict()
    second_trace = second.trace.to_dict()
    assert first.markdown == replay.markdown
    assert criteria_json == second.criteria.to_json()
    assert first_trace == second_trace
    assert json.loads(criteria_json)["schema_version"] == 1
    parsed = BeautifulSoup(raw, "lxml")
    ids = {item["node_id"] for item in first.trace.node_references}
    assert len(ids) == len(first.trace.node_references)
    assert all(1 <= node_id <= len(parsed.find_all(True)) for node_id in ids)
    assert len(json.dumps(first_trace)) < len(raw)


def test_bleepingcomputer_patch_tuesday_keeps_vulnerability_catalog() -> None:
    """A large link-dense CVE table must not make the comments win root selection."""
    case = CASES["bleepingcomputer_november_2026_patch_tuesday"]
    pipeline = _pipeline(case.id)
    result = pipeline.run(case.html_text())

    cleaned = BeautifulSoup(result.cleaned_html, "lxml")
    assert result.criteria.include == (".article_section", "h1", "div.articleBody", "article.articleBody")
    assert cleaned.select_one(".articleBody") is not None
    assert len(cleaned.select(".articleBody tr")) >= 1300
    assert "1,235 flaws" in result.document
    assert "CVE-2026-124194" in result.document
    assert "jmwoods" not in result.document
    assert "ZeroYourHero" not in result.document


def test_bushido_popular_post_previews_are_not_collapsed_to_read_more_links() -> None:
    """Heading-bearing article cards must retain their available preview text."""
    case = CASES["bushidotoken_blackbasta_leaks_lessons_from_ascension"]
    result = _pipeline(case.id).run(case.html_text())

    assert "Feedback from the infosec community about these projects" in result.markdown
    assert "Logo credit: RedCanary" in result.markdown
    assert "Who is RansomHub?" in result.markdown


def test_unit42_clickfix_apply_preserves_nested_article_sections() -> None:
    """Applying the real article root must not flatten its heading-led body into card links."""
    case = CASES["unit42_preventing_clickfix_attack_vector"]
    result = _pipeline(case.id).run(
        case.html_text(),
        criteria=ExtractionCriteria(include=("section.blog-contents",)),
    )

    assert "## Executive Summary" in result.markdown
    assert "### NetSupport RAT Switches Up Its Loading" in result.markdown
    assert "## Hunting for ClickFix Infections" in result.markdown
    assert "msvcp140.dll" in result.markdown
    assert len(result.markdown.split()) > 2_000


def test_safedep_discover_preserves_shiki_code_blocks() -> None:
    case = CASES["safedep_malicious_ixpresso_core_npm_rat"]
    result = _pipeline(case.id).run(case.html_text())

    assert result.markdown.count("```") == 10
    assert result.trace.content_metrics["after"]["code_blocks"] == 5


def test_chainstack_incident_post_ignores_header_menu_and_related_articles() -> None:
    """A large header menu must not outscore the editorial article body."""
    case = CASES["chainstack_security_incident_nov_2026"]
    result = _pipeline(case.id).run(case.html_text())

    assert "Chainstack is committed to the security of our platform" in result.markdown
    assert "An external attacker gained unauthorized access" in result.markdown
    assert "Rotate the node credentials" in result.markdown
    assert "Log in" not in result.document
    assert "Smart contract Frameworks – Foundry vs Hardhat" not in result.document
    assert "UniWhales" not in result.document


def test_oracle_cpun_table_keeps_product_columns_and_cves() -> None:
    """Wrapped Oracle tables must stay tables instead of becoming definition lists."""
    case = CASES["oracle_cpu_october_2026"]
    raw = case.html_text()
    result = _pipeline(case.id).run(raw)
    cleaned = BeautifulSoup(result.cleaned_html, "lxml")

    assert len(cleaned.find_all("table")) == 35
    assert len(cleaned.find_all("tr")) == 1495
    assert sum(line.startswith("|") for line in result.markdown.splitlines()) == 1530
    assert "| Affected Products and Versions | Patch Availability Document |" in result.markdown
    assert "[Helidon](https://support.oracle.com/support/?documentId=CPU375)" in result.markdown
    assert '<a href="https://support.oracle.com/support/?documentId=CPU375">' not in result.markdown
    assert len(re.findall(r"CVE-\d{4}-\d+", result.markdown)) == len(re.findall(r"CVE-\d{4}-\d+", raw))


def test_real_socket_criteria_edits_remove_restore_change_root_unwrap_and_replace() -> None:
    case = CASES["socket_jscrambler_supply_chain_attack"]
    html = case.html_text()
    pipeline = _pipeline(case.id)
    discovered = pipeline.run(html)
    assert "compromised release" in discovered.markdown.lower()
    assert "Subscribe to our newsletter" not in discovered.markdown

    # D1/D4: a partial edit invalidates recorded node replay and removes only the named block.
    edited = replace(discovered.criteria, exclude=(".dek",))
    without_dek = pipeline.run(html, criteria=edited)
    assert "A compromised jscrambler npm release added a malicious preinstall hook" not in without_dek.markdown
    assert "compromised release of the popular" in without_dek.markdown.lower()

    # D2: select real editorial content outside the automatic root.
    newsletter = pipeline.run(html, criteria=ExtractionCriteria(include=(".newsletter",)))
    assert "Subscribe to our newsletter" in newsletter.markdown
    assert "Get notified when we publish new security blog posts" in newsletter.markdown

    # D3: explicit root replaces the automatic article root.
    changed_root = pipeline.run(html, criteria=ExtractionCriteria(include=(".article-body",)))
    assert "compromised release" in changed_root.markdown.lower()
    assert "jscrambler npm Package Compromised" not in changed_root.markdown

    # D5: unwrap retains the children and reading order without duplicating text.
    unwrapped = pipeline.run(html, criteria=ExtractionCriteria(include=("article",), unwrap=(".article-body",)))
    assert "compromised release" in unwrapped.markdown.lower()
    assert "article-body" not in unwrapped.cleaned_html
    assert unwrapped.markdown.count("compromised release") == 1

    # D6: a broader explicit root retains content outside Discover's root.
    all_body = pipeline.run(html, criteria=ExtractionCriteria(include=("body",), exclude=()))
    assert "Subscribe to our newsletter" in all_body.markdown
    assert "More security research from Socket" in all_body.markdown


@pytest.mark.parametrize(
    ("case_id", "selector", "marker"),
    [
        ("github_issue_security_timeline", ".js-repo-nav", "Issues 1.3k"),
        ("arxiv_2603_28627", "div.extra-services", "Access Paper"),
        ("wikipedia_elliptic_curve_cryptography", ".hatnote", "Further information"),
        ("cybersecuritynews_azure_password_spray_attack", ".td-post-sharing", "Copy URL"),
    ],
)
def test_real_extraction_decisions_can_be_overridden(case_id: str, selector: str, marker: str) -> None:
    case = CASES[case_id]
    pipeline = _pipeline(case_id)
    normal = pipeline.run(case.html_text())
    if case_id in {
        "wikipedia_elliptic_curve_cryptography",
        "cybersecuritynews_azure_password_spray_attack",
        "bleepingcomputer_november_2026_patch_tuesday",
        "dailysecu_sparrow_enterprise_procurement",
        "arxiv_2603_28627",
    }:
        assert normal.trace.to_dict()["criteria_source"] == "site"
    else:
        assert normal.trace.to_dict()["criteria_source"] == "site"
    forced = pipeline.run(case.html_text(), criteria=ExtractionCriteria(include=(selector,), exclude=()))
    assert marker in forced.markdown
    assert marker not in normal.markdown


def test_github_release_is_marked_non_replayable_without_frozen_external_resource(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        github_preparation,
        "_fetch_release_assets",
        lambda url: (_ for _ in ()).throw(OSError("network disabled")),
    )
    case = CASES["node_release_tag_v2530"]
    result = _pipeline(case.id).run(case.html_text())
    assert not result.criteria.replayable
    assert any("external" in limitation.lower() for limitation in result.criteria.limitations)


def test_github_release_replay_refetches_assets_before_apply(monkeypatch: pytest.MonkeyPatch) -> None:
    """Replay uses the same preparation stage and retains available remote assets."""

    calls: list[str] = []

    def fetch(url: str) -> str:
        calls.append(url)
        return '<ul><li><a href="/example/project/archive/refs/tags/v1.zip">Source code</a></li></ul>'

    monkeypatch.setattr(github_preparation, "_fetch_release_assets", fetch)
    case = CASES["node_release_tag_v2530"]
    pipeline = _pipeline(case.id)
    html = case.html_text()

    discovered = pipeline.run(html)
    replayed = pipeline.run(html, criteria=ExtractionCriteria.from_json(discovered.criteria.to_json()))

    assert len(calls) == 2
    assert discovered.document == replayed.document
    assert "### Assets" in replayed.markdown
    assert "https://github.com/example/project/archive/refs/tags/v1.zip" in replayed.markdown
    assert any("external" in limitation.lower() for limitation in discovered.criteria.limitations)


def test_real_corpus_feature_coverage_and_securelist_absence() -> None:
    raw_paths = list((Path(__file__).parent / "html").glob("*.html"))
    assert len(raw_paths) == len(CASES) == 37

    feature_cases = {
        "table": "oracle_cpu_october_2026",
        "pre": "adnanthekhan_clinejection",
        "code": "socket_jscrambler_supply_chain_attack",
        "textarea": "github_issue_security_timeline",
        "img": "bleepingcomputer_november_2026_patch_tuesday",
    }
    for element, case_id in feature_cases.items():
        soup = BeautifulSoup(CASES[case_id].html_text(), "lxml")
        assert soup.find(element) is not None

    assert "securelist-cloud-infrastructure-isolation-bypass" not in " ".join(path.name for path in raw_paths)
