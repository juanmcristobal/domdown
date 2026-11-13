from __future__ import annotations

from domdown._pipeline import HtmlToMarkdownPipeline
from domdown.adapters import (
    BleepingComputerAdapter,
    CyberSecurityNewsAdapter,
    DailySecuAdapter,
    GBHackersAdapter,
    TheHackerNewsAdapter,
)


def test_dailysecu_adapter_removes_article_chrome_and_keeps_body() -> None:
    pipeline = HtmlToMarkdownPipeline(adapters=(DailySecuAdapter(),))
    html = """
    <html>
      <head>
        <meta property="og:site_name" content="데일리시큐" />
        <meta property="og:url" content="https://www.dailysecu.com/news/articleView.html?idxno=1" />
      </head>
      <body>
        <div id="article-view">
          <div class="article-view-header"><div class="section-name">산업</div></div>
          <h1>Title</h1>
          <div class="helper-tool-group">Share and font controls</div>
          <article id="article-view-content-div"><p>Body paragraph.</p><div class="ad-template"></div></article>
          <article class="article-writer">By Reporter</article>
          <article class="box-skin">Related stories</article>
        </div>
      </body>
    </html>
    """

    result = pipeline.run(html)

    assert result.markdown == "Body paragraph."


def test_bleepingcomputer_adapter_removes_sidebar_comments_and_promos() -> None:
    pipeline = HtmlToMarkdownPipeline(adapters=(BleepingComputerAdapter(),))
    html = """
    <html>
      <head>
        <meta property="og:site_name" content="BleepingComputer" />
        <meta property="og:url" content="https://www.bleepingcomputer.com/news/security/example/" />
      </head>
      <body>
        <div class="articleBody">
          <h1>Title</h1>
          <p>Body paragraph.</p>
          <div class="article-callout">Promotional whitepaper.</div>
          <div class="cz-related-article-wrapp"><a href="/news/security/other/">Related article</a></div>
          <div id="nfeatured"><a href="/news/security/other/">Related article</a></div>
          <div id="comment_form"><h5>Post a Comment</h5></div>
          <div class="cz-newz-comment-wrapp"><h5>Comments</h5><p>Forum comment text.</p></div>
        </div>
        <div class="bc_right_sidebar"><div id="pop_stories">Popular Stories</div></div>
      </body>
    </html>
    """

    result = pipeline.run(html)

    assert result.markdown == "# Title\n\nBody paragraph."


def test_bleepingcomputer_adapter_removes_wiz_campaign_banner_but_keeps_editorial_link() -> None:
    pipeline = HtmlToMarkdownPipeline(adapters=(BleepingComputerAdapter(),))
    html = """
    <html>
      <head>
        <meta property="og:site_name" content="BleepingComputer" />
        <meta property="og:url" content="https://www.bleepingcomputer.com/news/security/example/" />
      </head>
      <body><div class="articleBody">
        <h1>Article title</h1>
        <p>Wiz researchers published an investigation that describes the attack.</p>
        <p><a href="https://www.wiz.io/blog/research-report">Read the Wiz research report</a></p>
        <div><a href="https://www.wiz.io/lp/securing-ai-agents-101?utm_source=bleepingcomputer&amp;utm_medium=display&amp;utm_campaign=campaign-id">
          <img src="https://www.bleepstatic.com/c/w/AI-Agents-101.jpg" alt="Wiz AI security banner" />
        </a></div>
        <div class="cz-newz-comment-wrapp" id="comments">
          <h2>Comments</h2><p>Forum-only response should be removed.</p>
        </div>
      </div></body>
    </html>
    """

    result = pipeline.run(html)

    assert "Article title" in result.markdown
    assert "Wiz researchers published an investigation" in result.markdown
    assert "Read the Wiz research report" in result.markdown
    assert "AI-Agents-101.jpg" not in result.cleaned_html
    assert "Wiz AI security banner" not in result.markdown
    assert "Forum-only response" not in result.cleaned_html
    assert "Forum-only response" not in result.markdown
    assert result.criteria.adapter_removed_node_ids
    replay = pipeline.run(html, criteria=result.criteria)
    assert replay.markdown == result.markdown


def test_bleepingcomputer_adapter_keeps_non_campaign_wiz_links_and_images() -> None:
    pipeline = HtmlToMarkdownPipeline(adapters=(BleepingComputerAdapter(),))
    html = """
    <html>
      <head>
        <meta property="og:site_name" content="BleepingComputer" />
        <meta property="og:url" content="https://www.bleepingcomputer.com/news/security/example/" />
      </head>
      <body><article class="articleBody">
        <h1>Article title</h1>
        <p><a href="https://www.wiz.io/lp/security-guide">Wiz guide without campaign tags</a></p>
        <p><a href="https://example.com/banner"><img src="https://www.bleepstatic.com/c/w/editorial-image.jpg" alt="Editorial image" /></a></p>
      </article></body>
    </html>
    """

    result = pipeline.run(html)

    assert "Wiz guide without campaign tags" in result.markdown
    assert "https://www.bleepstatic.com/c/w/editorial-image.jpg" in result.markdown


