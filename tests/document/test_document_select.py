from __future__ import annotations

from domdown._document import choose_root, parse_html
from domdown._document.select import (
    _best_content_subtree,
    _best_page_shell_child,
    _collect_root_candidates,
    _contains_page_shell_child,
    _looks_like_layout_shell,
    _pick_best_root_candidate,
    _refine_content_root,
    _root_candidate_penalty,
    _root_selectors,
    _score_content,
)
from tests.fixtures import ARTICLE_SHELL_HTML


def test_choose_root_prefers_the_denser_shell_over_selector_order() -> None:
    """Root selection should favor the denser shell even if selector order differs."""

    soup = parse_html(
        "<html><body><main><div class='articlebody'><p>article</p></div><div class='post-body'><p>post</p></div></main></body></html>"
    )

    root = choose_root(soup, prefer_article_body=True)

    assert root.get("class") == ["articlebody"]


def test_choose_root_can_flip_priority_order() -> None:
    """The root chooser should respect the caller preference order."""

    soup = parse_html(
        "<html><body><main><div class='articlebody'><p>article</p></div><div class='post-body'><p>post</p></div></main></body></html>"
    )

    root = choose_root(soup, prefer_article_body=False)

    assert root.get("class") == ["articlebody"]


def test_choose_root_prefers_inner_content_container_inside_article_shell() -> None:
    """Article shells should resolve to the inner content container, not the whole wrapper."""

    soup = parse_html(ARTICLE_SHELL_HTML)

    root = choose_root(soup, prefer_article_body=True)

    assert root.name in {"article", "div"}
    if root.name == "div":
        assert root.get("class") == ["content", "content--narrow"]


def test_choose_root_keeps_small_semantic_article() -> None:
    """A small but semantic content container should still win over the shell."""

    soup = parse_html(
        """
            <html>
              <body>
                <main class="story-shell">
                  <div class="entry-content">
                    <p>Short story.</p>
                  </div>
                  <div class="promo-banner">
                    <p>Read the latest updates and learn more.</p>
                  </div>
                </main>
              </body>
            </html>
        """
    )

    root = choose_root(soup, prefer_article_body=True)

    assert root.get("class") == ["entry-content"]


def test_choose_root_ignores_navigation_like_content_blocks() -> None:
    """Navigation-like blocks with 'content' in the class should not displace the shell."""

    soup = parse_html(
        """
            <html>
              <body>
                <main>
                  <div class="navigation__feature-content">
                    <p>What’s new in this section</p>
                  </div>
                  <p>This is the actual article body paragraph one.</p>
                  <p>This is the actual article body paragraph two.</p>
                </main>
              </body>
            </html>
        """
    )

    root = choose_root(soup, prefer_article_body=True)

    assert root.name in {"main", "section"}
    if root.name == "section":
        assert root.get("class") == ["blog-all-content"]


def test_choose_root_skips_root_article_when_it_looks_like_chrome() -> None:
    """A root article that smells like chrome should be skipped in favor of a real shell."""

    soup = parse_html(
        """
            <html>
              <body>
                <article class="navigation__feature">
                  <p>What’s new in this section</p>
                </article>
                <main>
                  <p>This is the actual article body paragraph one.</p>
                  <p>This is the actual article body paragraph two.</p>
                </main>
              </body>
            </html>
        """
    )

    root = choose_root(soup, prefer_article_body=True)

    assert root.name == "main"


def test_choose_root_prefers_the_more_content_dense_shell_when_multiple_candidates_match() -> None:
    """The selector tier should not force a smaller shell to win over a denser one."""

    soup = parse_html(
        """
            <html>
              <body>
                <main>
                  <div class="post-body">
                    <p>Short body.</p>
                  </div>
                  <div class="articlebody">
                    <p>Paragraph one.</p>
                    <p>Paragraph two.</p>
                    <p>Paragraph three.</p>
                  </div>
                </main>
              </body>
            </html>
        """
    )

    root = choose_root(soup, prefer_article_body=True)

    assert root.get("class") == ["articlebody"]


def test_choose_root_does_not_pick_body_when_a_real_content_shell_exists() -> None:
    """The fallback body should never beat a real article container."""

    soup = parse_html(
        """
            <html>
              <body class="page-wrapper">
                <main class="article-shell">
                  <div class="markdown-body">
                    <p>This is the actual article body paragraph one.</p>
                    <p>This is the actual article body paragraph two.</p>
                  </div>
                </main>
              </body>
            </html>
        """
    )

    root = choose_root(soup, prefer_article_body=True)

    assert root.name != "body"
    assert root.name in {"main", "div"}


