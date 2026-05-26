from __future__ import annotations

from pathlib import Path

from bs4 import BeautifulSoup

from domdown import html_to_markdown
from domdown._core import DomdownOptions
from domdown.markdown.block import (
    _collect_definition_items,
    _collect_definition_items_from_node,
    _definition_label_child,
    _looks_like_definition_list,
    _parse_definition_item,
    render_block,
    render_container,
    render_definition_list,
    render_figure,
)


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


def test_render_block_ignores_empty_absolute_permalink_anchors_in_headings() -> None:
    """Empty permalink anchors with absolute fragment URLs should not leak into headings."""

    soup = BeautifulSoup(
        """
        <h2>
          <a class="header-anchor" href="https://example.com/test#technical-analysis-how-the-attack-unfolds"></a>
          Technical analysis: How the attack unfolds
        </h2>
        """,
        "lxml",
    )

    assert (
        render_block(soup.h2, DomdownOptions())
        == "## Technical analysis: How the attack unfolds"
    )


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


def test_render_block_covers_inline_and_block_fallbacks() -> None:
    """Block rendering should dispatch to the expected specialized handlers."""

    soup = BeautifulSoup(
        """
        <div>
          text
          <a href="/docs">Docs</a>
          <br />
          <pre><code>print(1)</code></pre>
          <ul><li>One</li></ul>
          <ol><li>Two</li></ol>
          <table><tr><td>Cell</td></tr></table>
          <span>Fallback</span>
        </div>
        """,
        "lxml",
    )

    children = [child for child in soup.div.children if getattr(child, "name", None)]

    assert render_block(123, DomdownOptions()) == ""
    assert render_block(children[0], DomdownOptions()) == "[Docs](/docs)"
    assert render_block(children[1], DomdownOptions()) == ""
    assert render_block(children[2], DomdownOptions()) == "```\nprint(1)\n```"
    assert render_block(children[3], DomdownOptions()) == "- One"
    assert render_block(children[4], DomdownOptions()) == "1. Two"
    assert render_block(children[5], DomdownOptions()) == "| Cell |\n| --- |"
    assert render_block(children[6], DomdownOptions()) == "Fallback"


def test_render_figure_without_caption_uses_container_rendering() -> None:
    """Figures without a caption should fall back to the container renderer."""

    soup = BeautifulSoup(
        """
        <figure>
          <img src="https://example.com/a.png" alt="Example" />
        </figure>
        """,
        "lxml",
    )

    assert render_figure(soup.figure, DomdownOptions()) == "![Example](https://example.com/a.png)"


def test_render_figure_ignores_empty_captions() -> None:
    """Empty figcaptions should not add blank markdown blocks."""

    soup = BeautifulSoup(
        """
        <figure>
          <img src="https://example.com/a.png" alt="Example" />
          <figcaption><span></span></figcaption>
        </figure>
        """,
        "lxml",
    )

    assert render_figure(soup.figure, DomdownOptions()) == "![Example](https://example.com/a.png)"


def test_definition_list_helpers_cover_explicit_labels_and_anchor_rows() -> None:
    """Definition list helpers should recognize both labeled rows and permalink rows."""

    soup = BeautifulSoup(
        """
        <div class="metadata">
          <div class="row">
            <span class="field-label">Platforms:</span> Windows
          </div>
          <div class="row">
            <a href="/versions/v19/techniques/T1055/004/">Version Permalink</a>
          </div>
          <div class="row">
            <span class="field-label">Version:</span> 2.0
          </div>
        </div>
        """,
        "lxml",
    )

    row = soup.select_one(".row")
    assert row is not None
    assert _definition_label_child(row, DomdownOptions()) is not None
    assert _parse_definition_item(row, DomdownOptions()) == ("Platforms", "Windows")

    anchor_row = soup.select(".row")[1]
    assert _parse_definition_item(anchor_row, DomdownOptions()) == (
        "Version Permalink",
        '<a href="/versions/v19/techniques/T1055/004/">Version Permalink</a>',
    )

    assert _looks_like_definition_list(soup.div, DomdownOptions()) is True
    assert render_definition_list(soup.div, DomdownOptions()) == """- **Platforms:** Windows
- **Version Permalink:** <a href="/versions/v19/techniques/T1055/004/">Version Permalink</a>
- **Version:** 2.0"""


