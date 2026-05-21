from domdown import DomdownOptions
from domdown.node import parse

SIMPLE_HTML = """<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
<article>
<p>Yey!<img src="https://example.com/img.png" alt="IMG"></p>
</article>
</body>
</html>"""


class TestExclamationMark:
    def test_space_between_exclamation_and_image(self):
        html = SIMPLE_HTML
        result = parse(html, "https://example.com", DomdownOptions(separate_markdown=True))

        assert "! ![IMG]" in result.content_markdown
        assert "!![" not in result.content_markdown

    def test_space_between_exclamation_and_linked_image(self):
        html = (
            "<html><head><title>Test</title></head>"
            '<body><article><p>Hello!<a href="https://example.com">'
            '<img src="https://example.com/img.png" alt="photo"></a></p>'
            "</article></body></html>"
        )
        result = parse(html, "https://example.com", DomdownOptions(separate_markdown=True))

        assert "! [![photo]" in result.content_markdown
        assert "![![photo]" not in result.content_markdown

    def test_normal_image_syntax_unchanged(self):
        html = (
            "<html><head><title>Test</title></head>"
            "<body><article><p>Hello world</p>"
            '<img src="https://example.com/img.png" alt="photo"></article>'
            "</body></html>"
        )
        result = parse(html, "https://example.com", DomdownOptions(separate_markdown=True))

        assert "![photo](https://example.com/img.png)" in result.content_markdown

    def test_exclamation_not_before_image_unchanged(self):
        html = (
            "<html><head><title>Test</title></head><body><article><p>Hello! This is great!</p></article></body></html>"
        )
        result = parse(html, "https://example.com", DomdownOptions(separate_markdown=True))

        assert "Hello! This is great!" in result.content_markdown


class TestBaseHrefResolution:
    def test_resolve_relative_urls_against_base_href(self):
        html = (
            "<html><head><title>Test</title>"
            '<base href="/html/2312.00752v2/">'
            "</head><body><article><p>Content</p>"
            '<img src="x1.png"></article></body></html>'
        )
        result = parse(
            html,
            "https://arxiv.org/html/2312.00752",
            DomdownOptions(separate_markdown=True),
        )

        assert "https://arxiv.org/html/2312.00752v2/x1.png" in result.content

    def test_fallback_to_document_url_without_base_href(self):
        html = (
            "<html><head><title>Test</title></head>"
            "<body><article><p>Content</p>"
            '<img src="x1.png"></article></body></html>'
        )
        result = parse(
            html,
            "https://arxiv.org/html/2312.00752",
            DomdownOptions(separate_markdown=True),
        )

        assert "https://arxiv.org/html/x1.png" in result.content


class TestWbrHandling:
    def test_wbr_removed_without_spaces(self):
        html = (
            "<html><head><title>Test</title></head>"
            "<body><article><p>Super<wbr>cali<wbr>fragilistic</p>"
            "</article></body></html>"
        )
        result = parse(html, "https://example.com", DomdownOptions(separate_markdown=True))

        assert "Supercalifragilistic" in result.content_markdown or "Super" in result.content_markdown

    def test_wbr_inside_links(self):
        html = (
            "<html><head><title>Test</title></head>"
            '<body><article><p><a href="https://example.com">long<wbr>word</a></p>'
            "</article></body></html>"
        )
        result = parse(html, "https://example.com", DomdownOptions(separate_markdown=True))

        assert "longword" in result.content_markdown or "long" in result.content_markdown