def test_choose_root_ignores_cookie_consent_banners_when_article_body_is_nested() -> None:
    """Consent overlays should not win when the article body is nested deeper in the page."""

    soup = parse_html(
        """
            <html>
              <body>
                <div class="cli-modal-content cli-bar-popup">
                  <div class="cli-privacy-content-text">
                    This website uses cookies to improve your experience while you navigate through the website.
                  </div>
                </div>
                <div class="category-section category-section-details bg-white">
                  <div class="container">
                    <div class="row">
                      <div class="col-sm-12 col-md-12 col-lg-8">
                        <div class="article-details-block wow fadeInUp">
                          <div class="common-heading line-bottom article-title mb-3 wow fadeInUp">
                            <h2>Azure CLI Targeted in LSHIY Password Spray Campaign Across 64 Orgs</h2>
                          </div>
                          <div class="post-time mb-3">
                            <span>Pierluigi Paganini</span>
                            <span>July 01, 2026</span>
                          </div>
                          <p>The article body starts here and contains the real report.</p>
                          <p>It should win over the consent banner.</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </body>
            </html>
        """
    )

    root = choose_root(soup, prefer_article_body=True)

    assert root.get("class") == ["article-details-block", "wow", "fadeInUp"]
    assert "cookies" not in root.get_text(" ", strip=True).lower()


def test_choose_root_prefers_tagdiv_article_content_over_theme_wrapper() -> None:
    """TagDiv theme wrappers should not outrank the actual post content."""

    soup = parse_html(
        """
            <html>
              <body>
                <div class="td-theme-wrap">
                  <div class="td-main-content-wrap td-container-wrap">
                    <article class="post">
                      <div class="td_block_wrap tdb_single_content td-post-content tagdiv-type">
                        <h1>Massive Password Stealing Attack Targeting Microsoft 365 Users</h1>
                        <p>The article body starts here and contains the report text.</p>
                        <p>More prose to make the content block clearly dominant.</p>
                      </div>
                    </article>
                  </div>
                </div>
              </body>
            </html>
        """
    )

    root = choose_root(soup, prefer_article_body=True)

    assert "Massive Password Stealing Attack Targeting Microsoft 365 Users" in root.get_text(" ", strip=True)
    assert "The article body starts here" in root.get_text(" ", strip=True)
    assert "td-theme-wrap" not in (root.get("class") or [])


def test_choose_root_prefers_main_over_a_giant_page_wrapper() -> None:
    """Generic page wrappers with a nested main should not outrank the article shell."""

    soup = parse_html(
        """
            <html>
              <body>
                <div class="page_wrap">
                  <div class="nav">
                    <a href="/a">A</a>
                    <a href="/b">B</a>
                    <a href="/c">C</a>
                    <a href="/d">D</a>
                  </div>
                  <main>
                    <section class="blog-all-content">
                      <h1>Article title</h1>
                      <p>Paragraph one.</p>
                      <p>Paragraph two.</p>
                      <h2>Key takeaways</h2>
                      <ul>
                        <li>Takeaway one.</li>
                        <li>Takeaway two.</li>
                      </ul>
                    </section>
                  </main>
                </div>
              </body>
            </html>
        """
    )

    root = choose_root(soup, prefer_article_body=True)

    assert root.name == "section"
    assert root.get("class") == ["blog-all-content"]


def test_choose_root_prefers_article_over_a_link_dense_shell() -> None:
    """Link-heavy generic shells should not beat the real article body."""

    soup = parse_html(
        """
            <html>
              <body>
                <div class="xf-content-height">
                  <header class="ftnt-navigation">
                    <nav>
                      <a href="/one">One</a>
                      <a href="/two">Two</a>
                      <a href="/three">Three</a>
                      <a href="/four">Four</a>
                      <a href="/five">Five</a>
                      <a href="/six">Six</a>
                      <a href="/seven">Seven</a>
                      <a href="/eight">Eight</a>
                      <a href="/nine">Nine</a>
                      <a href="/ten">Ten</a>
                      <a href="/eleven">Eleven</a>
                      <a href="/twelve">Twelve</a>
                      <a href="/thirteen">Thirteen</a>
                      <a href="/fourteen">Fourteen</a>
                      <a href="/fifteen">Fifteen</a>
                      <a href="/sixteen">Sixteen</a>
                      <a href="/seventeen">Seventeen</a>
                      <a href="/eighteen">Eighteen</a>
                      <a href="/nineteen">Nineteen</a>
                      <a href="/twenty">Twenty</a>
                    </nav>
                  </header>
                </div>
                <main class="page--body">
                  <h1>Article title</h1>
                  <p>Paragraph one.</p>
                  <p>Paragraph two.</p>
                  <p>Paragraph three.</p>
                </main>
              </body>
            </html>
        """
    )

    root = choose_root(soup, prefer_article_body=True)

    assert root.name == "main"


