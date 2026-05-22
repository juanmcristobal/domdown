from __future__ import annotations

from bs4 import BeautifulSoup

from domdown._core import DomdownOptions
from domdown._metadata import extract_metadata


def test_extract_metadata_reads_article_fields() -> None:
    """Metadata extraction should normalize the common article fields."""

    soup = BeautifulSoup(
        """
        <html lang="en">
          <head>
            <meta property="og:title" content="Example Article" />
            <link rel="canonical" href="https://example.com/posts/example-article" />
            <meta name="author" content="The Hacker News" />
            <meta property="article:published_time" content="2025-12-29T15:14:00+05:30" />
            <meta name="description" content="Example description." />
            <meta property="og:image" content="https://example.com/image.png" />
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
    assert metadata.author == ("Example Author",)
    assert metadata.published == "2025-12-29T15:14:00+05:30"
    assert metadata.created == "2026-05-15"
    assert metadata.description == "Example description."
    assert metadata.tags == ("Threat Intelligence", "Cloud Security")
    assert metadata.language == "en"
    assert metadata.canonical_url == "https://example.com/posts/example-article"
    assert metadata.image == "https://example.com/image.png"


def test_extract_metadata_prefers_visible_author_and_tags() -> None:
    """Visible article metadata should win over generic HTML metatags."""

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
    assert metadata.tags == ("Visible Tag A", "Visible Tag B")
