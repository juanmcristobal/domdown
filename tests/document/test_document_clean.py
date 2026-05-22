from __future__ import annotations

from bs4 import BeautifulSoup

from domdown._constants import SKIP_TAGS
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


def test_clean_root_removes_html_comments() -> None:
    """Cleanup should drop HTML comments like more markers."""

    soup = BeautifulSoup("<article><!--more--><p>Content</p></article>", "lxml")

    cleaned = clean_root(soup.article, (), SKIP_TAGS)

    assert "more" not in cleaned.get_text(" ", strip=True)
    assert "Content" in cleaned.get_text(" ", strip=True)
