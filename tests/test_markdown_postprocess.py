from __future__ import annotations

from domdown.markdown.postprocess import postprocess_markdown


def test_postprocess_markdown_cleans_spacing_and_outer_whitespace() -> None:
    """Postprocessing should keep paragraphs while removing extra blank lines."""

    assert postprocess_markdown("A\r\n\r\n\r\nB  \n") == "A\n\nB"
