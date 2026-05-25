from __future__ import annotations

from bs4 import BeautifulSoup

from domdown._core import DomdownOptions
from domdown._metadata import extract_metadata, extract_tags


def test_extract_metadata_reads_article_fields() -> None:
    """Metadata extraction should normalize the common article fields."""

    soup = BeautifulSoup(
        """
        <html lang="en">
          <head>
            <meta property="og:title" content="Example Article" />
            <meta property="og:site_name" content="Example Platform" />
            <link rel="canonical" href="https://example.com/posts/example-article" />
            <meta name="author" content="The Hacker News" />
            <meta property="article:published_time" content="2025-12-29T15:14:00+05:30" />
            <meta name="description" content="Example description." />
            <meta property="og:image" content="https://example.com/image.png" />
            <meta property="article:tag" content="Meta Tag A" />
            <meta name="keywords" content="Meta Tag B, Meta Tag C" />
          </head>
          <body>
            <div class="story-meta">
              <a rel="author" href="/authors/example-author">Example Author</a>
            </div>
            <div class="p-tags">Threat Intelligence / Cloud Security</div>
          </body>
        </html>
        """,
        "lxml",
    )

    metadata = extract_metadata(soup, DomdownOptions(base_url="https://example.com", created="2026-05-15"))

    assert metadata.title == "Example Article"
    assert metadata.source == "https://example.com/posts/example-article"
    assert metadata.site_name == "Example Platform"
    assert metadata.author == ("Example Author",)
    assert metadata.published == "2025-12-29T15:14:00+05:30"
    assert metadata.created == "2026-05-15"
    assert metadata.description == "Example description."
    assert metadata.tags == ("Threat Intelligence", "Cloud Security", "Meta Tag A", "Meta Tag B", "Meta Tag C")
    assert metadata.language == "en"
    assert metadata.canonical_url == "https://example.com/posts/example-article"
    assert metadata.image == "https://example.com/image.png"


def test_extract_metadata_strips_site_suffixes_and_resolves_relative_source_against_base_url() -> None:
    """Metadata extraction should clean common site suffixes without inventing fields."""

    soup = BeautifulSoup(
        """
        <html lang="en">
          <head>
            <meta property="og:site_name" content="Example Platform" />
            <meta property="og:title" content="Example Release Note · Example Platform" />
            <meta property="og:url" content="/posts/example-release-note" />
            <meta name="description" content="Example runtime release note." />
          </head>
          <body>
            <article>
              <h1>Example Release Note · Example Platform</h1>
            </article>
          </body>
        </html>
        """,
        "lxml",
    )

    metadata = extract_metadata(soup, DomdownOptions(base_url="https://example.com"))

    assert metadata.title == "Example Release Note"
    assert metadata.source == "https://example.com/posts/example-release-note"
    assert metadata.canonical_url == "https://example.com/posts/example-release-note"
    assert metadata.description == "Example runtime release note."
    assert metadata.site_name == "Example Platform"


def test_extract_metadata_reads_visible_published_time_when_meta_is_missing() -> None:
    """Published time should fall back to a visible datetime when no meta tag exists."""

    soup = BeautifulSoup(
        """
        <html lang="en">
          <head>
            <meta property="og:site_name" content="Example News" />
            <meta property="og:title" content="Example Alert Title · Example News" />
            <meta property="og:url" content="https://example.com/news/example-alert" />
          </head>
          <body>
            <div class="c-page-title__fields">
              <div class="c-field c-field--name-field-release-date c-field--type-datetime c-field--label-above">
                <div class="c-field__label">Release Date</div>
                <div class="c-field__content"><time datetime="2026-03-03T12:00:00Z">March 03, 2026</time></div>
              </div>
            </div>
            <div class="l-page-section l-page-section--rich-text csaf-imported">
              <div class="l-page-section__content">
                <p>Example alert content.</p>
              </div>
            </div>
          </body>
        </html>
        """,
        "lxml",
    )

    metadata = extract_metadata(soup, DomdownOptions())

    assert metadata.title == "Example Alert Title"
    assert metadata.source == "https://example.com/news/example-alert"
    assert metadata.published == "2026-03-03T12:00:00Z"


def test_extract_metadata_prefers_visible_author_and_combines_tags() -> None:
    """Visible article metadata should stay primary while tags are combined."""

    soup = BeautifulSoup(
        """
        <html lang="en">
          <head>
            <meta property="og:title" content="Example Article" />
            <meta name="author" content="Meta Author" />
            <meta name="keywords" content="Meta Tag A, Meta Tag B" />
          </head>
          <body>
            <article>
              <header>
                <div class="postmeta">
                  <a rel="author" href="/authors/example-author">Visible Author</a>
                </div>
              </header>
              <div class="single-tags">Visible Tag A / Visible Tag B</div>
            </article>
          </body>
        </html>
        """,
        "lxml",
    )

    metadata = extract_metadata(soup, DomdownOptions())

    assert metadata.author == ("Visible Author",)
    assert metadata.tags == ("Visible Tag A", "Visible Tag B", "Meta Tag A", "Meta Tag B")


def test_extract_metadata_can_prefer_metadata_author_without_affecting_tag_combination() -> None:
    """Author priority should be configurable without changing tag extraction."""

    soup = BeautifulSoup(
        """
        <html lang="en">
          <head>
            <meta property="og:title" content="Example Article" />
            <meta name="author" content="The Hacker News" />
          </head>
          <body>
            <article>
              <div class="postmeta">
                <a rel="author" href="/authors/example-author">Visible Author</a>
              </div>
              <div class="tags">
                <a rel="tag" href="/tags/a">Tag A</a>,
                <a rel="tag" href="/tags/b">Tag B</a>
              </div>
            </article>
          </body>
        </html>
        """,
        "lxml",
    )

    metadata = extract_metadata(soup, DomdownOptions(author_priority="metadata"))

    assert metadata.author == ("The Hacker News",)
    assert metadata.tags == ("Tag A", "Tag B")


def test_extract_tags_combines_visible_tags_and_metadata() -> None:
    """Tag extraction should combine visible tag blocks with metadata and deduplicate tokens."""

    soup = BeautifulSoup(
        """
        <html lang="en">
          <head>
            <meta name="keywords" content="Meta Tag A, Meta Tag B" />
            <meta property="article:tag" content="Meta Tag A, Meta Tag C" />
          </head>
          <body>
            <div class="tags">
              <a rel="tag" href="/tags/a">Visible Tag A</a>,
              <a rel="tag" href="/tags/b">Visible Tag B</a>,
              <a rel="tag" href="/tags/a">Visible Tag A</a>
            </div>
          </body>
        </html>
        """,
        "lxml",
    )

    assert extract_tags(soup) == ("Visible Tag A", "Visible Tag B", "Meta Tag A", "Meta Tag C", "Meta Tag B")


def test_extract_tags_uses_metadata_when_visible_tags_are_absent() -> None:
    """Tag extraction should use metadata when visible tags are not present."""

    soup = BeautifulSoup(
        """
        <html lang="en">
          <head>
            <meta name="keywords" content="Meta Tag A, Meta Tag B" />
            <meta property="article:section" content="Meta Tag C" />
          </head>
          <body>
            <article><p>Body only.</p></article>
          </body>
        </html>
        """,
        "lxml",
    )

    assert extract_tags(soup) == ("Meta Tag A", "Meta Tag B", "Meta Tag C")
