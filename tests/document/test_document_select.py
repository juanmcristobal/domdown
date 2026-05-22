from __future__ import annotations

from domdown._document import choose_root, parse_html
from tests.fixtures import ARTICLE_SHELL_HTML


def test_choose_root_prefers_post_body_when_article_body_is_enabled() -> None:
    """Root selection should favor the post body when that mode is enabled."""

    soup = parse_html(
        "<html><body><main><div class='articlebody'><p>article</p></div><div class='post-body'><p>post</p></div></main></body></html>"
    )

    root = choose_root(soup, prefer_article_body=True)

    assert root.get("class") == ["post-body"]


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

    assert root.name == "div"
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
