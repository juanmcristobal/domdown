from __future__ import annotations

from bs4 import BeautifulSoup

from domdown._pipeline import HtmlToMarkdownPipeline
from domdown.adapters import DomainAdapterSpec, make_domain_adapter
from domdown.adapters.domain import (
    _class_name,
    _host_matches,
    _normalize_host,
    _normalize_suffix,
    _page_host,
    _remove_selectors,
    _site_name,
    _strip_markdown,
)


def test_declarative_domain_adapter_can_be_declared_with_a_single_spec() -> None:
    """A new domain should be expressible without writing a custom adapter class."""

    ExampleAdapter = make_domain_adapter(
        DomainAdapterSpec(
            name="example",
            site_names=("Example Publishing",),
            host_exact=("example.com",),
            remove_selectors=("header", "footer"),
            trim_before_first_heading=True,
            trailing_noise_prefixes=("- **Privacy:**",),
            noise_lines=("·",),
        )
    )

    pipeline = HtmlToMarkdownPipeline(adapters=(ExampleAdapter(),))
    html = """
    <html>
      <head>
        <meta property="og:site_name" content="Example Publishing" />
        <meta property="og:url" content="https://example.com/post" />
      </head>
      <body>
        <header><p>Site chrome</p></header>
        <article>
          <p>Intro noise</p>
          <h1>Article title</h1>
          <p>Body paragraph.</p>
          <p>·</p>
          <p>- **Privacy:** <a href="https://example.com/privacy">Privacy</a></p>
        </article>
        <footer><p>Footer chrome</p></footer>
      </body>
    </html>
    """

    result = pipeline.run(html)

    assert result.markdown == "# Article title\n\nBody paragraph."


def test_declarative_domain_adapter_matches_www_hosts() -> None:
    """Exact host matching should tolerate a leading www subdomain."""

    ExampleAdapter = make_domain_adapter(
        DomainAdapterSpec(
            name="example",
            host_exact=("example.com",),
            trim_before_first_heading=True,
        )
    )

    pipeline = HtmlToMarkdownPipeline(adapters=(ExampleAdapter(),))
    html = """
    <html>
      <head>
        <meta property="og:url" content="https://www.example.com/post" />
      </head>
      <body><article><p>Noise</p><h1>Title</h1><p>Body</p></article></body>
    </html>
    """

    result = pipeline.run(html)

    assert result.markdown == "# Title\n\nBody"


def test_domain_adapter_helpers_cover_host_normalization_and_empty_class_names() -> None:
    """Domain helper functions should normalize hosts and fall back for empty names."""

    soup = BeautifulSoup(
        """
        <html>
          <head>
            <link rel="canonical" href="https://www.example.com/post" />
          </head>
          <body></body>
        </html>
        """,
        "lxml",
    )

    assert _page_host(soup, ("link[rel='canonical']",)) == "example.com"
    assert _normalize_host("WWW.Example.com") == "example.com"
    assert _normalize_suffix("example.com") == ".example.com"
    assert _host_matches("www.example.com", ("example.com",), ()) is True
    assert _class_name("") == "Domain"


def test_domain_helpers_handle_missing_and_invalid_page_urls() -> None:
    soup = BeautifulSoup("<html><head><link rel='canonical' href='http://['></head></html>", "lxml")
    assert _site_name(None) == ""
    assert _page_host(None, ("link[rel='canonical']",)) == ""
    assert _page_host(soup, ("link[rel='canonical']",)) == ""
    assert _host_matches("other.example.net", (), ("example.com",)) is False
    assert _normalize_suffix("") == ""
    assert _class_name("---") == "Domain"


def test_domain_adapter_selector_cleanup_handles_missing_document_and_matches() -> None:
    _remove_selectors(None, (".remove",))
    soup = BeautifulSoup("<div><p class='remove'>noise</p><p>keep</p></div>", "lxml")
    _remove_selectors(soup, (".remove",))
    assert soup.get_text(" ", strip=True) == "keep"


def test_strip_markdown_applies_configured_cleanup_while_preserving_fenced_code() -> None:
    cleaned = _strip_markdown(
        "Intro\r\n# Title\r\n\r\nBy Example\r\n\r\nSponsored: offer\r\nBody\r\n\r\n```text\r\nSponsored: code\r\n```\r\n\r\nPrivacy policy\r\n",
        trim_before_first_heading=True,
        leading_noise_lines=("By Example",),
        leading_noise_prefixes=(),
        leading_noise_patterns=(),
        leading_block_patterns=(r"Sponsored:.*",),
        rstrip_noise_lines=("Privacy policy",),
        rstrip_noise_patterns=(),
        trailing_noise_lines=("Privacy policy",),
        trailing_noise_prefixes=(),
        trailing_noise_patterns=(),
        noise_lines=("Body",),
        noise_patterns=(r"Sponsored:.*",),
    )

    assert cleaned.startswith("# Title")
    assert "Sponsored: offer" not in cleaned
    assert "Privacy policy" not in cleaned
    assert "Body" not in cleaned
    assert "Sponsored: code" in cleaned


def test_strip_markdown_keeps_content_when_rules_have_no_heading_or_match() -> None:
    markdown = "plain article text\n\n\nsecond paragraph"
    cleaned = _strip_markdown(
        markdown,
        trim_before_first_heading=True,
        leading_noise_lines=(),
        leading_noise_prefixes=(),
        leading_noise_patterns=(),
        leading_block_patterns=(r"never matches",),
        rstrip_noise_lines=(),
        rstrip_noise_patterns=(),
        trailing_noise_lines=(),
        trailing_noise_prefixes=(),
        trailing_noise_patterns=(),
        noise_lines=(),
        noise_patterns=(r"never matches",),
    )

    assert cleaned == "plain article text\n\nsecond paragraph"


def test_strip_markdown_ignores_configured_regex_on_oversized_lines() -> None:
    long_line = "x" * 1001
    cleaned = _strip_markdown(
        f"# Title\n{long_line}",
        trim_before_first_heading=False,
        leading_noise_lines=(),
        leading_noise_prefixes=(),
        leading_noise_patterns=(),
        leading_block_patterns=(),
        rstrip_noise_lines=(),
        rstrip_noise_patterns=(),
        trailing_noise_lines=(),
        trailing_noise_prefixes=(),
        trailing_noise_patterns=(),
        noise_lines=(),
        noise_patterns=(r"x+",),
    )

    assert long_line in cleaned