def test_choose_root_ignores_empty_toc_sidebars() -> None:
    """A compact table-of-contents sidebar should not win over the article body."""

    soup = parse_html(
        """
            <html>
              <body>
                <article>
                  <section class="article-layout">
                    <div class="article-layout__sidebar" data-toc-container="true">
                      <div class="p-6">
                        <h3>Table of Contents</h3>
                        <nav aria-label="Table of Contents"></nav>
                      </div>
                    </div>
                    <div class="article-layout__content prose">
                      <p>The real article body paragraph one.</p>
                      <p>The real article body paragraph two.</p>
                    </div>
                  </section>
                </article>
              </body>
            </html>
        """
    )

    root = choose_root(soup, prefer_article_body=True)

    assert "The real article body paragraph one." in root.get_text(" ", strip=True)
    assert root.get("class") != ["article-layout__sidebar"]


def test_choose_root_stops_before_refining_into_a_bare_paragraph() -> None:
    """Paragraph-level nodes should not become the selected content root."""

    soup = parse_html(
        """
            <html>
              <body>
                <main class="article-shell">
                  <div class="content-shell">
                    <span class="rich-text">
                      <p>This is the article body paragraph one.</p>
                      <p>This is the article body paragraph two.</p>
                    </span>
                  </div>
                </main>
              </body>
            </html>
        """
    )

    root = choose_root(soup, prefer_article_body=True)

    assert root.name != "p"


def test_choose_root_does_not_refine_into_a_generic_layout_wrapper() -> None:
    """Generic layout wrappers should not win over the actual content shell."""

    soup = parse_html(
        """
            <html>
              <body>
                <main>
                  <div class="container-fluid wrapper">
                    <div class="article-copy">
                      <p>This is the real article body paragraph one.</p>
                      <p>This is the real article body paragraph two.</p>
                    </div>
                  </div>
                </main>
              </body>
            </html>
        """
    )

    root = choose_root(soup, prefer_article_body=True)

    assert root.get("class") != ["container-fluid", "wrapper"]


def test_choose_root_prefers_semantic_article_over_layout_shell() -> None:
    """An article inside a bootstrap-like layout shell should beat the outer wrapper."""

    soup = parse_html(
        """
            <html>
              <body>
                <div class="container d-flex flex-column px-xxl-5">
                  <aside id="sidebar">
                    <nav><a href="/">Home</a><a href="/tags">Tags</a></nav>
                  </aside>
                  <div id="main-wrapper" class="d-flex justify-content-center">
                    <main aria-label="Main Content" class="col-12 col-lg-11 col-xl-9 px-md-4">
                      <article class="px-1">
                        <header>
                          <h1>HookChain: A Deep Dive into Advanced EDR Bypass Techniques</h1>
                          <div class="post-meta text-muted">
                            <span>Posted <time datetime="2024-10-25T00:00:00+03:00">Oct 25, 2024</time></span>
                            <span>By <em><a href="https://twitter.com/0xmaz">Mohamed Alzhrani</a></em></span>
                          </div>
                        </header>
                        <div class="content">
                          <p>Paragraph one.</p>
                          <p>Paragraph two.</p>
                          <p>Paragraph three.</p>
                        </div>
                      </article>
                    </main>
                  </div>
                </div>
              </body>
            </html>
        """
    )

    root = choose_root(soup, prefer_article_body=True)

    assert root.name == "div"
    assert root.get("class") == ["content"]


