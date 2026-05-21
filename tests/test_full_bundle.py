import pytest
from bs4 import BeautifulSoup

from domdown import DomdownOptions
from domdown.domdown import Domdown
from domdown.markdown import to_markdown

SIMPLE_HTML = """<!DOCTYPE html>
<html>
<head><title>Test Page</title></head>
<body>
<article>
<h1>Test Article</h1>
<p>This is a <strong>test</strong> paragraph with some content that should be long enough to pass the scoring threshold for content extraction.</p>
<p>Another paragraph here with more content to ensure the article is detected as main content by the domdown algorithm.</p>
<p>Third paragraph adds even more content to make sure we have plenty of words for the scoring algorithm to work with.</p>
</article>
</body>
</html>
"""


@pytest.fixture
def doc():
    return BeautifulSoup(SIMPLE_HTML, "lxml")


@pytest.fixture
def url():
    return "https://example.com"


class TestFullBundleMarkdown:
    def test_markdown_true_converts_to_markdown(self, doc, url):
        opts = DomdownOptions(markdown=True, url=url)
        domdown = Domdown(doc, opts)
        result = domdown.parse()
        to_markdown(result, opts, url)

        assert "<p>" not in result.content
        assert "<strong>" not in result.content
        assert "**test**" in result.content

    def test_separate_markdown_keeps_html_populates_markdown(self, doc, url):
        opts = DomdownOptions(separate_markdown=True, url=url)
        domdown = Domdown(doc, opts)
        result = domdown.parse()
        to_markdown(result, opts, url)

        assert "<p>" in result.content
        assert "<strong>" in result.content

        assert result.content_markdown is not None
        assert "<p>" not in result.content_markdown
        assert "**test**" in result.content_markdown

    def test_no_markdown_options_keeps_html_no_markdown(self, doc, url):
        opts = DomdownOptions(url=url)
        domdown = Domdown(doc, opts)
        result = domdown.parse()
        to_markdown(result, opts, url)

        assert "<p>" in result.content
        assert "<strong>" in result.content

        assert result.content_markdown is None
