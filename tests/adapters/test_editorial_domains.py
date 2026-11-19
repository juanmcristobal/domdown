from __future__ import annotations

import pytest

from domdown._pipeline import HtmlToMarkdownPipeline


@pytest.mark.parametrize(
    ("url", "footer_heading", "promo"),
    [
        ("https://blog.railway.com/p/story", "Continue Reading...", "Recommended story"),
    ],
)
def test_site_criteria_remove_trailing_recommendations(url, footer_heading, promo) -> None:
    html = f"""
    <html><head><meta property="og:url" content="{url}" /></head><body>
      <article><h1>Editorial title</h1>
        <p>Editorial body remains.</p>
        <p><a href="https://example.com/reference">Reference link</a></p>
        <section><h2>{footer_heading}</h2><p>{promo}</p></section>
      </article>
    </body></html>
    """

    result = HtmlToMarkdownPipeline().run(html)

    assert "Editorial body remains." in result.markdown
    assert "Reference link" in result.markdown
    assert footer_heading not in result.markdown
    assert promo not in result.markdown
    assert result.trace.to_dict()["criteria_source"] == "site"


def test_wiz_uses_heading_and_prose_without_page_recommendations() -> None:
    html = """
    <html><head><meta property="og:url" content="https://www.wiz.io/blog/story" /></head>
    <body><article><header><h1>Wiz research title</h1></header>
      <div class="prose"><p>Wiz article body remains.</p>
        <p>Reference: <a href="https://example.com/report">technical report</a></p>
      </div>
      <aside><section><h2>Continue reading</h2><p>Recommendation to remove.</p></section>
        <section><h2>Ready to see Wiz in action?</h2><p>Sales CTA to remove.</p></section></aside>
    </article></body></html>
    """

    result = HtmlToMarkdownPipeline().run(html)
    replayed = HtmlToMarkdownPipeline().run(html, criteria=result.criteria)

    assert result.criteria.include == ("h1", "div.prose")
    assert result.criteria.exclude == ("a.ease-spring-button",)
    assert "Wiz research title" in result.markdown
    assert "Wiz article body remains." in result.markdown
    assert "technical report" in result.markdown
    assert "Continue reading" not in result.markdown
    assert "Recommendation to remove." not in result.markdown
    assert "Ready to see Wiz in action?" not in result.markdown
    assert "Sales CTA to remove." not in result.markdown
    assert result.trace.to_dict()["criteria_source"] == "site"
    assert replayed.document == result.document


def test_dark_reading_site_criteria_remove_author_bio_and_topic_tags() -> None:
    html = """
    <html><head><meta property="og:url" content="https://www.darkreading.com/example" /></head>
    <body><div class="TwoColumnLayout-Content"><div class="TwoColumnLayout-Body"><div class="ArticleBase-Body">
      <h1>Article title</h1><p>Editorial body remains with its technical details.</p>
      <div class="ArticleBase-ContributorsWrapper">
        <h2 class="ArticleBase-ContributorsTitle">About the Author</h2>
        <div class="ContributorSummary-InfoWrapper">
          <p class="ContributorSummary-Title">Elizabeth Montalbano</p>
          <p class="ContributorSummary-SubTitle">Contributing Writer</p>
          <div class="ContributorSummary-ContentWrapper"><p>Long author biography text to remove.</p></div>
          <div class="ContributorSummary-SeeMore"><a>See more from Elizabeth</a></div>
        </div>
      </div>
      <div class="ArticleBase-More">Read more about: DR Global Europe</div>
    </div></div></body></html>
    """

    result = HtmlToMarkdownPipeline().run(html)

    assert "Editorial body remains" in result.markdown
    assert "About the Author" not in result.markdown
    assert "Elizabeth Montalbano" not in result.markdown
    assert "Long author biography text" not in result.markdown
    assert "See more from Elizabeth" not in result.markdown
    assert "Read more about" not in result.markdown


