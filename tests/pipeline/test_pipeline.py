from __future__ import annotations

import warnings
from dataclasses import replace

import pytest

from domdown import CriteriaError, DomdownOptions, ExtractionCriteria, HtmlToMarkdownPipeline, html_to_markdown


def test_pipeline_declares_stages_in_execution_order() -> None:
    """The pipeline should keep stage ordering explicit and stable."""

    pipeline = HtmlToMarkdownPipeline()

    assert [stage.name for stage in pipeline.stages] == [
        "parse",
        "prepare",
        "metadata",
        "clean",
        "preserve",
        "markdown",
        "postprocess",
        "frontmatter",
    ]


def test_html_to_markdown_round_trip_uses_pipeline_output() -> None:
    """The public helper should return the rendered document string."""

    html = "<html><body><div class='articlebody'><p>Hello</p></div></body></html>"

    assert html_to_markdown(html, DomdownOptions(emit_frontmatter=False)) == "Hello"


def test_apply_include_exclude_and_unwrap() -> None:
    html = """
    <html><body>
      <article class="story"><div class="wrap"><p>Keep <b>this</b></p><div class="ad">Drop</div></div></article>
      <aside>Outside</aside>
    </body></html>
    """
    criteria = ExtractionCriteria(include=("article.story",), exclude=(".ad",), unwrap=(".wrap",))

    result = HtmlToMarkdownPipeline(DomdownOptions(emit_frontmatter=False)).run(html, criteria=criteria)

    assert "Keep **this**" in result.markdown
    assert "Drop" not in result.markdown
    assert "Outside" not in result.markdown


def test_apply_trace_records_selector_matches_changes_and_content_metrics() -> None:
    html = """
    <html><body><article class="story"><div class="wrap"><p>Keep useful words here.</p><div class="ad"><p>Drop this advert.</p></div></div></article></body></html>
    """
    criteria = ExtractionCriteria(
        include=("article.story",),
        exclude=(".ad", ".missing"),
        unwrap=(".wrap", ".none"),
    )

    result = HtmlToMarkdownPipeline(DomdownOptions(emit_frontmatter=False)).run(html, criteria=criteria)
    trace = result.trace.to_dict()
    decisions = trace["decisions"]

    assert trace["mode"] == "selector_apply"
    assert trace["criteria_source"] == "explicit"
    assert decisions[0] == {
        "action": "apply-criteria",
        "include": ["article.story"],
        "include_fallback": [],
        "min_words": 50,
        "exclude": [".ad", ".missing"],
        "unwrap": [".wrap", ".none"],
        "drop_text": [],
        "shared_cleanup": "auto",
    }
    include = next(item for item in decisions if item["action"] == "include")
    assert include["selector"] == "article.story" and include["matches"] == 1
    excludes = [item for item in decisions if item["action"] == "exclude"]
    assert excludes[0]["status"] == "applied" and excludes[0]["nodes_removed"] == 2
    assert excludes[1]["status"] == "no-matches" and excludes[1]["nodes_removed"] == 0
    unwraps = [item for item in decisions if item["action"] == "unwrap"]
    assert unwraps[0]["nodes_unwrapped"] == 1 and unwraps[0]["status"] == "applied"
    assert unwraps[1]["status"] == "no-matches"
    metrics = trace["content_metrics"]
    assert metrics["before"]["paragraphs"] == 2
    assert metrics["after"]["paragraphs"] == 1
    assert metrics["after"]["words"] < metrics["before"]["words"]
    assert metrics["word_retention"] is not None
    assert metrics["after"]["words"] == len(result.markdown.split())
    assert trace["warnings"] == ["Possible empty shell: include matched 1 elements but produced 4 words"]


def test_selector_apply_preserves_direct_text_and_removes_selected_elements() -> None:
    html = "<article>Item Page <span class='placeholder'>placeholder(#1)</span> Useful text <p>Keep this paragraph.</p></article>"
    result = HtmlToMarkdownPipeline(DomdownOptions(emit_frontmatter=False)).run(
        html,
        criteria=ExtractionCriteria(include=("article",), exclude=(".placeholder",)),
    )

    assert "Item Page" in result.markdown
    assert "Useful text" in result.markdown
    assert "Keep this paragraph." in result.markdown
    assert "placeholder(#1)" not in result.markdown


