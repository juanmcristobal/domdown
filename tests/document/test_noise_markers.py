from pathlib import Path

from domdown import DomdownOptions, html_to_markdown
from domdown._constants.selectors import NOISE_MARKERS


class TestNoiseMarkers:
    """Tests for defuddle noise markers integration."""

    def test_defuddle_noise_markers_added(self):
        """Test that defuddle noise markers are defined in NOISE_MARKERS."""
        defuddle_markers = [
            "read-more",
            "article-card",
            "post-meta",
            "article-actions",
            "post-actions",
            "byline",
            "author-block",
            "meta-info",
            "sidebar",
            "aside",
            "related-posts",
            "related-content",
            "promo-box",
            "sponsor-box",
            "ad-box",
            "promo-block",
        ]

        for marker in defuddle_markers:
            assert marker in NOISE_MARKERS, f"{marker} not in NOISE_MARKERS"

    def test_read_more_marker_removal(self):
        """Test that 'read-more' marker elements are removed."""
        html = """
        <html>
          <body>
            <article>
              <h1>Main Article</h1>
              <p>Main article content here.</p>
            </article>
            <div class="read-more">
              <a href="/other">Read more</a>
            </div>
          </body>
        </html>
        """

        result = html_to_markdown(html, DomdownOptions(base_url="https://example.com/test"))

        assert "Main Article" in result
        assert "Main article content here" in result
        assert "Read more" not in result

    def test_article_card_removal(self):
        """Test that 'article-card' elements are removed."""
        html = """
        <html>
          <body>
            <main>
              <h1>Real Article</h1>
              <p>Real article content.</p>
            </main>
            <div class="article-card">
              <h2>Related Article</h2>
              <p>Not our content.</p>
            </div>
          </body>
        </html>
        """

        result = html_to_markdown(html, DomdownOptions(base_url="https://example.com/test"))

        assert "Real Article" in result
        assert "Real article content" in result
        assert "Related Article" not in result

    def test_post_meta_removal(self):
        """Test that 'post-meta' elements are removed."""
        html = """
        <html>
          <body>
            <article>
              <div class="post-meta">
                <span>Author: John</span>
                <span>Date: 2024</span>
              </div>
              <h1>Post Title</h1>
              <p>Post content.</p>
            </article>
          </body>
        </html>
        """

        result = html_to_markdown(html, DomdownOptions(base_url="https://example.com/test"))

        assert "Post Title" in result
        assert "Post content" in result
        assert "Author: John" not in result

    def test_sidebar_removal(self):
        """Test that 'sidebar' elements are removed."""
        html = """
        <html>
          <body>
            <main>
              <h1>Main Content</h1>
              <p>Main article.</p>
            </main>
            <aside class="sidebar">
              <h2>Sidebar</h2>
              <p>Sidebar content to remove.</p>
            </aside>
          </body>
        </html>
        """

        result = html_to_markdown(html, DomdownOptions(base_url="https://example.com/test"))

        assert "Main Content" in result
        assert "Main article" in result
        assert "Sidebar" not in result

    def test_related_posts_removal(self):
        """Test that 'related-posts' elements are removed."""
        html = """
        <html>
          <body>
            <article>
              <h1>Article</h1>
              <p>Article content.</p>
            </article>
            <div class="related-posts">
              <h2>Related</h2>
              <a href="/other">Other post</a>
            </div>
          </body>
        </html>
        """

        result = html_to_markdown(html, DomdownOptions(base_url="https://example.com/test"))

        assert "Article" in result
        assert "Article content" in result
        assert "Related" not in result

    def test_multiple_markers_removal(self):
        """Test that multiple noise markers are removed simultaneously."""
        html = """
        <html>
          <body>
            <main>
              <h1>Real Content</h1>
              <p>Real article content here.</p>
            </main>
            <div class="read-more">Read more</div>
            <div class="article-card">Article card</div>
            <aside class="sidebar">Sidebar</aside>
            <div class="post-meta">Meta info</div>
          </body>
        </html>
        """

        result = html_to_markdown(html, DomdownOptions(base_url="https://example.com/test"))

        assert "Real Content" in result
        assert "Real article content here" in result
        assert "Read more" not in result
        assert "Article card" not in result
        assert "Sidebar" not in result
        assert "Meta info" not in result

    def test_noise_markers_do_not_remove_valid_content(self):
        """Test that noise markers don't remove legitimate content."""
        html = """
        <html>
          <body>
            <article>
              <h1>Important Article</h1>
              <p>This discusses read-more patterns in modern web design.</p>
              <p>It's valid prose that should be preserved.</p>
            </article>
          </body>
        </html>
        """

        result = html_to_markdown(html, DomdownOptions(base_url="https://example.com/test"))

        assert "Important Article" in result
        assert "This discusses read-more patterns" in result
        assert "modern web design" in result
        assert "valid prose that should be preserved" in result

    def test_regression_existing_noise_markers_still_work(self):
        """Test that existing noise markers still function correctly."""
        html = """
        <html>
          <body>
            <article>
              <h1>Article</h1>
              <p>Article content.</p>
            </article>
            <div class="share-widget">Share this</div>
            <div class="social-links">Social media</div>
            <div class="newsletter">Subscribe</div>
            <footer class="footer">Footer content</footer>
          </body>
        </html>
        """

        result = html_to_markdown(html, DomdownOptions(base_url="https://example.com/test"))

        assert "Article" in result
        assert "Article content" in result
        assert "Share this" not in result
        assert "Social media" not in result
        assert "Subscribe" not in result
        assert "Footer content" not in result
