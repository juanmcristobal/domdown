from __future__ import annotations

from bs4 import BeautifulSoup
import pytest

from domdown import CriteriaError, ExtractionCriteria, HtmlToMarkdownPipeline, SITE_CRITERIA
from domdown.site_criteria import criteria_for_document
from tests.real import load_real_cases


def test_site_registry_uses_only_supported_rule_fields() -> None:
    assert set(SITE_CRITERIA) == {
        "wikipedia", "the_register", "cyberscoop", "dark_reading",
        "securityweek", "security_affairs", "wiz", "railway", "gbhackers",
        "the_hacker_news", "cybersecurity_news", "bleepingcomputer", "dailysecu",
        "arxiv", "medium", "github",
    }
    for rules in SITE_CRITERIA.values():
        assert isinstance(rules, list) and rules
        for rule in rules:
            assert {"match", "include", "exclude", "unwrap"} <= set(rule)
            assert set(rule) <= {"match", "include", "exclude", "unwrap", "drop_text"}


def test_github_has_ordered_declarative_variant_rules() -> None:
    rules = SITE_CRITERIA["github"]
    assert len(rules) == 5
    assert [rule["match"].get("url") for rule in rules[:4]] == [
        r"/blob/", r"/issues/", r"/releases/tag/", r"/security/advisories"
    ]
    assert rules[-1]["match"] == {"site_name": "GitHub"}


@pytest.mark.parametrize(
    ("host", "selector"),
    [
        ("https://medium.com/story", "article"),
    ],
)
def test_medium_site_selector_rule_is_available(host: str, selector: str) -> None:
    document = BeautifulSoup(f'<link rel="canonical" href="{host}">', "lxml")
    criteria = criteria_for_document(document)
    assert criteria is not None
    assert selector in criteria.include


def test_medium_site_name_matches_custom_publication_hostname() -> None:
    document = BeautifulSoup(
        '<meta property="og:site_name" content="Medium"><meta property="og:url" content="https://publication.example/post">',
        "lxml",
    )
    assert criteria_for_document(document) is not None
    assert criteria_for_document(document).include == ("article",)


def test_wikipedia_site_criteria_reproduce_real_discovery_and_are_portable() -> None:
    case = next(case for case in load_real_cases(None) if case.id == "wikipedia_elliptic_curve_cryptography")
    pipeline = HtmlToMarkdownPipeline()

    discovered = pipeline.run(case.html_text())
    replayed = pipeline.run(case.html_text(), criteria=ExtractionCriteria.from_json(discovered.criteria.to_json()))

    assert discovered.trace.to_dict()["criteria_source"] == "site"
    assert discovered.trace.to_dict()["mode"] == "selector_apply"
    assert discovered.criteria.include == ("#mw-content-text",)
    assert discovered.criteria.generated is True
    assert discovered.markdown == replayed.markdown
    assert discovered.document == replayed.document == case.markdown_text()
    assert replayed.trace.to_dict()["criteria_source"] == "site"
    assert replayed.trace.to_dict()["mode"] == "exact_replay"
    with pytest.raises(CriteriaError, match="same HTML"):
        pipeline.run(case.html_text() + "<p>changed</p>", criteria=discovered.criteria)


def test_wikipedia_site_selectors_apply_to_a_second_document() -> None:
    data = SITE_CRITERIA["wikipedia"][0]
    criteria = ExtractionCriteria(
        include=tuple(data["include"]),
        exclude=tuple(data["exclude"]),
        unwrap=tuple(data["unwrap"]),
    )
    html = """<html><head><link rel="canonical" href="https://en.wikipedia.org/wiki/Other"></head>
    <body><main id="mw-content-text"><aside>Navigation</aside><p>Different article body.</p></main></body></html>"""

    result = HtmlToMarkdownPipeline().run(html, criteria=criteria)
    assert "Different article body." in result.markdown
    assert "Navigation" not in result.markdown


def test_site_criteria_use_canonical_host_and_do_not_override_explicit_criteria() -> None:
    document = BeautifulSoup(
        '<link rel="canonical" href="https://en.wikipedia.org/wiki/Test">', "lxml"
    )
    criteria = criteria_for_document(document)
    assert criteria is not None
    assert criteria.include == ("#mw-content-text",)
    assert criteria.exclude == tuple(SITE_CRITERIA["wikipedia"][0]["exclude"])

    html = """<html><head><link rel="canonical" href="https://en.wikipedia.org/wiki/Test"></head>
    <body><main id="mw-content-text"><article id="explicit"><p>Explicit selected content.</p></article>
    <p>Site selected content.</p></main></body></html>"""
    result = HtmlToMarkdownPipeline().run(html, criteria=ExtractionCriteria(include=("#explicit",)))
    assert result.trace.to_dict()["criteria_source"] == "explicit"
    assert "Explicit selected content." in result.markdown
    assert "Site selected content." not in result.markdown


def test_theregister_site_drop_text_is_exact_and_replays() -> None:
    html = """<html><head><link rel="canonical" href="https://www.theregister.com/story"></head>
    <body><main><article><h1>Story title</h1>Item Page <span>placeholder(#1)</span> Useful direct text
    <p>The article body remains intact.</p></article><div class="toplist">Top Stories</div></main></body></html>"""
    pipeline = HtmlToMarkdownPipeline()

    discovered = pipeline.run(html)
    replayed = pipeline.run(html, criteria=ExtractionCriteria.from_json(discovered.criteria.to_json()))

    assert discovered.trace.to_dict()["criteria_source"] == "site"
    assert discovered.criteria.drop_text == (r"placeholder\(#1\)",)
    assert "Item Page" in discovered.markdown
    assert "Useful direct text" in discovered.markdown
    assert "placeholder(#1)" not in discovered.markdown
    assert "Top Stories" not in discovered.markdown
    assert replayed.markdown == discovered.markdown


def test_unconfigured_censys_article_uses_generic_discover_and_replays() -> None:
    html = """<html><head><link rel="canonical" href="https://censys.com/blog/post"></head>
    <body><div id="wrap_all"><header>Platform navigation and Get Started Now</header>
      <main class="template-page content">Header and footer chrome</main>
      <div id="main"><section class="article-hero"><div class="article-hero__text">
        <h1 id="article-title" class="article-hero__title">Research</h1></div></section>
        <div class="article-layout"><div class="article-layout__contents">
          <nav class="article-contents"><p>Jump to section:</p><ul class="article-contents__list">
            <li><a href="#summary">Executive summary</a></li>
          </ul></nav></div>
          <article class="article-body"><div class="article-body__content">
            <h2>Executive summary</h2><p>Findings and mitigation guidance remain.</p>
          </div></article><aside class="article-sidebar">Subscribe to our blog</aside>
        </div><section class="related-posts-header"><h2>Related Content</h2><p>Other articles</p></section>
      </div>
    </div></body></html>"""
    result = HtmlToMarkdownPipeline().run(html)
    replayed = HtmlToMarkdownPipeline().run(html, criteria=result.criteria)

    assert result.trace.to_dict()["criteria_source"] == "discover"
    assert "Research" in result.markdown
    assert "Findings and mitigation guidance remain." in result.markdown
    assert "Featured promotion" not in result.markdown
    assert "Subscribe to our blog" not in result.markdown
    assert "Related Content" not in result.markdown
    assert replayed.document == result.document
