from __future__ import annotations

from bs4 import BeautifulSoup

from domdown._core import DomdownOptions
from domdown.markdown.block import render_block


def test_render_block_covers_headings_paragraphs_and_quotes() -> None:
    """Block rendering should handle common structural HTML elements."""

    soup = BeautifulSoup(
        "<div><h1>Title</h1><p>Body</p><blockquote><p>Quote</p></blockquote><script>skip()</script></div>",
        "lxml",
    )

    children = list(soup.div.children)

    assert render_block(children[0], DomdownOptions()) == "# Title"
    assert render_block(children[1], DomdownOptions()) == "Body"
    assert render_block(children[2], DomdownOptions()) == "> Quote"
    assert render_block(children[3], DomdownOptions()) == ""


def test_render_block_unwraps_self_linked_heading_titles() -> None:
    """Heading titles that wrap a single self-link should render as plain text."""

    soup = BeautifulSoup(
        '<h1><a href="https://example.com/article"><span>Example Title</span></a></h1>',
        "lxml",
    )

    assert render_block(soup.h1, DomdownOptions()) == "# Example Title"


def test_render_block_ignores_permalink_icons_in_headings() -> None:
    """Heading permalinks should not leak slug anchors into Markdown output."""

    soup = BeautifulSoup(
        """
        <h2>
          <span class="me-2">Example Section</span>
          <a href="#example-section" class="anchor text-muted">
            <i class="fas fa-hashtag"></i>
          </a>
        </h2>
        """,
        "lxml",
    )

    assert render_block(soup.h2, DomdownOptions()) == "## Example Section"


def test_render_block_ignores_bracket_permalink_markers_in_headings() -> None:
    """Bracket markers used around permalink headings should not appear in markdown."""

    soup = BeautifulSoup(
        """
        <h2 id="inside-the-attack">
          <a class="header-anchor" href="#inside-the-attack"></a>
          [[Inside the attack]]
        </h2>
        """,
        "lxml",
    )

    assert render_block(soup.h2, DomdownOptions()) == "## Inside the attack"


def test_render_block_renders_captioned_figures_as_image_then_caption() -> None:
    """Captioned figures should render as a media block followed by the caption."""

    soup = BeautifulSoup(
        """
        <div class="Body-module-scss-module__z40yvW__media-column">
          <figure class="ImageWithCaption-module-scss-module__Duq99q__e-imageWithCaption">
            <img
              loading="eager"
              width="3840"
              height="1762"
              decoding="async"
              data-nimg="1"
              style="color:transparent"
              srcset="/_next/image?url=https%3A%2F%2Fwww-cdn.anthropic.com%2Fimages%2F4zrzovbb%2Fwebsite%2F021f5a89f9b3ba1755f9a2315bc63be855259532-3840x1762.png&amp;w=3840&amp;q=75 1x"
              src="/_next/image?url=https%3A%2F%2Fwww-cdn.anthropic.com%2Fimages%2F4zrzovbb%2Fwebsite%2F021f5a89f9b3ba1755f9a2315bc63be855259532-3840x1762.png&amp;w=3840&amp;q=75"
            />
            <figcaption class="caption">
              <em>Left: </em>Character archetypes form a "persona space," with the Assistant at one extreme of the "Assistant Axis." <em>Right:</em> Capping drift along this axis prevents models (here, Llama 3.3 70B) from drifting into alternative personas and behaving in harmful ways.
            </figcaption>
          </figure>
        """,
        "lxml",
    )

    assert render_block(soup.figure, DomdownOptions()) == '![](/_next/image?url=https%3A%2F%2Fwww-cdn.anthropic.com%2Fimages%2F4zrzovbb%2Fwebsite%2F021f5a89f9b3ba1755f9a2315bc63be855259532-3840x1762.png&w=3840&q=75)\n\n_Left:_Character archetypes form a "persona space," with the Assistant at one extreme of the "Assistant Axis." _Right:_ Capping drift along this axis prevents models (here, Llama 3.3 70B) from drifting into alternative personas and behaving in harmful ways.'