def test_selector_apply_uses_same_cleanup_as_discover_for_same_root() -> None:
    html = """
    <article>
      <div class="share-widget">Default removal selector stays.</div>
      <div class="caller-filter">Configured removal selector stays.</div>
      <section class="related-posts"><h2>Related stories</h2><p>Cleanup heuristic stays disabled.</p></section>
    </article>
    """
    options = DomdownOptions(emit_frontmatter=False, remove_selectors=(".caller-filter",))
    pipeline = HtmlToMarkdownPipeline(options)
    discovered = pipeline.run(html)
    result = pipeline.run(html, criteria=ExtractionCriteria(include=("article",)))

    assert result.markdown == discovered.markdown
    assert "Default removal selector stays." not in result.markdown
    assert "Configured removal selector stays." not in result.markdown


def test_legacy_soup_contains_selector_is_normalized_without_warning() -> None:
    html = '<div class="target">Find this text.</div><div>Other text.</div>'

    with warnings.catch_warnings(record=True) as observed:
        warnings.simplefilter("always")
        criteria = ExtractionCriteria(include=('div:contains("Find this")',))
        result = HtmlToMarkdownPipeline(DomdownOptions(emit_frontmatter=False)).run(html, criteria=criteria)

    assert result.markdown == "Find this text."
    assert result.criteria.include == criteria.include
    assert not any(":contains" in str(item.message) for item in observed)


def test_legacy_soup_contains_remove_selector_is_normalized_without_warning() -> None:
    html = "<article><p>Keep this paragraph.</p><div>Discard this block.</div></article>"
    options = DomdownOptions(
        emit_frontmatter=False,
        remove_selectors=('div:contains("Discard")',),
    )

    with warnings.catch_warnings(record=True) as observed:
        warnings.simplefilter("always")
        result = HtmlToMarkdownPipeline(options).run(html)

    assert "Keep this paragraph." in result.markdown
    assert "Discard this block." not in result.markdown
    assert not any(":contains" in str(item.message) for item in observed)


def test_contains_text_inside_attribute_value_is_not_rewritten() -> None:
    html = '<div data-note=":contains(target)">Attribute match.</div><div>Other.</div>'
    criteria = ExtractionCriteria(include=('div[data-note=":contains(target)"]',))

    result = HtmlToMarkdownPipeline(DomdownOptions(emit_frontmatter=False)).run(html, criteria=criteria)

    assert result.markdown == "Attribute match."


def test_selector_apply_multiple_includes_deduplicates_nested_matches_in_document_order() -> None:
    html = """
    <div class="outer"><p>First in document.</p><section class="inner"><p>Nested once.</p></section></div>
    <article class="later"><p>Last in document.</p></article>
    """
    result = HtmlToMarkdownPipeline(DomdownOptions(emit_frontmatter=False)).run(
        html,
        criteria=ExtractionCriteria(include=(".inner", ".later", ".outer")),
    )

    assert result.markdown.index("First in document.") < result.markdown.index("Nested once.")
    assert result.markdown.index("Nested once.") < result.markdown.index("Last in document.")
    assert result.markdown.count("Nested once.") == 1
    assert "data-domdown-criteria-root" not in result.markdown


def test_selector_apply_multiple_includes_collapses_sibling_roots_with_duplicate_text() -> None:
    article_text = " ".join(
        f"Section {index} explains a distinct security observation and its operational consequence."
        for index in range(1, 9)
    )
    html = f"""
    <div class="desktop-template"><article><h2>What we've done</h2><p>{article_text}</p></article></div>
    <section class="mobile-template"><div><h2>What we've done</h2><p>{article_text}</p></div></section>
    """

    result = HtmlToMarkdownPipeline(DomdownOptions(emit_frontmatter=False)).run(
        html,
        criteria=ExtractionCriteria(include=(".desktop-template", ".mobile-template")),
    )

    assert result.markdown.count("What we've done") == 1
    dedupe = next(item for item in result.trace.decisions if item["action"] == "dedupe-content")
    assert dedupe["nodes_removed"] == 1


def test_include_fallback_is_ordered_exclusive_and_stops_at_word_threshold() -> None:
    html = """
    <main>
      <section class="legacy"><p>Short legacy body.</p></section>
      <article class="current"><p>This is the current article body with enough useful words to meet the requested threshold.</p></article>
      <aside class="other"><p>This should not be appended as a union candidate.</p></aside>
    </main>
    """
    criteria = ExtractionCriteria(
        include_fallback=(".legacy", ".current", ".other"),
        min_words=8,
    )

    result = HtmlToMarkdownPipeline(DomdownOptions(emit_frontmatter=False)).run(html, criteria=criteria)

    assert "current article body" in result.markdown
    assert "legacy body" not in result.markdown
    assert "union candidate" not in result.markdown
    fallback_decisions = [item for item in result.trace.decisions if item["action"] == "include-fallback"]
    assert [item["status"] for item in fallback_decisions] == ["below-threshold", "selected"]


