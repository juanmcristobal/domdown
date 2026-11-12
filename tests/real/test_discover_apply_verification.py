"""End-to-end Discover/Apply checks against the checked-in raw HTML corpus."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from domdown import DomdownOptions, ExtractionCriteria, HtmlToMarkdownPipeline, html_to_markdown
from domdown.adapters import github

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
        monkeypatch.setattr(github, "_fetch_release_assets", lambda url: (_ for _ in ()).throw(OSError("network disabled")))

    case = CASES[case_id]
    html = case.html_text()
    options = DomdownOptions(base_url=case.base_url) if case.base_url else DomdownOptions()

    automatic = html_to_markdown(html, options=options)
    discovered = HtmlToMarkdownPipeline(options=options).run(html)
    criteria_json = discovered.criteria.to_json()
    criteria = ExtractionCriteria.from_json(criteria_json)
    criteria_roundtrip = ExtractionCriteria.from_json(criteria.to_json())
    applied_result = HtmlToMarkdownPipeline(options=options).run(html, criteria=criteria_roundtrip)
    public_applied = html_to_markdown(html, options=options, criteria=criteria_roundtrip)
    applied_repeat = HtmlToMarkdownPipeline(options=options).run(html, criteria=criteria_roundtrip)
    public_applied_repeat = html_to_markdown(html, options=options, criteria=criteria_roundtrip)

    assert automatic == discovered.document
    assert ExtractionCriteria.from_json(criteria_json).to_json() == criteria_json
    assert json.loads(criteria_json) == criteria_roundtrip.to_dict()

    observed_document_replay = automatic == applied_result.document
    observed_public_replay = automatic == public_applied
    observed_body_replay = discovered.markdown == applied_result.markdown
    observed_pipeline_apply_determinism = applied_result.document == applied_repeat.document
    observed_public_apply_determinism = public_applied == public_applied_repeat
    if discovered.criteria.replayable:
        assert observed_document_replay
        assert observed_public_replay
        assert observed_body_replay
        assert observed_pipeline_apply_determinism
        assert observed_public_apply_determinism
    else:
        record_property("non_replayable_document_match_observed", observed_document_replay)
        record_property("non_replayable_public_match_observed", observed_public_replay)
        record_property("non_replayable_body_match_observed", observed_body_replay)
        record_property("non_replayable_pipeline_apply_determinism_observed", observed_pipeline_apply_determinism)
        record_property("non_replayable_public_apply_determinism_observed", observed_public_apply_determinism)

    automatic_repeat = html_to_markdown(html, options=options)
    discovered_repeat = HtmlToMarkdownPipeline(options=options).run(html)
    assert automatic_repeat == automatic
    assert discovered_repeat.markdown == discovered.markdown
    assert discovered_repeat.criteria.to_json() == criteria_json
    assert discovered_repeat.trace.to_dict() == discovered.trace.to_dict()


@pytest.mark.parametrize("case_id", sorted(CASES))
def test_raw_discover_json_replay_is_exact(case_id: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """Every manifest raw must survive a public JSON serialization/replay round trip."""
    if case_id == "node_release_tag_v2530":
        monkeypatch.setattr(github, "_fetch_release_assets", lambda url: (_ for _ in ()).throw(OSError("network disabled")))
    case = CASES[case_id]
    pipeline = _pipeline(case_id)
    raw = case.html_text()
    first = pipeline.run(raw)
    second = pipeline.run(raw)
    restored = ExtractionCriteria.from_json(first.criteria.to_json())
    replay = pipeline.run(raw, criteria=restored)
    assert first.markdown == replay.markdown
    assert first.criteria.to_json() == second.criteria.to_json()
    assert first.trace.to_dict() == second.trace.to_dict()
    assert json.loads(first.criteria.to_json())["schema_version"] == 1
    parsed = BeautifulSoup(raw, "lxml")
    ids = {item["node_id"] for item in first.trace.node_references}
    assert all(item["node_id"] in ids for item in first.trace.node_references)
    assert all(1 <= node_id <= len(parsed.find_all(True)) for node_id in ids)
    assert len(json.dumps(first.trace.to_dict())) < len(raw)


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

    # D6: explicit empty exclusion list suppresses auto extraction filters.
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
def test_real_adapter_extraction_decisions_can_be_overridden(case_id: str, selector: str, marker: str) -> None:
    case = CASES[case_id]
    pipeline = _pipeline(case_id)
    normal = pipeline.run(case.html_text())
    assert normal.criteria.adapters
    forced = pipeline.run(case.html_text(), criteria=ExtractionCriteria(include=(selector,), exclude=()))
    assert marker in forced.markdown
    assert marker not in normal.markdown


def test_github_release_is_marked_non_replayable_without_frozen_external_resource(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(github, "_fetch_release_assets", lambda url: (_ for _ in ()).throw(OSError("network disabled")))
    case = CASES["node_release_tag_v2530"]
    result = _pipeline(case.id).run(case.html_text())
    assert not result.criteria.replayable
    assert any("fetched externally" in limitation for limitation in result.criteria.limitations)


def test_real_corpus_feature_coverage_and_securelist_absence() -> None:
    raw_paths = list((Path(__file__).parent / "html").glob("*.html"))
    assert len(raw_paths) == len(CASES) == 33
    corpus = "\n".join(path.read_text(encoding="utf-8") for path in raw_paths)
    soup = BeautifulSoup(corpus, "lxml")
    assert soup.find("table") is not None
    assert soup.find("pre") is not None
    assert soup.find("code") is not None
    assert soup.find("textarea") is not None
    assert soup.find("img") is not None
    assert "securelist-cloud-infrastructure-isolation-bypass" not in " ".join(path.name for path in raw_paths)
