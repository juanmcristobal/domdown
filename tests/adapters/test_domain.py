from __future__ import annotations

from bs4 import BeautifulSoup

from domdown._pipeline import HtmlToMarkdownPipeline
from domdown.adapters import DomainAdapterSpec, make_domain_adapter
from domdown.adapters.domain import _class_name, _host_matches, _normalize_host, _normalize_suffix, _page_host


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
