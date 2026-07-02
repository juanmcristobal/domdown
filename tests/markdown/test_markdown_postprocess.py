from __future__ import annotations

from domdown._core.metadata import HtmlMetadata
from domdown.markdown.postprocess import postprocess_markdown


def test_postprocess_strips_empty_headings_and_leading_branding() -> None:
    """Postprocessing should remove empty heading lines and duplicated site branding."""

    metadata = HtmlMetadata(site_name="OpenAI")

    assert postprocess_markdown("OpenAI\n\n#\n\nBody", metadata) == "Body"


def test_postprocess_keeps_regular_content_when_branding_is_absent() -> None:
    """Postprocessing should leave normal markdown intact."""

    assert postprocess_markdown("# Heading\n\nBody", None) == "# Heading\n\nBody"


def test_postprocess_ignores_blank_site_names() -> None:
    """Blank site names should not trim the body."""

    metadata = HtmlMetadata(site_name="   ")

    assert postprocess_markdown("Body\n\n\nNext", metadata) == "Body\n\nNext"