def test_dark_reading_two_column_layout_keeps_article_and_removes_promotional_blocks() -> None:
    html = """
    <html><head><meta property="og:url" content="https://www.darkreading.com/example" /></head>
    <body><div class="TwoColumnLayout-Content">
      <header><h1>Dark Reading article title</h1></header>
      <div class="TwoColumnLayout-Body">
        <p>Full article body remains available.</p>
        <div class="ArticleBase-Contributors"><p>Contributor block.</p></div>
        <div class="ArticleBase-ContributorsWrapper"><p>Contributor biography.</p></div>
        <div class="ArticleBase-More"><p>Read more about: related topics.</p></div>
        <div class="EventsPromotions"><p>Upcoming event promotion.</p></div>
        <div class="RelatedArticle"><p>Related article card.</p></div>
        <div class="Resources"><p>Download the resource.</p></div>
      </div>
    </div></body></html>
    """

    result = HtmlToMarkdownPipeline().run(html)
    replayed = HtmlToMarkdownPipeline().run(html, criteria=result.criteria)

    assert result.criteria.include[:2] == ("h1", "div.TwoColumnLayout-Body")
    assert result.criteria.exclude == (
        ".ArticleBase-Contributors",
        ".ArticleBase-ContributorsWrapper",
        ".ArticleBase-More",
        ".EventsPromotions",
        ".RelatedArticle",
        ".Resources",
    )
    assert result.markdown.count("Dark Reading article title") == 1
    assert "Full article body remains available." in result.markdown
    for noise in (
        "Contributor block.",
        "Contributor biography.",
        "Read more about",
        "Upcoming event promotion.",
        "Related article card.",
        "Download the resource.",
    ):
        assert noise not in result.markdown
    assert result.trace.to_dict()["criteria_source"] == "site"
    assert replayed.document == result.document


def test_security_affairs_removes_social_footer_and_keeps_author_attribution() -> None:
    html = """
    <html><head><meta property="og:url" content="https://securityaffairs.com/example" /></head>
    <body><div class="article-details-block">
      <h1>Article title</h1><p>Editorial article body remains.</p>
      <p><strong>Follow me on Twitter:</strong> <a href="https://twitter.com/securityaffairs">@securityaffairs</a>
        and <a href="https://www.facebook.com/sec.affairs">Facebook</a></p>
      <p><a href="https://www.linkedin.com/pub/example">Author attribution</a></p>
    </div></body></html>
    """

    result = HtmlToMarkdownPipeline().run(html)

    assert "Editorial article body remains." in result.markdown
    assert "Follow me on Twitter" not in result.markdown
    assert "@securityaffairs" not in result.markdown
    assert "Author attribution" in result.markdown
    assert result.trace.to_dict()["criteria_source"] == "site"


def test_securityweek_removes_embedded_ad_after_root_selection() -> None:
    html = """
    <html><head><meta property="og:url" content="https://www.securityweek.com/example" /></head>
    <body><main id="zox-site"><article><h1>Article title</h1>
      <div class="zox-post-body"><p>Editorial article body remains.</p>
        <div class="zox-post-ad-wrap"><span>Advertisement. Scroll to continue reading.</span>
          <div class="zox-post-ad"><script>ad code</script></div>
        </div>
      </div>
    </article></main></body></html>
    """

    result = HtmlToMarkdownPipeline().run(html)

    assert "Article title" in result.markdown
    assert "Editorial article body remains." in result.markdown
    assert "Advertisement. Scroll to continue reading." not in result.cleaned_html
    assert "Advertisement. Scroll to continue reading." not in result.markdown
    assert result.trace.to_dict()["criteria_source"] == "site"