def test_include_fallback_uses_best_matched_candidate_when_none_meets_threshold() -> None:
    html = '<div class="short">One two.</div><div class="long">One two three four five.</div>'
    result = HtmlToMarkdownPipeline(DomdownOptions(emit_frontmatter=False)).run(
        html,
        criteria=ExtractionCriteria(include_fallback=(".short", ".long"), min_words=20),
    )

    assert result.markdown == "One two three four five."
    decisions = [item for item in result.trace.decisions if item["action"] == "include-fallback"]
    assert decisions[-1]["status"] == "selected-best-below-threshold"


def test_drop_text_removes_full_direct_text_nodes_and_preserves_mixed_prose() -> None:
    html = """
    <article class="selected">
      Author : Cursor Team
      <span>/.col</span>
      placeholder(#1)
      <p>Useful prose mentions Author : Cursor Team inside a sentence.</p>
    </article>
    """
    result = HtmlToMarkdownPipeline(DomdownOptions(emit_frontmatter=False)).run(
        html,
        criteria=ExtractionCriteria(
            include=("article.selected",),
            drop_text=(r"Author\s*:\s*Cursor Team", r"/\.col", r"placeholder\(#1\)"),
        ),
    )

    assert "Useful prose mentions Author : Cursor Team inside a sentence." in result.markdown
    assert "Author : Cursor Team" not in result.markdown.split("Useful prose")[0]
    assert "/.col" not in result.markdown
    assert "placeholder(#1)" not in result.markdown


def test_inline_anchor_toc_immediately_after_first_heading_is_removed() -> None:
    html = """
    <article>
      <h1>Report title</h1>
      <nav class="be-table-of-contents">
        <ul><li><a href="#one">One</a></li><li><a href="#two">Two</a></li><li><a href="#three">Three</a></li></ul>
      </nav>
      <h2 id="one">First section</h2><p>Retained article text.</p>
    </article>
    """
    result = HtmlToMarkdownPipeline(DomdownOptions(emit_frontmatter=False)).run(html)

    assert "Retained article text." in result.markdown
    assert result.markdown.count("[One](#one)") == 0
    assert "Table of Contents" not in result.markdown


def test_empty_shell_warning_covers_small_shells_without_flagging_tiny_sources() -> None:
    pipeline = HtmlToMarkdownPipeline(DomdownOptions(emit_frontmatter=False))
    shell = pipeline.run("<html><body>" + (" " * 700) + "</body></html>")
    tiny = pipeline.run("<html><body></body></html>")

    assert any("Possible empty shell" in warning for warning in shell.warnings)
    assert not any("Possible empty shell" in warning for warning in tiny.warnings)
    assert shell.trace.to_dict()["warnings"] == list(shell.warnings)


def test_selector_apply_warns_when_matched_include_renders_fewer_than_ten_words() -> None:
    html = '<html><body><article class="selected">One short phrase.</article>' + (" " * 700) + "</body></html>"
    result = HtmlToMarkdownPipeline(DomdownOptions(emit_frontmatter=False)).run(
        html,
        criteria=ExtractionCriteria(include=("article.selected",)),
    )

    assert result.markdown == "One short phrase."
    assert result.warnings == ("Possible empty shell: include matched 1 elements but produced 3 words",)


def test_selector_apply_does_not_apply_selectors_to_its_synthetic_root() -> None:
    html = '<div class="first"><p>First survives.</p></div><article><p>Second survives.</p></article>'
    pipeline = HtmlToMarkdownPipeline(DomdownOptions(emit_frontmatter=False))

    excluded = pipeline.run(
        html,
        criteria=ExtractionCriteria(include=(".first", "article"), exclude=("div",)),
    )
    unwrapped = pipeline.run(
        html,
        criteria=ExtractionCriteria(include=(".first", "article"), unwrap=("div",)),
    )

    assert "First survives." not in excluded.markdown
    assert "Second survives." in excluded.markdown
    assert "First survives." in unwrapped.markdown
    assert "Second survives." in unwrapped.markdown


def test_selector_apply_can_exclude_or_reject_unwrap_of_the_selected_root() -> None:
    pipeline = HtmlToMarkdownPipeline(DomdownOptions(emit_frontmatter=False))
    html = "<article class='story'><p>Content.</p></article>"

    excluded = pipeline.run(html, criteria=ExtractionCriteria(include=("article.story",), exclude=("article.story",)))
    assert excluded.markdown == ""
    assert next(item for item in excluded.trace.decisions if item["action"] == "exclude")["status"] == "root-excluded"

    with pytest.raises(CriteriaError, match="unwrap cannot target"):
        pipeline.run(html, criteria=ExtractionCriteria(include=("article.story",), unwrap=("article.story",)))