def test_definition_list_anchor_rows_strip_nested_card_markup() -> None:
    """Anchor-only definition rows should keep the link, not the nested UI DOM."""

    soup = BeautifulSoup(
        """
        <div>
          <div>
            <a aria-label="Pixplus Pro" class="svelte-jrkm1h" href="https://apps.apple.com/us/app/pixplus-pro/id6762183243">
              <div class="container" style="display:flex">
                <picture><img alt="" src="/assets/artwork/1x1.gif" /></picture>
                <h3>Pixplus Pro</h3>
                <p>Utilities</p>
                <span>View</span>
              </div>
            </a>
          </div>
          <div><strong>Seller:</strong> Hangzhou Denghong Technology Co., Ltd.</div>
          <div><strong>Category:</strong> Utilities</div>
        </div>
        """,
        "lxml",
    )

    assert render_definition_list(soup.div, DomdownOptions()) == """- **Pixplus Pro Utilities View:** <a href="https://apps.apple.com/us/app/pixplus-pro/id6762183243">Pixplus Pro Utilities View</a>
- **Seller:** Hangzhou Denghong Technology Co., Ltd.
- **Category:** Utilities"""


def test_render_explicit_definition_list_as_markdown_bullets() -> None:
    """Native dl content should render as readable Markdown bullets."""

    soup = BeautifulSoup(
        """
        <dl>
          <dt>Granular controls</dt>
          <dd>You have the choice to explicitly enable or disable entire AI features.</dd>
          <dt>Security guardrails</dt>
          <dd>Your Gemini assistant starts to automate a task only when you tell it to.</dd>
          <dt>Explicit intent</dt>
          <dd>For any feature, you decide whether your data is shared.</dd>
        </dl>
        """,
        "lxml",
    )

    assert render_block(soup.dl, DomdownOptions()) == (
        "- **Granular controls:** You have the choice to explicitly enable or disable entire AI features.\n"
        "- **Security guardrails:** Your Gemini assistant starts to automate a task only when you tell it to.\n"
        "- **Explicit intent:** For any feature, you decide whether your data is shared."
    )


def test_render_definition_list_between_lists_keeps_contiguous_bullets() -> None:
    """Footnote dl blocks between lists should join the surrounding bullet sequence."""

    soup = BeautifulSoup(
        """
        <section>
          <h4>Footnotes</h4>
          <p>[1] The 1M token context window is currently available in beta.</p>
          <ul>
            <li>For GPT-5.2 and Gemini 3 Pro models, we compared the best reported model version.</li>
          </ul>
          <dl>
            <dt>SWE-bench Verified</dt>
            <dd>Our score was averaged over 25 trials.</dd>
            <dt>MCP Atlas</dt>
            <dd>Claude Opus 4.6 was run with max effort.</dd>
          </dl>
          <ul>
            <li><strong>CyberGym</strong>: Claude models were run on no thinking.</li>
          </ul>
        </section>
        """,
        "lxml",
    )

    assert render_container(soup.section, DomdownOptions()) == (
        "#### Footnotes\n\n"
        "[1] The 1M token context window is currently available in beta.\n\n"
        "- For GPT-5.2 and Gemini 3 Pro models, we compared the best reported model version.\n"
        "- **SWE-bench Verified:** Our score was averaged over 25 trials.\n"
        "- **MCP Atlas:** Claude Opus 4.6 was run with max effort.\n"
        "- **CyberGym**: Claude models were run on no thinking."
    )


def test_render_block_ignores_email_protection_dl_chrome() -> None:
    """Cloudflare email-protection blocks should stay as prose, not metadata lists."""

    soup = BeautifulSoup(
        """
        <div class="prose">
          <p>Body paragraph stays visible.</p>
          <p><code><a class="__cf_email__" data-cfemail="d1" href="/cdn-cgi/l/email-protection">[email&#160;protected]</a></code></p>
          <p>Another body paragraph also stays visible.</p>
        </div>
        """,
        "lxml",
    )

    output = render_block(soup.div, DomdownOptions())

    assert "<dl>" not in output
    assert "Body paragraph stays visible." in output
    assert "Another body paragraph also stays visible." in output


def test_render_definition_list_does_not_reclassify_heading_sections() -> None:
    """Heading-led content sections should stay as headings, not definition rows."""

    soup = BeautifulSoup(
        """
        <div class="RichTextBody">
          <p>Date: Since 2023</p>
          <div class="RichTextHeading">
            <h2><a href="#adversary" id="adversary">ADVERSARY</a></h2>
          </div>
          <ul class="rte2-style-ul">
            <li>Overlap with Volt Typhoon and BRONZE SILHOUETT</li>
          </ul>
          <div class="RichTextHeading">
            <h2><a href="#capabilities" id="capabilities">CAPABILITIES</a></h2>
          </div>
          <ul class="rte2-style-ul">
            <li>Heavy use of living off the land techniques</li>
          </ul>
        </div>
        """,
        "lxml",
    )

    output = render_block(soup.div, DomdownOptions())

    assert "<dl>" not in output
    assert "## ADVERSARY" in output
    assert "- Overlap with Volt Typhoon and BRONZE SILHOUETT" in output
    assert "## CAPABILITIES" in output
    assert "- Heavy use of living off the land techniques" in output


