from __future__ import annotations

from domdown._pipeline import HtmlToMarkdownPipeline
from domdown.adapters import BleepingComputerAdapter, CyberSecurityNewsAdapter, GBHackersAdapter, TheHackerNewsAdapter


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
        </div>
        <div class="bc_right_sidebar"><div id="pop_stories">Popular Stories</div></div>
      </body>
    </html>
    """

    result = pipeline.run(html)

    assert result.markdown == "# Title\n\nBody paragraph."


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