def test_selector_apply_accepts_soupsieve_has_and_escaped_special_class_selectors() -> None:
    html = '<div class="content:primary" data-kind="a:b"><p>Selected by <a href="https://example.com">link</a>.</p></div><aside>Outside.</aside>'
    criteria = ExtractionCriteria(include=('div.content\\:primary[data-kind="a:b"]:has(> p)',))

    result = HtmlToMarkdownPipeline(DomdownOptions(emit_frontmatter=False)).run(html, criteria=criteria)

    assert "Selected by [link](https://example.com)." in result.markdown
    assert "Outside." not in result.markdown


def test_selector_apply_matches_medium_site_criteria_without_adapter_postprocessing() -> None:
    html = """
    <html><head><meta property="og:site_name" content="Medium"></head><body>
      <article class="chosen"><p>Caller selected introduction.</p><h2>Selected heading</h2><p>Selected body.</p></article>
    </body></html>
    """
    pipeline = HtmlToMarkdownPipeline(DomdownOptions(emit_frontmatter=False))
    discovered = pipeline.run(html)
    result = pipeline.run(
        html,
        criteria=ExtractionCriteria(include=("article.chosen",)),
    )

    assert result.markdown == discovered.markdown
    assert "Caller selected introduction." in result.markdown
    assert "Selected heading" in result.markdown


def test_explicit_include_can_retain_heuristically_removed_editorial_content() -> None:
    html = """
    <html><body>
      <article class="articlebody">
        <p>Main article text.</p>
        <section class="related-posts"><h2>Related stories</h2><p>Editorially relevant section.</p></section>
      </article>
    </body></html>
    """

    pipeline = HtmlToMarkdownPipeline(DomdownOptions(emit_frontmatter=False))
    discovered = pipeline.run(html)
    result = pipeline.run(
        html,
        criteria={"schema_version": 1, "include": ["article"]},
    )

    assert result.markdown == discovered.markdown
    assert "Editorially relevant section." not in result.markdown


def test_apply_missing_include_is_an_error() -> None:
    with pytest.raises(CriteriaError, match="matched no elements"):
        HtmlToMarkdownPipeline().run("<p>text</p>", criteria={"schema_version": 1, "include": [".missing"]})


def test_unmatched_include_in_large_html_identifies_empty_shell_diagnosis() -> None:
    html = "<html><body>" + (" " * 700) + "</body></html>"

    with pytest.raises(CriteriaError, match="possible empty shell or stale selector"):
        HtmlToMarkdownPipeline().run(html, criteria={"schema_version": 1, "include": ["#__next"]})


def test_discovered_criteria_replay_exactly_after_json_round_trip() -> None:
    html = "<html><body><nav>Nav</nav><article class='articlebody'><p>Body</p><div class='related'>Related</div></article></body></html>"
    pipeline = HtmlToMarkdownPipeline(DomdownOptions(emit_frontmatter=False))

    discovered = pipeline.run(html)
    replayed = pipeline.run(html, criteria=ExtractionCriteria.from_json(discovered.criteria.to_json()))

    assert replayed.markdown == discovered.markdown
    assert discovered.criteria.generated
    assert discovered.trace.to_dict()["mode"] == "discover"
    assert replayed.trace.to_dict()["mode"] == "exact_replay"
    assert discovered.trace.to_dict()["criteria_source"] == "discover"
    assert replayed.trace.to_dict()["criteria_source"] == "discover"

    with pytest.raises(CriteriaError, match="same HTML"):
        pipeline.run(html + "<p>changed</p>", criteria=discovered.criteria)


def test_discovered_medium_site_criteria_replay_through_apply() -> None:
    html = """
    <html><head><meta property="og:site_name" content="Medium">
      <link rel="canonical" href="https://medium.com/story"></head><body>
      <nav>site navigation</nav>
      <article><h1>Story</h1><p>3 min read</p><p>Editorial body text survives.</p></article>
    </body></html>
    """
    pipeline = HtmlToMarkdownPipeline(DomdownOptions(emit_frontmatter=False))

    discovered = pipeline.run(html)
    replayed = pipeline.run(html, criteria=discovered.criteria.to_json())

    assert discovered.markdown == replayed.markdown
    assert "3 min read" not in discovered.markdown
    assert discovered.trace.to_dict()["criteria_source"] == "site"
    assert discovered.criteria.drop_text
    assert discovered.trace.adapters == ()


