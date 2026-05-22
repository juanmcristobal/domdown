from __future__ import annotations

from textwrap import dedent

from domdown import DomdownOptions, html_to_markdown


def test_html_to_markdown_renders_document_with_frontmatter() -> None:
    html = dedent(
        """
        <html lang="en">
          <head>
            <title>Example Article</title>
            <link rel="canonical" href="https://example.com/posts/example-article" />
            <meta name="author" content="The Hacker News" />
            <meta name="description" content="Example description." />
            <meta itemprop="datePublished" content="2025-12-29T15:14:00+05:30" />
          </head>
          <body>
            <div class="post-body">
              <div class="post-head">
                <h1 class="story-title">
                  <a href="https://example.com/posts/example-article">Example Article</a>
                </h1>
                <div class="postmeta">
                  <span class="p-author">
                    <span class="author">Ravie Lakshmanan</span>
                    <span class="author">Dec 29, 2025</span>
                  </span>
                  <span class="p-tags">Threat Intelligence / Cloud Security</span>
                </div>
              </div>
              <div class="articlebody clear cf" id="articlebody">
                <p>Cybersecurity researchers disclosed details of a campaign.</p>
                <p>Researchers Nicholas Anderson and Kirill Boychenko <a href="https://example.com/source">said</a>.</p>
                <p>The names of the packages are listed below -</p>
                <ul>
                  <li>secure-docs-app</li>
                  <li>sync365</li>
                </ul>
                <div class="separator">
                  <a href="https://example.com/image.png">
                    <img alt="" data-src="https://example.com/image.png" />
                  </a>
                </div>
                <p>To counter the risk posed by the threat.</p>
              </div>
              <div class="tags">Cloud security , Credential Theft</div>
            </div>
          </body>
        </html>
        """
    ).strip()

    output = html_to_markdown(html, DomdownOptions(created="2026-05-15"))

    expected = dedent(
        """
        ---
        title: Example Article
        source: "https://example.com/posts/example-article"
        author:
          - "The Hacker News"
        published: "2025-12-29T15:14:00+05:30"
        created: 2026-05-15
        description: Example description.
        tags:
          - Threat Intelligence
          - Cloud Security
        ---
        Cybersecurity researchers disclosed details of a campaign.

        Researchers Nicholas Anderson and Kirill Boychenko [said](https://example.com/source).

        The names of the packages are listed below -

        - secure-docs-app
        - sync365

        [![](https://example.com/image.png)](https://example.com/image.png)

        To counter the risk posed by the threat.
        """
    ).strip()

    assert output == expected
