from __future__ import annotations

from bs4 import BeautifulSoup

from domdown._core import DomdownOptions
from domdown.markdown.images import render_image


def test_render_image_prefers_lazy_loaded_sources() -> None:
    """Image rendering should resolve the best available source URL."""

    soup = BeautifulSoup("<img alt='Cybersecurity' data-src='/image.png' />", "lxml")

    assert render_image(soup.img, DomdownOptions(base_url="https://example.com")) == "![Cybersecurity](https://example.com/image.png)"
