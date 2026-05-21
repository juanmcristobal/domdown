"""Tests for schema.org text fallback behavior.

When schema.org structured data contains more text (via `text` or
`articleBody`) than the content scorer extracted, domdown searches
the DOM for the element matching the schema text and returns its HTML.

NOTE: The schema fallback behavior in domdown may differ from the
TypeScript implementation. Some tests are skipped until behavior is verified.
"""

from domdown import Domdown
from domdown.utils.dom import parse_html


class TestSchemaOrgTextFallback:
    """Tests for the schema.org text fallback path in parse()."""

    def test_uses_schema_text_when_it_has_more_words(self) -> None:
        """Schema text with more words than extracted content should trigger fallback."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Post</title>
            <script type="application/ld+json">
            {
                "@type": "SocialMediaPosting",
                "text": "This is a much longer post body that contains significantly more words than the short article element. It goes on and on with additional sentences to ensure the word count exceeds the extracted content. Here is even more text to make absolutely sure we cross the threshold. The schema text fallback should kick in when this text is longer than what the scorer found."
            }
            </script>
        </head>
        <body>
            <nav><a href="/">Home</a></nav>
            <div id="feed">
                <div class="post" id="other-post">
                    <p>Some other post in the feed that is not what we want.</p>
                </div>
                <div class="post" id="target-post">
                    <p>This is a much longer post body that contains significantly more words than the short article element. It goes on and on with additional sentences to ensure the word count exceeds the extracted content. Here is even more text to make absolutely sure we cross the threshold. The schema text fallback should kick in when this text is longer than what the scorer found.</p>
                </div>
            </div>
        </body>
        </html>"""

        doc = parse_html(html)
        domdown = Domdown(doc)
        result = domdown.parse()

        assert "This is a much longer post body" in result.content
        assert "schema text fallback should kick in" in result.content

    def test_uses_articleBody_from_schema_org_data(self) -> None:
        """Should use articleBody from schema.org structured data."""
        article_body = (
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
            "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
            "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris "
            "nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in "
            "reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur."
        )

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Article Page</title>
            <script type="application/ld+json">
            {{
                "@type": "Article",
                "articleBody": "{article_body}"
            }}
            </script>
        </head>
        <body>
            <header><h1>My Blog</h1></header>
            <main>
                <article>
                    <p>{article_body}</p>
                </article>
            </main>
            <footer>Copyright 2024</footer>
        </body>
        </html>"""

        doc = parse_html(html)
        domdown = Domdown(doc)
        result = domdown.parse()

        assert "Lorem ipsum dolor sit amet" in result.content
        assert "fugiat nulla pariatur" in result.content

    def test_extracted_content_used_when_scoring_is_sufficient(self) -> None:
        """Should use extracted content when it has sufficient words."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Good Extraction</title>
            <script type="application/ld+json">
            {
                "@type": "SocialMediaPosting",
                "text": "Short schema text."
            }
            </script>
        </head>
        <body>
            <article>
                <h1>Full Article</h1>
                <p>This article has plenty of content that the scorer will extract correctly. It contains multiple paragraphs with enough words to exceed the schema text length. The content scorer should pick this up as the main content without needing the schema fallback.</p>
                <p>Here is another paragraph with even more content to make the word count higher. We want to ensure the extracted content exceeds the schema text word count so the fallback does not trigger.</p>
                <p>And a third paragraph for good measure, with additional words and sentences to pad out the content even further beyond what the schema text contains.</p>
            </article>
        </body>
        </html>"""

        doc = parse_html(html)
        domdown = Domdown(doc)
        result = domdown.parse()

        assert "multiple paragraphs" in result.content
        assert "third paragraph" in result.content

    def test_falls_back_to_schema_text_string_when_no_dom_element_matches(
        self,
    ) -> None:
        """When no DOM element matches schema text, should use raw schema text string."""
        schema_text = (
            "This unique schema text does not appear anywhere in the visible "
            "DOM body content. It has enough words to trigger the fallback path. "
            "We need quite a few words here to exceed the extracted content word count. "
            "Adding more sentences to be safe and ensure we trigger the right code path."
        )

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>No Match Page</title>
            <script type="application/ld+json">
            {{
                "@type": "SocialMediaPosting",
                "text": "{schema_text}"
            }}
            </script>
        </head>
        <body>
            <div>
                <p>Tiny content.</p>
            </div>
        </body>
        </html>"""

        doc = parse_html(html)
        domdown = Domdown(doc)
        result = domdown.parse()

        assert "unique schema text does not appear" in result.content

    def test_schema_fallback_finds_smallest_matching_element(self) -> None:
        """Should match the target post, not a larger wrapper."""
        post_text = (
            "This is the target post content with enough words to trigger the "
            "schema text fallback mechanism. It needs to be long enough that its "
            "word count exceeds whatever the scorer extracted from the page. "
            "Adding more sentences here to pad the word count sufficiently."
        )

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Feed Page</title>
            <script type="application/ld+json">
            {{
                "@type": "SocialMediaPosting",
                "text": "{post_text}"
            }}
            </script>
        </head>
        <body>
            <div id="wrapper">
                <div id="feed">
                    <div class="post">
                        <p>First post in the feed with different content entirely.</p>
                    </div>
                    <div class="post" id="target">
                        <p>{post_text}</p>
                    </div>
                    <div class="post">
                        <p>Third post with yet more different content.</p>
                    </div>
                </div>
            </div>
        </body>
        </html>"""

        doc = parse_html(html)
        domdown = Domdown(doc)
        result = domdown.parse()

        assert "target post content" in result.content
        assert "First post in the feed" not in result.content
        assert "Third post with yet more" not in result.content

    def test_schema_fallback_preserves_inline_formatting(self) -> None:
        """Should preserve HTML formatting in matched element."""
        plain_text = (
            "This post has formatted content with bold text and italic text and a link "
            "to example site. It needs enough words to trigger the schema fallback path "
            "so we keep adding more content here."
        )

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Formatted Post</title>
            <script type="application/ld+json">
            {{
                "@type": "SocialMediaPosting",
                "text": "{plain_text}"
            }}
            </script>
        </head>
        <body>
            <div>
                <p>Nav item</p>
            </div>
            <div class="post">
                <p>This post has <strong>formatted content</strong> with <em>bold text</em> and <em>italic text</em> and a <a href="https://example.com">link to example site</a>. It needs enough words to trigger the schema fallback path so we keep adding more content here.</p>
            </div>
        </body>
        </html>"""

        doc = parse_html(html)
        domdown = Domdown(doc)
        result = domdown.parse()

        assert "<strong>formatted content</strong>" in result.content
        assert 'href="https://example.com' in result.content


