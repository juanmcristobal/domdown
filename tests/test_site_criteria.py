from __future__ import annotations

from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from domdown import SITE_CRITERIA, CriteriaError, DomdownOptions, ExtractionCriteria, HtmlToMarkdownPipeline
from domdown.site_criteria import criteria_for_document
from tests.real import load_real_cases


def test_site_registry_uses_only_supported_rule_fields() -> None:
    assert set(SITE_CRITERIA) == {
        "wikipedia",
        "the_register",
        "cyberscoop",
        "dark_reading",
        "securityweek",
        "security_affairs",
        "wiz",
        "railway",
        "google_blog",
        "gbhackers",
        "the_hacker_news",
        "cybersecurity_news",
        "bleepingcomputer",
        "dailysecu",
        "arxiv",
        "medium",
        "github",
        "huggingface_blog",
        "techcrunch_articles",
        "deepmind_blog",
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
        r"/blob/",
        r"/issues/",
        r"/releases/tag/",
        r"/security/advisories",
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
    document = BeautifulSoup('<link rel="canonical" href="https://en.wikipedia.org/wiki/Test">', "lxml")
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


def test_google_blog_site_criteria_preserve_real_article_and_replay() -> None:
    """Google's article layout uses shared Apply criteria and omits its audio chrome."""

    url = "https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-hydrogen/"
    html = (Path(__file__).parent / "fixtures" / "blog_google_gemini_4_hydrogen.html").read_text(encoding="utf-8")
    pipeline = HtmlToMarkdownPipeline(DomdownOptions(base_url=url))

    result = pipeline.run(html)
    replay = pipeline.run(html, criteria=ExtractionCriteria.from_json(result.criteria.to_json()))

    assert result.trace.criteria_source == "site"
    assert result.trace.mode == "selector_apply"
    assert result.trace.adapters == ()
    assert result.criteria.include == ("article.uni-article-wrapper",)
    assert result.markdown.startswith(
        "# Introducing Gemini 4 Hydrogen\n\nHydrogen brings cutting-edge intelligence to everyone."
    )
    assert "Unlocking efficiencies in multi-model workloads" in result.markdown
    assert "Gemini 4 Hydrogen, available to everyone today" in result.markdown
    assert "Artificial analysis intelligence index" in result.markdown
    assert result.markdown.count("![") >= 8
    assert "Listen to article" not in result.markdown
    assert "This content is generated by Google AI" not in result.markdown
    assert "Last updated November 16, 2026" not in result.markdown
    assert "Koray Kavukcuoglu" not in result.markdown
    assert result.metadata.published == "2026-11-12"
    assert replay.markdown == result.markdown
    assert replay.document == result.document
    assert replay.trace.mode == "exact_replay"


def test_google_blog_science_article_uses_shared_criteria_and_replays() -> None:
    url = "https://blog.google/innovation-and-ai/technology/research/gemini-for-science-io-2026/"
    html = (Path(__file__).parent / "fixtures" / "google_gemini_for_science.html").read_text(encoding="utf-8")
    pipeline = HtmlToMarkdownPipeline(DomdownOptions(base_url=url))

    result = pipeline.run(html)
    replay = pipeline.run(html, criteria=ExtractionCriteria.from_json(result.criteria.to_json()))

    assert result.trace.criteria_source == "site"
    assert result.trace.mode == "selector_apply"
    assert result.trace.adapters == ()
    assert result.criteria.include == ("article.uni-article-wrapper",)
    assert result.metadata.title == "Gemini for Science: AI experiments and tools for a new era of discovery"
    assert result.metadata.published == "2026-05-19"
    assert "A force multiplier for human ingenuity" in result.markdown
    assert "A scientific workbench on your desktop" in result.markdown
    assert "A collaborative effort with the scientific community" in result.markdown
    assert "Listen to article" not in result.markdown
    assert "Pushmeet Kohli" not in result.markdown
    assert "Yossi Matias" not in result.markdown
    assert len(result.markdown.split()) > 900
    assert len(result.markdown.split("](")) > 20
    assert replay.markdown == result.markdown
    assert replay.document == result.document
    assert replay.trace.mode == "exact_replay"


def test_huggingface_blog_criteria_extract_streamhouse_article_and_replay() -> None:
    url = "https://huggingface.co/blog/ibm-research/time-series-powered-streamhouse"
    html = (Path(__file__).parent / "fixtures" / "huggingface_streamhouse.html").read_text(encoding="utf-8")
    pipeline = HtmlToMarkdownPipeline(DomdownOptions(base_url=url))

    result = pipeline.run(html)
    replay = pipeline.run(html, criteria=ExtractionCriteria.from_json(result.criteria.to_json()))

    assert result.trace.criteria_source == "site"
    assert result.trace.mode == "selector_apply"
    assert result.trace.adapters == ()
    assert result.criteria.include == (".blog-content",)
    assert result.metadata.title == "Time-Series Models in the Streamhouse: A New Frontier and Use Cases"
    assert "Real-time forecasting, anomaly detection, and optimization" in result.markdown
    assert "Mission-critical use cases across real-enterprises" in result.markdown
    assert "Use Case 1 | Production optimization: every tub in spec" in result.markdown
    assert len(result.markdown.split()) > 2_000
    assert result.markdown.count("![") >= 10
    assert "Back to Articles" not in result.markdown
    assert "Published November 18, 2026" not in result.markdown
    assert "Upvote 17" not in result.markdown
    assert "Follow ibm-research" not in result.markdown
    assert replay.markdown == result.markdown
    assert replay.document == result.document
    assert replay.trace.mode == "exact_replay"


def test_huggingface_site_rule_is_scoped_to_blog_paths() -> None:
    document = BeautifulSoup('<link rel="canonical" href="https://huggingface.co/models/example">', "lxml")
    assert criteria_for_document(document) is None


def test_techcrunch_criteria_extract_mavi_article_and_replay() -> None:
    url = "https://techcrunch.com/2026/09/28/mavi-bets-on-the-ai-boom-creating-demand-for-a-new-kind-of-accountant/"
    html = (Path(__file__).parent / "fixtures" / "techcrunch_mavi_accountant.html").read_text(encoding="utf-8")
    pipeline = HtmlToMarkdownPipeline(DomdownOptions(base_url=url))

    result = pipeline.run(html)
    replay = pipeline.run(html, criteria=ExtractionCriteria.from_json(result.criteria.to_json()))

    assert result.trace.criteria_source == "site"
    assert result.trace.mode == "selector_apply"
    assert result.trace.adapters == ()
    assert result.criteria.include == (".seamless-scroll-container",)
    assert result.metadata.title == "MAVI bets on the AI boom creating demand for a new kind of accountant"
    assert result.metadata.author == ("Dominic-Madori Davis",)
    assert result.metadata.published.startswith("2026-09-28")
    assert result.markdown.count("# MAVI bets on the AI boom") == 1
    assert "Molly Liu and Aman Puri are tackling the U.S. accounting shortage" in result.markdown
    assert "Speaking to TechCrunch, Liu" in result.markdown
    assert "high-skill talent" in result.markdown
    assert result.markdown.count("![") >= 1
    assert "Dominic-Madori Davis" not in result.markdown
    assert "Loading the next article" not in result.markdown
    assert "commission" not in result.markdown
    assert "translate.goog" not in result.markdown
    assert replay.markdown == result.markdown
    assert replay.document == result.document
    assert replay.trace.mode == "exact_replay"


def test_techcrunch_site_rule_is_scoped_to_dated_article_paths() -> None:
    document = BeautifulSoup('<link rel="canonical" href="https://techcrunch.com/latest/">', "lxml")
    assert criteria_for_document(document) is None


def test_deepmind_blog_criteria_extract_planning_article_and_replay() -> None:
    url = "https://deepmind.google/blog/speeding-up-planning-decisions-with-ai/"
    html = (Path(__file__).parent / "fixtures" / "deepmind_speeding_up_planning.html").read_text(encoding="utf-8")
    pipeline = HtmlToMarkdownPipeline(DomdownOptions(base_url=url))

    result = pipeline.run(html)
    replay = pipeline.run(html, criteria=ExtractionCriteria.from_json(result.criteria.to_json()))

    assert result.trace.criteria_source == "site"
    assert result.trace.mode == "selector_apply"
    assert result.trace.adapters == ()
    assert result.criteria.include == ("main#page-content",)
    assert result.criteria.drop_text == (r"Your browser does not support the video tag\.",)
    assert result.metadata.title == "Speeding up planning decisions with AI"
    assert result.metadata.published.startswith("2026-10-31")
    assert result.metadata.author == ("Owen Larter and David Thacker", "Owen Larter and David Thacker")
    assert "How PlanAssist supports officers" in result.markdown
    assert "Moving from pilot to scale" in result.markdown
    assert "AI in service of communities" in result.markdown
    assert "See how Plan Assist works." in result.markdown
    assert "Your browser does not support the video tag." not in result.markdown
    assert "October 31, 2026" not in result.markdown
    assert "Owen Larter and David Thacker" not in result.markdown
    assert "Related posts" not in result.markdown
    assert len(result.markdown.split()) > 500
    assert result.markdown.count("![") >= 3
    assert replay.markdown == result.markdown
    assert replay.document == result.document
    assert replay.trace.mode == "exact_replay"


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
