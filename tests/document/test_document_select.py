from __future__ import annotations

from domdown._document import choose_root, parse_html
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

    assert root.name == "main"


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