def test_cybersecuritynews_adapter_removes_social_header_and_related_modules() -> None:
    pipeline = HtmlToMarkdownPipeline(adapters=(CyberSecurityNewsAdapter(),))
    html = """
    <html>
      <head>
        <meta property="og:site_name" content="Cyber Security News" />
        <meta property="og:url" content="https://cybersecuritynews.com/example/" />
      </head>
      <body>
        <article>
          <p><a href="https://www.linkedin.com/company/cyber-news-live-/">Follow on LinkedIn</a></p>
          <h1>Title</h1>
          <p><a href="https://accounts.google.com/"><img alt="Google Prefered" src="https://cybersecuritynews.com/google.svg" /></a></p>
          <p><a href="https://news.google.com/publications/example"><img alt="Google news" src="https://cybersecuritynews.com/google-news.svg" /></a></p>
          <p>Body paragraph.</p>
          <p>********************************************************************************************************************************Follow us on Google News</p>
          <div class="td_module_wrap"><h3>Related Story</h3></div>
        </article>
      </body>
    </html>
    """

    result = pipeline.run(html)

    assert result.markdown == "# Title\n\nBody paragraph."


def test_gbhackers_adapter_removes_tagdiv_chrome_and_keeps_the_article_body() -> None:
    pipeline = HtmlToMarkdownPipeline(adapters=(GBHackersAdapter(),))
    html = """
    <html>
      <head>
        <meta property="og:site_name" content="GBHackers Security | #1 Globally Trusted Cyber Security News Platform" />
        <meta property="og:url" content="https://gbhackers.com/progress-kemp-loadmaster-vulnerability/" />
      </head>
      <body>
        <article>
          <div class="tdb_single_categories">
            <a href="/tag/cyber-security/">cyber security</a>
            <a href="/tag/vulnerability/">Vulnerability</a>
          </div>
          <div class="tdb-post-meta">2 min. Read</div>
          <div class="td-post-sharing">Share Facebook Twitter Pinterest WhatsApp</div>
          <div class="tdb-author-box">By Mayura Kathir</div>
          <h1>Critical Progress Kemp LoadMaster Vulnerability Enables Pre-Auth Remote Code Execution</h1>
          <div class="td-post-content">
            <p>Progress’s Kemp LoadMaster is at the center of a critical pre-authentication RCE vulnerability.</p>
            <p>The flaw allows unauthenticated attackers to run arbitrary shell commands.</p>
          </div>
          <div class="td_module_wrap">
            <h3>Related story</h3>
            <p>Another link card.</p>
          </div>
          <div class="td-related-title">Related Posts</div>
          <div class="td-next-prev-wrap">Previous Next</div>
        </article>
      </body>
    </html>
    """

    result = pipeline.run(html)

    assert result.markdown == (
        "Progress’s Kemp LoadMaster is at the center of a critical pre-authentication RCE vulnerability.\n\n"
        "The flaw allows unauthenticated attackers to run arbitrary shell commands."
    )


def test_gbhackers_adapter_drops_follow_us_footer_copy() -> None:
    pipeline = HtmlToMarkdownPipeline(adapters=(GBHackersAdapter(),))
    html = """
    <html>
      <head>
        <meta property="og:site_name" content="GBHackers Security | #1 Globally Trusted Cyber Security News Platform" />
        <meta property="og:url" content="https://gbhackers.com/example/" />
      </head>
      <body>
        <article>
          <h1>Title</h1>
          <p>Body paragraph.</p>
          <p class="has-text-align-center has-background wp-block-paragraph">
            <strong>Follow us on Google News, LinkedIn, and X to Get Instant Updates and Set GBH as a Preferred Source in Google.</strong>
          </p>
        </article>
      </body>
    </html>
    """

    result = pipeline.run(html)

    assert result.markdown == "# Title\n\nBody paragraph."


def test_thehackernews_adapter_removes_featured_resources_sidebar() -> None:
    pipeline = HtmlToMarkdownPipeline(adapters=(TheHackerNewsAdapter(),))
    html = """
    <html>
      <head>
        <meta property="og:site_name" content="The Hacker News" />
        <meta property="og:url" content="https://thehackernews.com/2026/06/example.html" />
      </head>
      <body>
        <main>
          <h1>Title</h1>
          <p>Body paragraph.</p>
          <section class="side_res"><div class="PopularPosts">⭐ Featured Resources</div></section>
        </main>
      </body>
    </html>
    """

    result = pipeline.run(html)

    assert result.markdown == "# Title\n\nBody paragraph."
