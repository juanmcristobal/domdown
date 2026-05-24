from __future__ import annotations

from bs4 import BeautifulSoup

from domdown._core import DomdownOptions
from domdown.markdown.inline import render_inline, render_inline_children


def test_render_inline_children_normalizes_inline_content() -> None:
    """Inline rendering should preserve text and inline emphasis."""

    soup = BeautifulSoup("<p>Hello <strong>world</strong></p>", "lxml")

    assert render_inline_children(soup.p, DomdownOptions()) == "Hello **world**"


def test_render_inline_handles_html_br_and_script_nodes() -> None:
    """Inline rendering should keep line breaks and skip scripts."""

    soup = BeautifulSoup("<div><br/><script>bad()</script></div>", "lxml")

    assert render_inline(soup.br, DomdownOptions()) == "\n"
    assert render_inline(soup.script, DomdownOptions()) == ""


def test_render_inline_children_preserves_hard_line_breaks() -> None:
    """Inline children should keep hard breaks instead of flattening them."""

    soup = BeautifulSoup("<p>Alpha<br/>Beta</p>", "lxml")

    assert render_inline_children(soup.p, DomdownOptions()) == "Alpha\n\nBeta"


def test_render_inline_children_separates_caption_credits() -> None:
    """Caption credit spans should start on a fresh line."""

    soup = BeautifulSoup(
        '<div class="caption-content">The attacker spoofs the victim’s MAC address on a different NIC,<br/>causing the internal switch to mistakenly associate the victim’s address with the attacker’s port/BSSID.<span class="caption-credit">Credit: Zhou et al.</span></div>',
        "lxml",
    )

    assert (
        render_inline_children(soup.div, DomdownOptions())
        == "The attacker spoofs the victim’s MAC address on a different NIC,\n\ncausing the internal switch to mistakenly associate the victim’s address with the attacker’s port/BSSID.\n\nCredit: Zhou et al."
    )


def test_render_inline_preserves_strong_emphasis() -> None:
    """Strong inline text should keep markdown emphasis markers."""

    soup = BeautifulSoup("<p><strong>Tool Name</strong></p>", "lxml")

    assert render_inline_children(soup.p, DomdownOptions()) == "**Tool Name**"


def test_render_inline_preserves_emphasis_around_linked_image() -> None:
    """Strong wrappers around images should stay emphasized in markdown."""

    soup = BeautifulSoup('<p><strong><img src="https://example.com/tool.png" alt="Tool Name" /></strong></p>', "lxml")

    assert render_inline_children(soup.p, DomdownOptions()) == "**![Tool Name](https://example.com/tool.png)**"