def test_choose_root_prefers_main_over_page_shell_wrappers() -> None:
    """A full page shell should not beat a semantic main content block."""

    soup = parse_html(
        """
            <html>
              <body>
                <div class="page">
                  <header class="global-header">
                    <nav><a href="/">Home</a></nav>
                  </header>
                  <main>
                    <section class="hero">
                      <p>Interactive malware analysis sandbox for SOC teams</p>
                    </section>
                    <section class="feature">
                      <h2>Fast access to knowledge</h2>
                      <p>Our VMs start in under 10s.</p>
                      <p>And it takes just 40s until the report.</p>
                    </section>
                  </main>
                  <footer class="footer">
                    <p>Footer links</p>
                  </footer>
                </div>
              </body>
            </html>
        """
    )

    root = choose_root(soup, prefer_article_body=True)

    assert root.name == "main"


def test_choose_root_prefers_blog_content_over_tabbed_promotional_modules() -> None:
    """HubSpot-style tabbed marketing blocks should not outrank the article body."""

    soup = parse_html(
        """
            <html>
              <body>
                <div class="body-container container-fluid">
                  <div class="row-fluid-wrapper row-number-1">
                    <div class="hero-wrap hero-post">
                      <h1>Elliptic intelligence used by the FBI in action against Huione Group</h1>
                      <div class="hero-dtls">
                        <p>Elliptic Intel</p>
                        <p>23 June, 2026</p>
                      </div>
                    </div>
                  </div>
                  <div class="row-fluid-wrapper row-number-2">
                    <div class="span12 widget-span widget-type-cell">
                      <div class="blog-content">
                        <div class="entry-content">
                          <p>Elliptic intelligence was used by the FBI in action against Huione.</p>
                          <p>The action targeted the operators of Huione Group.</p>
                          <p>More article text follows here.</p>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div id="tabs-content">
                    <div class="tab-content">
                      <a href="/solutions/crypto-compliance">Crypto Compliance</a>
                      <a href="/solutions/investigations">Investigations & Intelligence</a>
                      <a href="/solutions/monitoring">Monitoring</a>
                      <a href="/solutions/data-ingestion">Data Ingestion</a>
                    </div>
                  </div>
                </div>
              </body>
            </html>
        """
    )

    root = choose_root(soup, prefer_article_body=True)

    assert root.name == "div"
    assert root.get("class") in (["entry-content"], ["blog-content"])


def test_select_private_helpers_cover_shell_detection_and_scoring() -> None:
    """Selection helpers should keep their shell and scoring branches reachable."""

    soup = parse_html(
        """
        <html>
          <body>
            <div class="wrapper">
              <div class="page-wrapper">
                <header>Header</header>
                <main>
                  <div class="content">
                    <p>This is the actual article body paragraph one.</p>
                    <p>This is the actual article body paragraph two.</p>
                  </div>
                </main>
              </div>
              <div class="container-fluid">
                <main>
                  <p>This content lives in a bootstrap wrapper.</p>
                </main>
              </div>
            </div>
          </body>
        </html>
        """
    )

    selectors_true = _root_selectors(True)
    selectors_false = _root_selectors(False)
    assert selectors_true.index(".post-body") < selectors_true.index(".articlebody")
    assert selectors_false.index(".articlebody") < selectors_false.index(".post-body")

    wrapper = soup.select_one(".wrapper")
    page_wrapper = soup.select_one(".page-wrapper")
    container = soup.select_one(".container-fluid")
    content = soup.select_one(".content")
    assert wrapper is not None
    assert page_wrapper is not None
    assert container is not None
    assert content is not None

    assert _looks_like_layout_shell(wrapper) is True
    assert _contains_page_shell_child(wrapper) is True
    assert _best_page_shell_child(wrapper) is page_wrapper

    assert _score_content(content) > _score_content(container)
    assert _root_candidate_penalty(container) <= -180.0
    assert _root_candidate_penalty(wrapper) <= -180.0
    assert _root_candidate_penalty(parse_html("<div class='wrapper'><p>text</p></div>").div) == -25.0

    candidates = _collect_root_candidates(soup, (".content", "[class*='content']"))
    assert len(candidates) >= 1
    assert candidates[0][0].get("class") == ["content"]
    assert _pick_best_root_candidate([(wrapper, 1.0, 0), (content, 2.0, 1)]) is content


def test_select_private_helpers_cover_refinement_fallbacks() -> None:
    """Refinement should stop on paragraph-level and undersized candidates."""

    shallow = parse_html("<html><body><div class='article-shell'><p>Short text.</p></div></body></html>")
    assert _refine_content_root(shallow.div).name == "div"

    small = parse_html(
        "<html><body><div class='article-shell'><div class='content'><p>Just a few words here.</p></div></div></body></html>"
    )
    assert _best_content_subtree(small.div).name == "div"