def test_securityweek_selects_article_regions_without_social_or_sidebar_widgets() -> None:
    html = """
    <html><head><meta property="og:url" content="https://www.securityweek.com/example" /></head>
    <body><article>
      <header class="zox-post-head-wrap"><h1 class="zox-post-title">Article title</h1></header>
      <div class="zox-post-body"><p>Article body.</p></div>
      <ul class="zox-post-soc-list"><li><a href="#">Flipboard</a></li><li><a href="#">Reddit</a></li></ul>
      <div class="zox-post-side-wrap"><div class="zox-side-widget widget_text">
        <div class="sw-block-webinar"><div class="sw-webinar">
          <a href="https://register.securityweek.com/ciso-forum">Virtual Event: CISO Forum 2026 Summit</a>
          <p>Join as we bring together cybersecurity leaders.</p>
          <a href="https://register.securityweek.com/ciso-forum">Register</a>
        </div></div>
      </div></div>
    </article></body></html>
    """

    result = HtmlToMarkdownPipeline().run(html)
    replayed = HtmlToMarkdownPipeline().run(html, criteria=result.criteria)

    assert "Article title" in result.markdown
    assert "Article body." in result.markdown
    assert "Flipboard" not in result.markdown
    assert "Reddit" not in result.markdown
    assert "CISO Forum" not in result.markdown
    assert "Join as we bring" not in result.markdown
    assert "Register" not in result.markdown
    assert replayed.document == result.document


def test_securityweek_trims_trending_and_everything_after_it() -> None:
    html = """
    <html><head><meta property="og:url" content="https://www.securityweek.com/example" /></head>
    <body><article><h1>Article title</h1>
      <div class="zox-post-body"><p>Editorial body remains before the recommendations.</p>
        <p><strong>Related:</strong> <a href="https://securityweek.com/related/">Related article one.</a></p>
        <h3>Trending</h3><h2>Trending recommendation.</h2>
        <h2>More to read</h2><p>More recommendation content.</p>
      </div>
    </article></body></html>
    """

    result = HtmlToMarkdownPipeline().run(html)

    assert "Editorial body remains before the recommendations." in result.markdown
    assert "Related:" not in result.markdown
    assert "Related article one." not in result.markdown
    assert "Related article two." not in result.markdown
    assert "Related article three." not in result.markdown
    assert "Related article four." not in result.markdown
    assert "Trending" not in result.markdown
    assert "Trending recommendation." not in result.markdown
    assert "More recommendation content." not in result.markdown
    assert result.trace.to_dict()["criteria_source"] == "site"


def test_cyberscoop_site_criteria_remove_advertisement_and_google_stickybar() -> None:
    html = """
    <html><head>
      <meta property="og:url" content="https://cyberscoop.com/story/" />
    </head><body>
      <div class="single-article__header-content">
        <ul class="single-article__eyebrow"><li><a href="/tag/security/">Security</a></li></ul>
        <h1 class="single-article__title">Editorial title</h1>
        <div class="single-article__excerpt"><p>Story summary teaser.</p></div>
        <div class="single-article__meta"><p>By Author Name</p></div>
      </div>
      <main id="main">
        <div class="ad__inner"><span class="screen-reader-text">Advertisement</span></div>
        <div class="stickybar">
          <p>Get our latest cybersecurity news first on Google.</p>
          <a class="stickybar__link" href="https://google.com/preferences/source?q=cyberscoop.com">Click here!</a>
        </div>
        <div class="single-article__container js-single-article-content">
          <article class="single-article content"><p>Article body remains.</p></article>
          <footer class="single-article__footer"><p>Related stories footer.</p></footer>
        </div>
      </main>
    </body></html>
    """

    result = HtmlToMarkdownPipeline().run(html)

    assert result.trace.to_dict()["criteria_source"] == "site"
    assert result.criteria.include == ("div.single-article__container.js-single-article-content",)
    assert "Editorial title" not in result.markdown  # promoted as heading via frontmatter title
    assert "Article body remains." in result.markdown
    assert "Advertisement" not in result.markdown
    assert "Get our latest cybersecurity news first on Google." not in result.markdown
    assert "Click here!" not in result.markdown
    assert "Story summary teaser." not in result.markdown
    assert "By Author Name" not in result.markdown
    assert "Related stories footer." not in result.markdown
    assert "- Security" not in result.markdown


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
