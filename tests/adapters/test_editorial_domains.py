from __future__ import annotations

import pytest

from domdown._core import DomdownOptions, PipelineContext
from domdown._pipeline import HtmlToMarkdownPipeline
from domdown.adapters import (
    CensysAdapter,
    CyberScoopEditorialAdapter,
    RailwayAdapter,
    SecurityAffairsAdapter,
    SecurityWeekAdapter,
    TheRegisterAdapter,
    WizAdapter,
)
from domdown.stages.parse import ParseStage


@pytest.mark.parametrize(
    ("adapter", "url", "selector", "attribute", "noise"),
    [
        (TheRegisterAdapter(), "https://www.theregister.com/2026/01/01/story/", "toplist", "class", "Top Stories"),
        (SecurityWeekAdapter(), "https://www.securityweek.com/story/", "widget_sw_widget_moves", "class", "People on the Move"),
        (SecurityAffairsAdapter(), "https://securityaffairs.com/story/", "right-sidebar", "class", "Recent Articles"),
        (CyberScoopEditorialAdapter(), "https://cyberscoop.com/story/", "latest-podcasts", "class", "Latest Podcasts"),
        (CensysAdapter(), "https://censys.com/blog/story/", "header", "id", "Featured promotion"),
    ],
)
def test_editorial_domain_adapters_remove_only_known_modules(adapter, url, selector, attribute, noise) -> None:
    html = f"""
    <html><head>
      <meta property="og:url" content="{url}" />
    </head><body>
      <header><p>Generic site header</p></header>
      <main><article>
        <h1>Editorial title</h1>
        <p>Editorial body must remain, including its technical details.</p>
        <table><tr><th>Setting</th><th>Value</th></tr><tr><td>Port</td><td>443</td></tr></table>
        <p><a href="https://example.com/reference">Technical reference</a></p>
        <aside {attribute}="{selector}">
        <p>{noise}</p>
        </aside>
      </article></main>
    </body></html>
    """

    result = HtmlToMarkdownPipeline(adapters=(adapter,)).run(html)

    assert "Editorial title" in result.markdown
    assert "Editorial body must remain" in result.markdown
    assert "| Setting | Value |" in result.markdown
    assert "Technical reference" in result.markdown
    assert noise not in result.markdown
    assert adapter.name in {item["name"] for item in result.trace.to_dict()["adapters"]}


@pytest.mark.parametrize(
    ("adapter", "url", "footer_heading", "promo"),
    [
        (WizAdapter(), "https://www.wiz.io/blog/story", "## Continue reading", "Ready to see Wiz in action?"),
        (RailwayAdapter(), "https://blog.railway.com/p/story", "### Continue Reading...", "Recommended story"),
    ],
)
def test_editorial_domain_adapters_trim_only_trailing_recommendations(
    adapter, url, footer_heading, promo
) -> None:
    html = f"""
    <html><head><meta property="og:url" content="{url}" /></head><body>
      <article><h1>Editorial title</h1>
        <p>Editorial body remains.</p>
        <p><a href="https://example.com/reference">Reference link</a></p>
      </article>
      <section><h2>{footer_heading}</h2><p>{promo}</p></section>
    </body></html>
    """

    result = HtmlToMarkdownPipeline(adapters=(adapter,)).run(html)

    assert "Editorial body remains." in result.markdown
    assert "Reference link" in result.markdown
    assert footer_heading not in result.markdown
    assert promo not in result.markdown


def test_the_register_toplists_are_removed_after_root_selection() -> None:
    html = """
    <html><head>
      <meta property="og:url" content="https://www.theregister.com/2026/story/" />
    </head><body>
      <main class="pageWidth">
        <section id="main" class="main article">
          <h1>Editorial article title</h1>
          <div class="bodytext"><p>Editorial story.</p>
            <p>References and findings belonging to the article remain intact.</p>
          </div>
        </section>
        <div class="toplist"><h2>TOP STORIES</h2>
          <p>Unrelated recommended story.</p>
        </div>
      </main>
    </body></html>
    """
    context = ParseStage().run(PipelineContext(html=html, options=DomdownOptions()))
    adapter = TheRegisterAdapter()

    assert adapter.matches(context)
    context = adapter.preprocess(context)
    assert context.document.select_one(".toplist") is not None

    context.document = context.document.select_one("main.pageWidth")
    context = adapter.post_clean(context)

    assert context.document.select_one(".toplist") is None
    assert "Editorial article title" in context.document.get_text(" ", strip=True)
    assert "References and findings belonging to the article remain intact." in context.document.get_text(" ", strip=True)


def test_cyberscoop_removes_advertisement_and_google_stickybar() -> None:
    html = """
    <html><head>
      <meta property="og:url" content="https://cyberscoop.com/story/" />
    </head><body><main id="main">
      <div class="ad__inner"><span class="screen-reader-text">Advertisement</span></div>
      <div class="stickybar">
        <p>Get our latest cybersecurity news first on Google.</p>
        <a class="stickybar__link" href="https://google.com/preferences/source?q=cyberscoop.com">Click here!</a>
      </div>
      <article><h1>Editorial title</h1><p>Article body remains.</p></article>
    </main></body></html>
    """

    result = HtmlToMarkdownPipeline(adapters=(CyberScoopEditorialAdapter(),)).run(html)

    assert "Editorial title" in result.markdown
    assert "Article body remains." in result.markdown
    assert "Advertisement" not in result.markdown
    assert "Get our latest cybersecurity news first on Google." not in result.markdown
    assert "Click here!" not in result.markdown


def test_opshiled_notice_page_is_treated_as_semantic_content() -> None:
    html = """
    <html><head><title>Security Advisory</title></head><body>
      <main class="notice-page security-advisory">
        <article class="notice-article">
          <h1>Security Advisory: Vulnerability Report</h1>
          <p>The advisory describes an affected component and remediation steps.</p>
        </article>
      </main>
      <footer><nav><h2>SECURITY FOR</h2><p>Footer navigation links</p></nav></footer>
    </body></html>
    """

    result = HtmlToMarkdownPipeline().run(html)

    assert "Security Advisory: Vulnerability Report" in result.markdown
    assert "affected component and remediation steps" in result.markdown
    assert "SECURITY FOR" not in result.markdown
