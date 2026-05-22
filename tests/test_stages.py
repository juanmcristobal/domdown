from __future__ import annotations

from bs4 import BeautifulSoup

from domdown._core import DomdownOptions, HtmlMetadata, PipelineContext
from domdown.stages import FrontmatterStage, MarkdownStage, MetadataStage, ParseStage, PostProcessStage, PreserveStage


def test_parse_stage_builds_the_document_tree() -> None:
    """The parse stage should attach a BeautifulSoup tree to the context."""

    context = ParseStage().run(PipelineContext(html="<html><body><p>x</p></body></html>", options=DomdownOptions()))

    assert context.document is not None
    assert context.document.body is not None


def test_metadata_stage_extracts_metadata() -> None:
    """The metadata stage should populate the metadata slot."""

    soup = BeautifulSoup(
        "<html><head><meta property='og:title' content='Title' /></head><body><div class='p-tags'>alpha/beta</div></body></html>",
        "lxml",
    )
    context = PipelineContext(html="", options=DomdownOptions(), document=soup)

    context = MetadataStage().run(context)

    assert context.metadata is not None
    assert context.metadata.title == "Title"


def test_preserve_stage_resolves_relative_links_and_images() -> None:
    """The preserve stage should resolve URLs against the configured base."""

    soup = BeautifulSoup("<div><a href='/story'>Story</a><img data-src='/img.png' src='data:image/gif;base64,x' /></div>", "lxml")
    context = PipelineContext(
        html="",
        options=DomdownOptions(base_url="https://example.com"),
        document=soup.div,
    )

    context = PreserveStage().run(context)

    assert context.document.a["href"] == "https://example.com/story"
    assert context.document.img["src"] == "https://example.com/img.png"


def test_markdown_stage_renders_markdown_text() -> None:
    """The markdown stage should render the document subtree."""

    soup = BeautifulSoup("<div><p>Hello</p><ul><li>One</li></ul></div>", "lxml")
    context = PipelineContext(html="", options=DomdownOptions(), document=soup.div)

    context = MarkdownStage().run(context)

    assert context.markdown == "Hello\n\n- One"


def test_postprocess_stage_normalizes_markdown() -> None:
    """The postprocess stage should sanitize the final markdown string."""

    context = PipelineContext(html="", options=DomdownOptions(), markdown="A\r\n\r\n\r\nB  \n")

    context = PostProcessStage().run(context)

    assert context.markdown == "A\n\nB"


def test_frontmatter_stage_combines_metadata_and_body() -> None:
    """The frontmatter stage should prepend rendered metadata when enabled."""

    context = PipelineContext(
        html="",
        options=DomdownOptions(),
        metadata=HtmlMetadata(title="Title"),
        markdown="Body",
    )

    context = FrontmatterStage().run(context)

    assert context.frontmatter == "---\ntitle: Title\n---"
    assert context.rendered_document == "---\ntitle: Title\n---\nBody"
