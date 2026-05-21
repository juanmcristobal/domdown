"""Debug options and pipeline toggles tests."""

import pytest

from domdown import Domdown, DomdownOptions
from domdown.utils.dom import parse_html as _parse_html

FIXTURE_HTML = """<!DOCTYPE html>
<html>
<head><title>Buy Wisely - Stephen Bono</title></head>
<body>
<article>
<h1>Buy Wisely</h1>
<p>This is a test article about buying wisely. It contains enough content to test the scoring mechanism.</p>
<p>Here is another paragraph with more content to ensure the scorer picks this up as the main content element.</p>
<p>Additional content that helps establish this as the primary article element on the page.</p>
</article>
</body>
</html>"""


@pytest.fixture
def fixture_doc():
    return _parse_html(FIXTURE_HTML)


def test_debug_mode_returns_info(fixture_doc):
    """Debug mode should return contentSelector and removals."""
    result = Domdown(fixture_doc, DomdownOptions(debug=True, url="https://stephango.com/buy-wisely")).parse()

    assert result.debug is not None, "debug info should be present"
    assert result.debug.content_selector, "content_selector should be set"
    assert isinstance(result.debug.removals, list), "removals should be a list"


def test_no_debug_mode(fixture_doc):
    """Without debug mode, debug field should be absent."""
    result = Domdown(fixture_doc, DomdownOptions(url="https://stephango.com/buy-wisely")).parse()

    assert result.debug is None, "debug info should not be present"


def test_debug_removals_have_required_fields(fixture_doc):
    """Each removal should have step and text fields."""
    result = Domdown(fixture_doc, DomdownOptions(debug=True, url="https://stephango.com/buy-wisely")).parse()

    removals = result.debug.removals
    for removal in removals:
        assert removal.step, f"removal missing step: {removal}"
        assert removal.text is not None, f"removal missing text: {removal}"


def test_pipeline_toggle_remove_low_scoring(fixture_doc):
    """Disabling low scoring should change the removals."""
    url = "https://stephango.com/buy-wisely"

    with_scoring = Domdown(fixture_doc, DomdownOptions(debug=True, url=url)).parse()
    without_scoring = Domdown(fixture_doc, DomdownOptions(debug=True, url=url, remove_low_scoring=False)).parse()

    no_scoring_steps = {r.step for r in without_scoring.debug.removals}

    # scoreAndRemove should be absent when disabled
    assert "scoreAndRemove" not in no_scoring_steps

    # Content without scoring should be >= content with scoring
    assert without_scoring.word_count >= with_scoring.word_count


def test_pipeline_toggle_remove_hidden_elements(fixture_doc):
    """Disabling hidden element removal should change the removals."""
    url = "https://stephango.com/buy-wisely"

    without_hidden = Domdown(fixture_doc, DomdownOptions(debug=True, url=url, remove_hidden_elements=False)).parse()

    no_hidden_steps = {r.step for r in without_hidden.debug.removals}
    assert "removeHiddenElements" not in no_hidden_steps


def test_pipeline_toggle_remove_small_images(fixture_doc):
    """Disabling small image removal should keep more content."""
    url = "https://stephango.com/buy-wisely"

    with_removal = Domdown(fixture_doc, DomdownOptions(url=url)).parse()
    without_removal = Domdown(fixture_doc, DomdownOptions(url=url, remove_small_images=False)).parse()

    assert len(without_removal.content) >= len(with_removal.content)


def test_all_toggles_off_keeps_most_content(fixture_doc):
    """With all removal toggles off, should keep most content."""
    url = "https://stephango.com/buy-wisely"

    defaults = Domdown(fixture_doc, DomdownOptions(url=url)).parse()
    all_off = Domdown(
        fixture_doc,
        DomdownOptions(
            url=url,
            remove_low_scoring=False,
            remove_hidden_elements=False,
            remove_small_images=False,
            remove_exact_selectors=False,
            remove_partial_selectors=False,
        ),
    ).parse()

    assert all_off.word_count >= defaults.word_count


def test_content_selector_body(fixture_doc):
    """contentSelector: body should select the body element."""
    url = "https://stephango.com/buy-wisely"
    result = Domdown(fixture_doc, DomdownOptions(debug=True, url=url, content_selector="body")).parse()

    assert "body" in result.debug.content_selector
    assert result.content, "content should not be empty"


def test_content_selector_fallback(fixture_doc):
    """Non-existent selector should fall back to auto-detection."""
    url = "https://stephango.com/buy-wisely"

    auto_result = Domdown(fixture_doc, DomdownOptions(debug=True, url=url)).parse()
    fallback_result = Domdown(
        fixture_doc, DomdownOptions(debug=True, url=url, content_selector=".nonexistent-xyz-class")
    ).parse()

    assert fallback_result.content, "fallback should still produce content"
    # Auto and fallback should use the same content selector
    assert fallback_result.debug.content_selector == auto_result.debug.content_selector


def test_content_selector_narrows(fixture_doc):
    """Narrow contentSelector should produce less content."""
    url = "https://stephango.com/buy-wisely"

    auto_result = Domdown(fixture_doc, DomdownOptions(url=url)).parse()
    narrow_result = Domdown(fixture_doc, DomdownOptions(url=url, content_selector="p")).parse()

    # A single paragraph should have fewer words than the full article
    if narrow_result.content:
        assert narrow_result.word_count < auto_result.word_count