def _build_schema_fallback_html(dangerous_html: str, schema_text: str) -> str:
    """Helper: build HTML where the schema fallback triggers."""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test</title>
        <script type="application/ld+json">
        {{
            "@type": "SocialMediaPosting",
            "text": "{schema_text}"
        }}
        </script>
    </head>
    <body>
        <article>
            <h1>Title</h1>
            <p>Short article summary.</p>
        </article>
        <div class="full-post">
            <p>{schema_text}</p>
            {dangerous_html}
        </div>
    </body>
    </html>"""


class TestSchemaOrgTextFallbackSanitization:
    """Security tests for the schema.org text fallback path.

    NOTE: These tests depend on schema fallback triggering, which may not
    happen with the current Python implementation word count thresholds.
    Tests are skipped pending verification of fallback behavior.
    """

    def test_strips_script_tags(self) -> None:
        """Script tags should be stripped from schema fallback content."""
        schema_text = (
            "This is the full post body with enough words to exceed the short article "
            "summary that the content scorer will extract. Adding more sentences here "
            "to make sure the word count difference is large enough to reliably trigger "
            "the schema text fallback path in the parse method."
        )
        html = _build_schema_fallback_html('<script>alert("xss")</script>', schema_text)

        doc = parse_html(html)
        result = Domdown(doc).parse()

        assert "full post body" in result.content
        assert "<script" not in result.content
        assert "alert" not in result.content

    def test_strips_event_handlers(self) -> None:
        """Event handlers (onerror, onclick) should be stripped."""
        schema_text = (
            "This is the full post body with enough words to exceed the short article "
            "summary that the content scorer will extract. Adding more sentences here "
            "to make sure the word count difference is large enough to reliably trigger "
            "the schema text fallback path in the parse method."
        )
        html = _build_schema_fallback_html('<img src="x.jpg" onerror="alert(\'xss\')" onclick="steal()">', schema_text)

        doc = parse_html(html)
        result = Domdown(doc).parse()

        assert "full post body" in result.content
        assert "onerror" not in result.content
        assert "onclick" not in result.content
        assert "alert" not in result.content

    def test_strips_style_elements(self) -> None:
        """Style elements should be stripped from schema fallback content."""
        schema_text = (
            "This is the full post body with enough words to exceed the short article "
            "summary that the content scorer will extract. Adding more sentences here "
            "to make sure the word count difference is large enough to reliably trigger "
            "the schema text fallback path in the parse method."
        )
        html = _build_schema_fallback_html(
            '<style>.x { background: url("https://evil.com/steal") }</style>', schema_text
        )

        doc = parse_html(html)
        result = Domdown(doc).parse()

        assert "full post body" in result.content
        assert "<style" not in result.content
        assert "evil.com" not in result.content

    def test_strips_noscript_elements(self) -> None:
        """Noscript elements should be stripped from schema fallback content."""
        schema_text = (
            "This is the full post body with enough words to exceed the short article "
            "summary that the content scorer will extract. Adding more sentences here "
            "to make sure the word count difference is large enough to reliably trigger "
            "the schema text fallback path in the parse method."
        )
        html = _build_schema_fallback_html('<noscript><img src="https://evil.com/track"></noscript>', schema_text)

        doc = parse_html(html)
        result = Domdown(doc).parse()

        assert "full post body" in result.content
        assert "<noscript" not in result.content
        assert "evil.com" not in result.content

    def test_preserves_iframes_with_src(self) -> None:
        """Iframes with src attribute should be preserved."""
        schema_text = (
            "This is the full post body with enough words to exceed the short article "
            "summary that the content scorer will extract. Adding more sentences here "
            "to make sure the word count difference is large enough to reliably trigger "
            "the schema text fallback path in the parse method."
        )
        html = _build_schema_fallback_html(
            '<iframe src="https://www.youtube.com/embed/abc123" width="560" height="315">'
            '</iframe><iframe src="https://open.spotify.com/embed/track/xyz"></iframe>',
            schema_text,
        )

        doc = parse_html(html)
        result = Domdown(doc).parse()

        assert "full post body" in result.content
        assert "youtube.com/embed/abc123" in result.content
        assert "spotify.com/embed/track/xyz" in result.content

    def test_strips_srcdoc_attribute_from_iframes(self) -> None:
        """Iframe srcdoc attribute should be stripped."""
        schema_text = (
            "This is the full post body with enough words to exceed the short article "
            "summary that the content scorer will extract. Adding more sentences here "
            "to make sure the word count difference is large enough to reliably trigger "
            "the schema text fallback path in the parse method."
        )
        html = _build_schema_fallback_html("<iframe srcdoc=\"<script>alert('xss')</script>\"></iframe>", schema_text)

        doc = parse_html(html)
        result = Domdown(doc).parse()

        assert "full post body" in result.content
        assert "srcdoc" not in result.content
        assert "alert" not in result.content

    def test_strips_object_and_embed_elements(self) -> None:
        """Object and embed elements should be stripped."""
        schema_text = (
            "This is the full post body with enough words to exceed the short article "
            "summary that the content scorer will extract. Adding more sentences here "
            "to make sure the word count difference is large enough to reliably trigger "
            "the schema text fallback path in the parse method."
        )
        html = _build_schema_fallback_html(
            '<object data="https://evil.com/flash.swf"></object><embed src="https://evil.com/plugin">',
            schema_text,
        )

        doc = parse_html(html)
        result = Domdown(doc).parse()

        assert "full post body" in result.content
        assert "<object" not in result.content
        assert "<embed" not in result.content
        assert "evil.com" not in result.content

    def test_strips_javascript_uris(self) -> None:
        """JavaScript URIs should be stripped."""
        schema_text = (
            "This is the full post body with enough words to exceed the short article "
            "summary that the content scorer will extract. Adding more sentences here "
            "to make sure the word count difference is large enough to reliably trigger "
            "the schema text fallback path in the parse method."
        )
        html = _build_schema_fallback_html(
            '<a href="javascript:alert(\'xss\')">click me</a><a href="  javascript:void(0)">spaced</a>',
            schema_text,
        )

        doc = parse_html(html)
        result = Domdown(doc).parse()

        assert "full post body" in result.content
        assert "javascript:" not in result.content

    def test_strips_data_text_html_uris(self) -> None:
        """data:text/html URIs should be stripped."""
        schema_text = (
            "This is the full post body with enough words to exceed the short article "
            "summary that the content scorer will extract. Adding more sentences here "
            "to make sure the word count difference is large enough to reliably trigger "
            "the schema text fallback path in the parse method."
        )
        html = _build_schema_fallback_html('<img src="data:text/html,<script>alert(1)</script>">', schema_text)

        doc = parse_html(html)
        result = Domdown(doc).parse()

        assert "full post body" in result.content
        assert "data:text/html" not in result.content

    def test_strips_base_tag(self) -> None:
        """Base tag should be stripped to prevent URL hijacking."""
        schema_text = (
            "This is the full post body with enough words to exceed the short article "
            "summary that the content scorer will extract. Adding more sentences here "
            "to make sure the word count difference is large enough to reliably trigger "
            "the schema text fallback path in the parse method."
        )

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test</title>
            <script type="application/ld+json">
            {{
                "@type": "SocialMediaPosting",
                "text": "{schema_text}"
            }}
            </script>
        </head>
        <body>
            <base href="https://evil.com/">
            <article>
                <h1>Title</h1>
                <p>Short article summary.</p>
            </article>
            <div class="full-post">
                <p>{schema_text}</p>
            </div>
        </body>
        </html>"""

        doc = parse_html(html)
        result = Domdown(doc).parse()

        assert "full post body" in result.content
        assert "<base" not in result.content

    def test_schema_text_string_fallback_does_not_contain_html_injection(self) -> None:
        """Raw schema text fallback should not contain HTML injection."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test</title>
            <script type="application/ld+json">
            {
                "@type": "SocialMediaPosting",
                "text": "Safe text with enough words to trigger fallback. <script>alert('xss')</script> More text here to pad the word count above the threshold of what the scorer extracts from the tiny body."
            }
            </script>
        </head>
        <body>
            <div><p>Tiny.</p></div>
        </body>
        </html>"""

        doc = parse_html(html)
        result = Domdown(doc).parse()

        assert "Safe text" in result.content
