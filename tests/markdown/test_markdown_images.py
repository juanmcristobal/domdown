from __future__ import annotations

from bs4 import BeautifulSoup

from domdown._core import DomdownOptions
from domdown.markdown.images import _best_srcset_candidate, _srcset_score, render_image


def test_render_image_prefers_lazy_loaded_sources() -> None:
    """Image rendering should resolve the best available source URL."""

    soup = BeautifulSoup("<img alt='Cybersecurity' data-src='/image.png' />", "lxml")

    assert (
        render_image(soup.img, DomdownOptions(base_url="https://example.com"))
        == "![Cybersecurity](https://example.com/image.png)"
    )


def test_render_image_prefers_largest_srcset_candidate() -> None:
    """Image rendering should choose the highest-resolution srcset candidate when available."""

    soup = BeautifulSoup(
        """
        <img
          alt="Illustration"
          src="/small.png"
          srcset="/small.png 480w, /medium.png 960w, /large.png 1920w"
        />
        """,
        "lxml",
    )

    assert (
        render_image(soup.img, DomdownOptions(base_url="https://example.com"))
        == "![Illustration](https://example.com/large.png)"
    )


def test_render_image_uses_data_srcset_and_falls_back_to_data_original() -> None:
    """Image rendering should use alternate lazy-load attributes when present."""

    soup = BeautifulSoup(
        "<img title='Illustration' data-srcset='/small.png 1x, /large.png 2x' data-original='/fallback.png' />",
        "lxml",
    )

    assert (
        render_image(soup.img, DomdownOptions(base_url="https://example.com"))
        == "![Illustration](https://example.com/large.png)"
    )


def test_srcset_helpers_ignore_invalid_descriptors() -> None:
    """Srcset scoring should ignore malformed descriptors and empty candidates."""

    assert _best_srcset_candidate(" , /a.png foo, /b.png 2x") == "/b.png"
    assert _srcset_score(["bad"]) == 0.0