def test_manual_criteria_overrides_domain_adapter_removals() -> None:
    html = """
    <html><head><meta property="og:site_name" content="Medium"></head><body>
      <nav class="target">Navigation selected by caller</nav>
    </body></html>
    """

    result = HtmlToMarkdownPipeline(DomdownOptions(emit_frontmatter=False)).run(
        html,
        criteria={"schema_version": 1, "include": [".target"]},
    )

    assert "Navigation selected by caller" in result.markdown


def test_manual_criteria_overrides_github_preprocessing_removals() -> None:
    html = """
    <html><head>
      <meta property="og:site_name" content="GitHub">
      <meta property="og:url" content="https://github.com/acme/project/issues/1">
      <meta name="route-controller" content="issues">
    </head><body><nav class="caller-content">Caller selected this navigation content</nav></body></html>
    """

    result = HtmlToMarkdownPipeline(DomdownOptions(emit_frontmatter=False)).run(
        html,
        criteria={"schema_version": 1, "include": [".caller-content"]},
    )

    assert "Caller selected this navigation content" in result.markdown


def test_manual_criteria_can_select_github_embedded_blob_content() -> None:
    html = """
    <html><head>
      <meta property="og:site_name" content="GitHub">
      <meta property="og:url" content="https://github.com/acme/project/blob/main/example.py">
      <meta name="route-controller" content="blob">
    </head><body>
      <script data-target="react-app.embeddedData">
        {"payload":{"blob":{"rawLines":["print('criteria')"]}}}
      </script>
    </body></html>
    """

    result = HtmlToMarkdownPipeline(DomdownOptions(emit_frontmatter=False)).run(
        html,
        criteria={"schema_version": 1, "include": ["pre"]},
    )

    assert result.markdown == "print('criteria')"
    assert "print('criteria')" in result.markdown


def test_discovered_github_blob_criteria_replay_special_markdown_route() -> None:
    html = """
    <html><head>
      <meta property="og:site_name" content="GitHub">
      <meta property="og:url" content="https://github.com/acme/project/blob/main/example.py">
      <meta name="route-controller" content="blob">
    </head><body>
      <script data-target="react-app.embeddedData">
        {"payload":{"blob":{"rawLines":["print('replayed')"]}}}
      </script>
    </body></html>
    """
    pipeline = HtmlToMarkdownPipeline(DomdownOptions(emit_frontmatter=False))

    discovered = pipeline.run(html)
    replayed = pipeline.run(html, criteria=discovered.criteria.to_json())

    assert discovered.markdown == replayed.markdown
    assert discovered.trace.to_dict()["criteria_source"] == "site"
    assert "pre.domdown-raw-lines" in discovered.criteria.include[0]


def test_editing_discovered_include_switches_to_explicit_selection() -> None:
    html = """
    <html><body>
      <article class="articlebody"><p>Automatic article content.</p></article>
      <section id="manual"><p>Caller chosen content.</p></section>
    </body></html>
    """
    pipeline = HtmlToMarkdownPipeline(DomdownOptions(emit_frontmatter=False))
    discovered = pipeline.run(html)
    edited = replace(discovered.criteria, include=("#manual",))

    result = pipeline.run(html, criteria=edited)

    assert result.markdown == "Caller chosen content."


def test_criteria_rejects_invalid_selectors_and_schema_versions() -> None:
    with pytest.raises(CriteriaError, match="Invalid CSS selector"):
        ExtractionCriteria(include=("div[",))
    with pytest.raises(CriteriaError, match="schema_version"):
        ExtractionCriteria.from_json({"schema_version": 2, "include": [".content"]})


def test_schema_one_criteria_round_trips_fallback_and_drop_text() -> None:
    criteria = ExtractionCriteria(
        include_fallback=(".legacy", ".modern"),
        min_words=120,
        drop_text=(r"Author\s*:\s*Cursor Team",),
        shared_cleanup="force",
    )

    restored = ExtractionCriteria.from_json(criteria.to_json())

    assert restored == criteria
    assert restored.schema_version == 1


def test_shared_cleanup_can_be_forced_for_an_alternate_include_root() -> None:
    html = """
    <div class="selected">
      <p>Keep this selected paragraph with enough useful text to remain readable.</p>
      <footer><p>Copyright © 2026 Example. Back to Top</p></footer>
    </div>
    """
    result = HtmlToMarkdownPipeline(DomdownOptions(emit_frontmatter=False)).run(
        html,
        criteria=ExtractionCriteria(include=(".selected",), shared_cleanup="force"),
    )

    assert "Keep this selected paragraph" in result.markdown
    assert "Copyright" not in result.markdown
    assert "Back to Top" not in result.markdown
