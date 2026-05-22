from __future__ import annotations

from bs4 import BeautifulSoup

from domdown._constants import DEFAULT_REMOVE_SELECTORS, SKIP_TAGS
from domdown._document import clean_root, choose_root, parse_html
from tests.fixtures import ARTICLE_SHELL_HTML


def test_clean_root_removes_noise_and_promotes_lazy_loaded_images() -> None:
    """Cleanup should drop noisy tags and normalize lazy-loaded images."""

    soup = BeautifulSoup(
        "<div><script>alert(1)</script><div class='drop'>noise</div><img data-src='/img.png' src='data:image/gif;base64,x' /></div>",
        "lxml",
    )
    root = soup.div

    cleaned = clean_root(root, (".drop",), SKIP_TAGS)

    assert cleaned.find("script") is None
    assert cleaned.select_one(".drop") is None
    assert cleaned.img["src"] == "/img.png"


def test_clean_root_removes_generic_share_and_debug_chrome_from_article_shell() -> None:
    """Generic article chrome should be removed from the selected content subtree."""

    soup = parse_html(ARTICLE_SHELL_HTML)
    root = soup.article

    cleaned = clean_root(
        root,
        (
            ".share-widget",
            ".article-shell__tags",
            ".story-title",
            ".postmeta",
            "[class*='share']",
            "[id*='share']",
            "[class*='breadcrumb']",
            "[class*='related']",
            "[class*='recommend']",
            "[class*='newsletter']",
            "[class*='subscribe']",
            "[class*='promo']",
            "[class*='cta']",
            "[class*='debug']",
            "[class*='author_debug']",
        ),
        SKIP_TAGS,
    )

    text = cleaned.get_text("\n", strip=True)

    assert "Share this article" not in text
    assert "author_debug_inline" not in text
    assert "share-widget" not in text
    assert "Example Topic" not in text
    assert "One paragraph of article content appears here." in text


def test_clean_root_removes_social_follow_and_sponsored_blocks() -> None:
    """Cleanup should drop generic follow and sponsored chrome wrappers."""

    soup = BeautifulSoup(
        """
        <article>
          <p>Body</p>
          <div class="cf note-b">Found this article interesting? Follow us on <a href="https://example.com/news">News</a> and <a href="https://example.com/social">Social</a> to read more exclusive content we post.</div>
          <div class="dog_two clear">
            <div class="cf">
              <a href="https://example.com/ad" rel="nofollow sponsored" target="_blank">
                <img src="https://example.com/ad.png" alt="Ad" />
              </a>
            </div>
          </div>
        </article>
        """,
        "lxml",
    )

    cleaned = clean_root(
        soup.article,
        (
            "[class*='share']",
            "[id*='share']",
            "[class*='follow']",
            "[class*='social']",
            "[class*='sponsored']",
            "[rel*='sponsored']",
            "[class*='note-b']",
            "[class*='dog_two']",
        ),
        SKIP_TAGS,
    )

    text = cleaned.get_text(" ", strip=True)

    assert "Found this article interesting?" not in text
    assert "exclusive content we post" not in text
    assert "ad.png" not in text
    assert "Body" in text


def test_clean_root_removes_header_meta_and_related_link_blocks() -> None:
    """Cleanup should drop top-of-article chrome like repeated headers and related links."""

    soup = BeautifulSoup(
        """
        <article>
          <div class="article-header">
            <h1>Example Title</h1>
            <p>By Example Author</p>
            <time datetime="2026-05-22">May 22, 2026</time>
          </div>
          <section class="related-categories">
            <h2>Related Categories</h2>
            <ul>
              <li><a href="/news">News</a></li>
              <li><a href="/tips">Tips &amp; advice</a></li>
            </ul>
          </section>
          <p>Body</p>
        </article>
        """,
        "lxml",
    )

    cleaned = clean_root(
        soup.article,
        (
            "[class*='share']",
            "[id*='share']",
            "[class*='follow']",
            "[class*='social']",
            "[class*='sponsored']",
            "[rel*='sponsored']",
            "[class*='note-b']",
            "[class*='dog_two']",
        ),
        SKIP_TAGS,
    )

    text = cleaned.get_text(" ", strip=True)

    assert "Example Title" not in text
    assert "By Example Author" not in text
    assert "Related Categories" not in text
    assert "News" not in text
    assert "Tips & advice" not in text
    assert "Body" in text


def test_clean_root_removes_html_comments() -> None:
    """Cleanup should drop HTML comments like more markers."""

    soup = BeautifulSoup("<article><!--more--><p>Content</p></article>", "lxml")

    cleaned = clean_root(soup.article, (), SKIP_TAGS)

    assert "more" not in cleaned.get_text(" ", strip=True)
    assert "Content" in cleaned.get_text(" ", strip=True)
