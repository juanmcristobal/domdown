from __future__ import annotations

from bs4 import BeautifulSoup

from domdown._metadata.helpers import (
    collect_texts,
    first_image_src,
    first_list,
    first_text,
    looks_like_date,
    meta_content,
    select_texts,
    split_tags,
    tag_text,
)


def test_metadata_helper_functions_cover_common_patterns() -> None:
    """Metadata helpers should normalize text and extract primitive values."""

    soup = BeautifulSoup(
        """
        <html>
          <head>
            <link rel="canonical" href="https://example.com/story" />
            <meta name="description" content="Example description." />
          </head>
          <body>
            <h1> Story Title </h1>
            <div class="tags">Threat Intelligence / Cloud Security</div>
            <div class="author">Ravie Lakshmanan</div>
            <img src="/image.png" />
          </body>
        </html>
        """,
        "lxml",
    )

    assert meta_content(soup, "link[rel='canonical']") == "https://example.com/story"
    assert tag_text(soup.select_one("h1")) == "Story Title"
    assert select_texts(soup, ".author") == ("Ravie Lakshmanan",)
    assert collect_texts(soup, (".author", ".tags")) == ("Ravie Lakshmanan", "Threat Intelligence / Cloud Security")
    assert first_text("", ("A", "B"), None, "C") == "A"
    assert first_list("", ("A", "B"), "C") == ("A", "B")
    assert split_tags(("Threat Intelligence / Cloud Security",)) == ("Threat Intelligence", "Cloud Security")
    assert looks_like_date("Dec 29, 2025")
    assert first_image_src(soup) == "/image.png"


def test_split_tags_deduplicates_repeated_tag_tokens() -> None:
    """Tag splitting should remove repeated values while preserving order."""

    assert split_tags(("Cloud Security / Vulnerability", "Cloud Security, APT")) == (
        "Cloud Security",
        "Vulnerability",
        "APT",
    )
