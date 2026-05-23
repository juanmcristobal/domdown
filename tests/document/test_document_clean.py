from __future__ import annotations

from bs4 import BeautifulSoup

from domdown._constants import DEFAULT_REMOVE_SELECTORS, SKIP_TAGS
from domdown._document import clean_root, choose_root, parse_html
from tests.fixtures import (
    ARTICLE_ARTICLE_CHROME_HTML,
    ARTICLE_DIVI_ABOUT_AND_FAQ_HTML,
    ARTICLE_HUBSPOT_ROW_WRAPPER_HTML,
    ARTICLE_PAID_ACCESS_HTML,
    ARTICLE_SHELL_HTML,
)


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
            ".news-form",
            ".article-info",
            ".et_pb_title_meta_container",
            ".et_pb_text_0",
            ".dsm_open_icon",
            ".dsm_close_icon",
            ".dsm-faq-item-open_icon",
            ".dsm-faq-item-close_icon",
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


def test_clean_root_removes_fixed_ad_wrappers() -> None:
    """Cleanup should strip fixed ad wrappers that sit outside the article body."""

    soup = BeautifulSoup(
        """
        <article>
          <p>Body</p>
          <div class="ad-fixed__wrapper">
            <div>Advertisement</div>
            <a href="/pricing">Go ad free</a>
            <button>Hide</button>
          </div>
        </article>
        """,
        "lxml",
    )

    cleaned = clean_root(soup.article, (".ad-fixed__wrapper",), SKIP_TAGS)

    text = cleaned.get_text(" ", strip=True)

    assert "Advertisement" not in text
    assert "Go ad free" not in text
    assert "Hide" not in text
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
            ".news-form",
            ".article-info",
            ".et_pb_title_meta_container",
            ".et_pb_text_0",
            ".dsm_open_icon",
            ".dsm_close_icon",
            ".dsm-faq-item-open_icon",
            ".dsm-faq-item-close_icon",
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


def test_clean_root_removes_generic_boilerplate_phrases() -> None:
    """Cleanup should drop compact docs and feedback boilerplate blocks."""

    soup = BeautifulSoup(
        """
        <article>
          <div class="docs-feedback">
            Thanks for letting us know this page needs work.
            Help improve this page.
            Learn how to contribute.
          </div>
          <p>Body</p>
        </article>
        """,
        "lxml",
    )

    cleaned = clean_root(soup.article, (), SKIP_TAGS)

    text = cleaned.get_text(" ", strip=True)

    assert "Thanks for letting us know this page needs work" not in text
    assert "Help improve this page" not in text
    assert "Learn how to contribute" not in text
    assert "Body" in text


def test_clean_root_removes_paid_access_cta_and_header_chrome() -> None:
    """Cleanup should remove paid access chrome while keeping article paragraphs."""

    soup = parse_html(ARTICLE_PAID_ACCESS_HTML)
    root = soup.main

    cleaned = clean_root(
        root,
        (
            ".post-head",
            ".post-header",
            ".post-badge",
            ".post-access-cta",
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

    assert "This post is for paid members only" not in text
    assert "Become a paid member for unlimited ad-free access to articles" not in text
    assert "Subscribe" not in text
    assert "blog" not in text
    assert "By Example Author" not in text
    assert "The first article paragraph stays in the body." in text
    assert "The second article paragraph also stays in the body." in text


def test_clean_root_removes_article_skip_link_and_staff_picks_chrome() -> None:
    """Cleanup should remove skip links, comment picks, and staff-picks chrome."""

    soup = parse_html(ARTICLE_ARTICLE_CHROME_HTML)
    root = soup.body

    cleaned = clean_root(
        root,
        (
            "a[href='#main']",
            "a[href='#content']",
            ".story-tools",
            ".text-settings",
            ".text-settings-menu",
            ".text-settings-dropdown-story",
            ".text-settings-dropdown-nav",
            ".comments-wrapper",
            ".comments-picks-list",
            ".staff-picks-title",
            ".wp-forum-connect-comments",
            ".xf_thread_iframe_wrapper",
            ".comment-pick",
            ".single-most-read",
            ".component-most-read",
        ),
        SKIP_TAGS,
    )

    text = cleaned.get_text(" ", strip=True)

    assert "Skip to content" not in text
    assert "Staff Picks" not in text
    assert "Reader comment card content" not in text
    assert "Most Read" not in text
    assert "Body paragraph one stays." in text
    assert "Body paragraph two stays." in text


def test_clean_root_keeps_content_inside_hubspot_row_wrappers() -> None:
    """Cleanup should not delete content just because it lives inside a row wrapper."""

    soup = parse_html(ARTICLE_HUBSPOT_ROW_WRAPPER_HTML)
    root = soup.body

    cleaned = clean_root(
        root,
        (
            "[class*='share']",
            "[id*='share']",
            "[class*='follow']",
            "[class*='social']",
            "[class*='sponsored']",
            "[rel*='sponsored']",
            ".news-form",
            ".article-info",
            ".et_pb_title_meta_container",
            ".et_pb_text_0",
            ".dsm_open_icon",
            ".dsm_close_icon",
            ".dsm-faq-item-open_icon",
            ".dsm-faq-item-close_icon",
            "[class*='note-b']",
            "[class*='dog_two']",
        ),
        SKIP_TAGS,
    )

    text = cleaned.get_text(" ", strip=True)

    assert "Fragnesia (CVE-2026-46300) - Mitigation and Kernel Update" in text
    assert "CloudLinux explains the mitigation and kernel update steps." in text
    assert "Patched kernels and KernelCare livepatches are coming shortly." in text
    assert cleaned.select_one(".tag-list") is None
    assert "CloudLinux" not in text.split("Fragnesia (CVE-2026-46300) - Mitigation and Kernel Update", 1)[0]
    assert "Subscribe" not in text
    assert "Get a Trial" not in text


def test_clean_root_removes_divi_article_info_about_and_faq_icons() -> None:
    """Cleanup should remove article metadata wrappers, about blocks, and FAQ icons."""

    soup = parse_html(ARTICLE_DIVI_ABOUT_AND_FAQ_HTML)
    root = soup.body

    cleaned = clean_root(
        root,
        (
            "[class*='share']",
            "[id*='share']",
            "[class*='follow']",
            "[class*='social']",
            "[class*='sponsored']",
            "[rel*='sponsored']",
            ".news-form",
            ".article-info",
            ".et_pb_title_meta_container",
            ".et_pb_text_0",
            ".dsm_open_icon",
            ".dsm_close_icon",
            ".dsm-faq-item-open_icon",
            ".dsm-faq-item-close_icon",
            "[class*='note-b']",
            "[class*='dog_two']",
        ),
        SKIP_TAGS,
    )

    text = cleaned.get_text(" ", strip=True)

    assert "Blog" not in text
    assert "Example Author" not in text
    assert "Example Interview Story" in text
    assert "K" not in text
    assert "L" not in text
    assert "About ExampleCorp" not in text
    assert "Real body content should remain." in text
    assert "The example answer should remain." in text