def test_definition_list_helpers_fall_back_for_small_or_nested_blocks() -> None:
    """Small or non-metadata blocks should stay as normal container content."""

    soup = BeautifulSoup(
        """
        <div class="wrapper">
          <div class="row"><span class="field-label">Only one:</span> Item</div>
          <div class="row"><span class="field-label">Two:</span> Item</div>
        </div>
        """,
        "lxml",
    )

    assert _collect_definition_items(soup.div, DomdownOptions()) == [("Only one", "Item"), ("Two", "Item")]
    assert _collect_definition_items_from_node(soup.select_one(".row"), DomdownOptions()) == [("Only one", "Item")]
    assert _looks_like_definition_list(soup.div, DomdownOptions()) is False
    assert render_definition_list(soup.div, DomdownOptions()) == "Only one:\n\nItem\n\nTwo:\n\nItem"


def test_definition_list_anchor_with_malformed_url_falls_back_to_text() -> None:
    """Malformed URLs in metadata anchors should not crash markdown rendering."""

    soup = BeautifulSoup(
        """
        <div class="metadata">
          <div class="row">
            <a href="https://[invalid-ipv6]/path">Version Permalink</a>
          </div>
          <div class="row">
            <span class="field-label">Version:</span> 2.0
          </div>
          <div class="row">
            <span class="field-label">Created:</span> 14 January 2020
          </div>
        </div>
        """,
        "lxml",
    )

    assert render_block(soup.div, DomdownOptions()) == """- **Version Permalink:** Version Permalink
- **Version:** 2.0
- **Created:** 14 January 2020"""


def test_render_container_collapses_empty_children() -> None:
    """Container rendering should drop empty child nodes and normalize spacing."""

    soup = BeautifulSoup("<div><p>First</p><script>skip()</script><p>Second</p></div>", "lxml")

    assert render_container(soup.div, DomdownOptions()) == "First\n\nSecond"


def test_render_block_normalizes_metadata_panel_to_definition_list() -> None:
    """Repeated label/value rows should render as a semantic definition list."""

    soup = BeautifulSoup(
        """
        <div class="technique-metadata">
          <div class="row card-data">
            <div class="col-md-1 px-0 text-center">
              <span aria-hidden="true">ⓘ</span>
            </div>
            <div class="col-md-11 pl-0">
              <span class="h5 card-title">Platforms:&nbsp;</span>Windows
            </div>
          </div>
          <div class="row card-data">
            <div class="col-md-1 px-0 text-center"></div>
            <div class="col-md-11 pl-0">
              <span class="h5 card-title">Version:&nbsp;</span>2.0
            </div>
          </div>
          <div class="row card-data">
            <div class="col-md-1 px-0 text-center"></div>
            <div class="col-md-11 pl-0">
              <span class="h5 card-title">Created:&nbsp;</span>14 January 2020
            </div>
          </div>
          <div class="row card-data">
            <div class="col-md-1 px-0 text-center"></div>
            <div class="col-md-11 pl-0">
              <span class="h5 card-title">Last Modified:&nbsp;</span>12 May 2026
            </div>
          </div>
          <div class="text-center pt-2 version-button live">
            <div class="live">
              <a href="/versions/v19/techniques/T1055/004/" title="Permalink to this version of T1055.004">Version Permalink</a>
            </div>
            <div class="permalink">
              <a href="/versions/v19/techniques/T1055/004/" title="Go to the live version of T1055.004">Live Version</a>
            </div>
          </div>
        </div>
        """,
        "lxml",
    )

    assert render_block(soup.div, DomdownOptions()) == """- **Platforms:** Windows
- **Version:** 2.0
- **Created:** 14 January 2020
- **Last Modified:** 12 May 2026
- **Version Permalink:** <a href="/versions/v19/techniques/T1055/004/" title="Permalink to this version of T1055.004">Version Permalink</a>
- **Live Version:** <a href="/versions/v19/techniques/T1055/004/" title="Go to the live version of T1055.004">Live Version</a>"""


def test_render_acronis_article_skips_decorative_background_images() -> None:
    """Decorative hero/background wrappers should not render as leading content."""

    html_path = Path("tests/real/html/acronis_boto_cor_de_rosa_campaign_astaroth_whatsapp_brazil.html")
    output = html_to_markdown(
        html_path.read_text(encoding="utf-8"),
        DomdownOptions(base_url="https://www.acronis.com/en/tru/posts/boto-cor-de-rosa-campaign-reveals-astaroth-whatsapp-based-worm-activity-in-brazil/"),
    )
    body = output.split("---", 2)[-1].lstrip()

    assert not body.startswith("![Acronis](https://staticfiles.acronis.com/images/content/")
    assert not body.startswith("![Acronis](https://staticfiles.acronis.com/images/background/")
    assert body.splitlines()[0] == "# Boto-Cor-de-Rosa campaign reveals Astaroth WhatsApp-based worm activity in Brazil"
