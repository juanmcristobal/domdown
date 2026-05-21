"""Tests for X (Twitter) Article surrogate pair repair.

Verifies that emojis split across element boundaries (surrogate pairs)
are correctly repaired in article content.

NOTE: These tests are skipped because BeautifulSoup with lxml cannot
parse surrogate characters directly. The TypeScript implementation uses
linkedom which handles surrogates differently. This behavior would
need to be tested in a different way or using a different parser.
"""

from domdown import Domdown, DomdownOptions
from domdown.utils.dom import parse_html

# 🔄 (U+1F504) split into high surrogate \uD83D and low surrogate \uDD04
HIGH = "\ud83d"
LOW = "\udd04"


class TestXArticleSurrogatePairRepair:
    """Tests for emoji surrogate pair repair in X Article content.

    These tests are skipped because BeautifulSoup with lxml cannot
    handle lone surrogate characters in HTML. This is a fundamental
    difference between the Python (BS4/lxml) and TypeScript (linkedom)
    DOM implementations.
    """

    def test_repairs_emoji_split_across_bold_span_boundary(self) -> None:
        """Emoji split across bold span boundary should be repaired."""
        html = f"""
        <html><head><title>Test Article</title></head>
        <body>
            <div data-testid="twitterArticleRichTextView">
                <h1 data-testid="twitter-article-title">Test Article</h1>
                <div class="public-DraftStyleDefault-block">Refresh {HIGH}<span style="font-weight: bold">{LOW} updates</span> daily</div>
            </div>
        </body></html>
        """
        doc = parse_html(html)
        result = Domdown(doc, DomdownOptions(url="https://x.com/testuser/article/123456789")).parse()

        assert "🔄" in result.content
        import json

        json.dumps(result.content)  # should not throw

    def test_repairs_emoji_split_across_link_boundary(self) -> None:
        """Emoji split across link boundary should be repaired."""
        html = f"""
        <html><head><title>Test Article</title></head>
        <body>
            <div data-testid="twitterArticleRichTextView">
                <h1 data-testid="twitter-article-title">Test Article</h1>
                <div class="public-DraftStyleDefault-block">See {HIGH}<a href="https://example.com">{LOW}here</a></div>
            </div>
        </body></html>
        """
        doc = parse_html(html)
        result = Domdown(doc, DomdownOptions(url="https://x.com/testuser/article/123456789")).parse()

        import json

        json.dumps(result.content)  # should not throw

    def test_preserves_intact_emojis_unchanged(self) -> None:
        """Intact emojis should remain unchanged."""
        html = """
        <html><head><title>Test Article</title></head>
        <body>
            <div data-testid="twitterArticleRichTextView">
                <h1 data-testid="twitter-article-title">Test Article</h1>
                <div class="public-DraftStyleDefault-block">Refresh 🔄 daily</div>
            </div>
        </body></html>
        """
        doc = parse_html(html)
        result = Domdown(doc, DomdownOptions(url="https://x.com/testuser/article/123456789")).parse()

        assert "🔄" in result.content
        import json

        json.dumps(result.content)  # should not throw
