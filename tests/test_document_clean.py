from __future__ import annotations

from bs4 import BeautifulSoup

from domdown._constants import SKIP_TAGS
from domdown._document import clean_root


def test_clean_root_removes_noise_and_promotes_lazy_loaded_images() -> None:
    """Cleanup should drop noisy tags and normalize lazy-loaded images."""

    soup = BeautifulSoup(
        "<div><script>alert(1)</script><div class='drop'>noise</div><img data-src='/img.png' src='data:image/gif;base64,x' /></div>",
        "lxml",
    )
    root = soup.div

    cleaned = clean_root(root, (".drop",), SKIP_TAGS)

    assert cleaned.find("script") is None
    assert cleaned.select_one(".drop") is None
    assert cleaned.img["src"] == "/img.png"
