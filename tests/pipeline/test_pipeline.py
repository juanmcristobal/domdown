from __future__ import annotations

from dataclasses import replace

import pytest

from domdown import CriteriaError, DomdownOptions, ExtractionCriteria, HtmlToMarkdownPipeline, html_to_markdown


def test_pipeline_declares_stages_in_execution_order() -> None:
    """The pipeline should keep stage ordering explicit and stable."""

    pipeline = HtmlToMarkdownPipeline()

    assert [stage.name for stage in pipeline.stages] == [
        "parse",
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


def test_explicit_include_can_retain_heuristically_removed_editorial_content() -> None:
    html = """
    <html><body>
      <article class="articlebody">
        <p>Main article text.</p>
        <section class="related-posts"><h2>Related stories</h2><p>Editorially relevant section.</p></section>
      </article>
    </body></html>
    """

    result = HtmlToMarkdownPipeline(DomdownOptions(emit_frontmatter=False)).run(
        html,
        criteria={"schema_version": 1, "include": ["article"]},
    )

    assert "Editorially relevant section." in result.markdown


def test_apply_missing_include_is_an_error() -> None:
    with pytest.raises(CriteriaError, match="matched no elements"):
        HtmlToMarkdownPipeline().run("<p>text</p>", criteria={"schema_version": 1, "include": [".missing"]})


def test_discovered_criteria_replay_exactly_after_json_round_trip() -> None:
    html = "<html><body><nav>Nav</nav><article class='articlebody'><p>Body</p><div class='related'>Related</div></article></body></html>"
    pipeline = HtmlToMarkdownPipeline(DomdownOptions(emit_frontmatter=False))

    discovered = pipeline.run(html)
    replayed = pipeline.run(html, criteria=ExtractionCriteria.from_json(discovered.criteria.to_json()))

    assert replayed.markdown == discovered.markdown
    assert discovered.criteria.generated

    with pytest.raises(CriteriaError, match="same HTML"):
        pipeline.run(html + "<p>changed</p>", criteria=discovered.criteria)


def test_discovered_medium_criteria_replay_after_adapter_preprocessing() -> None:
    html = """
    <html><head><meta property="og:site_name" content="Medium"></head><body>
      <nav>site navigation</nav>
      <article><h1>Story</h1><p>Editorial body text survives.</p></article>
    </body></html>
    """
    pipeline = HtmlToMarkdownPipeline(DomdownOptions(emit_frontmatter=False))

    discovered = pipeline.run(html)
    replayed = pipeline.run(html, criteria=discovered.criteria.to_json())

    assert discovered.markdown == replayed.markdown
    assert any(adapter["name"] == "medium" for adapter in discovered.trace.adapters)


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
    assert any(adapter["name"] == "github" for adapter in discovered.trace.adapters)


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
