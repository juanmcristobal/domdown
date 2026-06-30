from __future__ import annotations

from domdown._pipeline import HtmlToMarkdownPipeline
from domdown.adapters import MediumAdapter


def test_medium_adapter_matches_medium_site_name_and_host() -> None:
    """Medium pages should be detected from their site metadata or host."""

    pipeline = HtmlToMarkdownPipeline(adapters=(MediumAdapter(),))
    html = """
    <html>
      <head>
        <meta property="og:site_name" content="Medium" />
        <meta property="og:url" content="https://example.medium.com/post" />
      </head>
      <body><article><h1>Title</h1><p>Body</p></article></body>
    </html>
    """

    result = pipeline.run(html)

    assert result.markdown == "# Title\n\nBody"


def test_medium_adapter_strips_medium_chrome_from_edges() -> None:
    """Medium-specific navigation and footer noise should be trimmed generically."""

    pipeline = HtmlToMarkdownPipeline(adapters=(MediumAdapter(),))
    html = """
    <html>
      <head>
        <meta property="og:site_name" content="Medium" />
        <meta property="og:url" content="https://infosecwriteups.com/post" />
      </head>
      <body>
        <header>
          <nav>
            <a href="https://infosecwriteups.com/?source=post_page---publication_nav">InfoSec Write-ups</a>
          </nav>
        </header>
        <article>
          <p>Mastodon</p>
          <p>Press enter or click to view image in full size</p>
          <h1>Title</h1>
          <p>Body paragraph.</p>
          <p>·</p>
          <p>--</p>
          <p>- **Help:** <a href="https://help.medium.com/hc/en-us">Help</a></p>
          <p>- **Privacy:** <a href="https://policy.medium.com">Privacy</a></p>
        </article>
      </body>
    </html>
    """

    result = pipeline.run(html)

    assert result.markdown == "# Title\n\nBody paragraph."


def test_medium_adapter_trims_medium_leading_lab_metadata_block() -> None:
    """Medium write-ups often repeat lab metadata before the first real paragraph."""

    pipeline = HtmlToMarkdownPipeline(adapters=(MediumAdapter(),))
    html = """
    <html>
      <head>
        <meta property="og:site_name" content="Medium" />
        <meta property="og:url" content="https://medium.com/post" />
      </head>
      <body>
        <article>
          <h1>User ID Controlled By Request Parameter With Password Disclosure</h1>
          <p>Access Control Vulnerabilities — APPRENTICE</p>
          <p>Lab-Access Control Vulnerabilities</p>
          <p>This lab has a user account page.</p>
        </article>
      </body>
    </html>
    """

    result = pipeline.run(html)

    assert (
        result.markdown
        == "# User ID Controlled By Request Parameter With Password Disclosure\n\nThis lab has a user account page."
    )


def test_medium_adapter_trims_medium_byline_block() -> None:
    """Medium byline boilerplate should not survive in the final Markdown."""

    pipeline = HtmlToMarkdownPipeline(adapters=(MediumAdapter(),))
    html = """
    <html>
      <head>
        <meta property="og:site_name" content="Medium" />
        <meta property="og:url" content="https://medium.com/post" />
      </head>
      <body>
        <article>
          <h1>Title</h1>
          <p>[![Yayangariestys](https://miro.medium.com/v2/da:true/resize:fill:64:64/0*FPCVDkHmqtY85uuB)](https://medium.com/@yayangariestys)</p>
          <p>[Yayangariestys](https://medium.com/@yayangariestys)</p>
          <p>3 min read</p>
          <p>Just now</p>
          <p>Body paragraph.</p>
        </article>
      </body>
    </html>
    """

    result = pipeline.run(html)

    assert result.markdown == "# Title\n\nBody paragraph."


def test_medium_adapter_trims_medium_chrome_before_body() -> None:
    """The generic Medium cleanup should remove the full byline and lab preamble block."""

    pipeline = HtmlToMarkdownPipeline(adapters=(MediumAdapter(),))
    html = """
    <html>
      <head>
        <meta property="og:site_name" content="Medium" />
        <meta property="og:url" content="https://medium.com/post" />
      </head>
      <body>
        <article>
          <h1>User ID Controlled By Request Parameter With Password Disclosure</h1>
          <p>[![Yayangariestys](https://miro.medium.com/v2/da:true/resize:fill:64:64/0*FPCVDkHmqtY85uuB)](https://medium.com/@yayangariestys)</p>
          <p>[Yayangariestys](https://medium.com/@yayangariestys)</p>
          <p>3 min read</p>
          <p>·</p>
          <p>Just now</p>
          <p>--</p>
          <p>Access Control Vulnerabilities — APPRENTICE</p>
          <p>Lab-Access Control Vulnerabilities</p>
          <p>This lab has a user account page.</p>
        </article>
      </body>
    </html>
    """

    result = pipeline.run(html)

    assert (
        result.markdown
        == "# User ID Controlled By Request Parameter With Password Disclosure\n\nThis lab has a user account page."
    )


def test_medium_adapter_trims_medium_author_footer() -> None:
    """Medium author cards and follow links should not remain after the article body."""

    pipeline = HtmlToMarkdownPipeline(adapters=(MediumAdapter(),))
    html = """
    <html>
      <head>
        <meta property="og:site_name" content="Medium" />
        <meta property="og:url" content="https://medium.com/post" />
      </head>
      <body>
        <article>
          <h1>Title</h1>
          <p>Body paragraph.</p>
          <p>[![Yayangariestys](https://miro.medium.com/v2/resize:fill:96:96/0*FPCVDkHmqtY85uuB)](https://medium.com/@yayangariestys?source=post_page---post_author_info--9ea55a7593d6---------------------------------------)</p>
          <p>[![Yayangariestys](https://miro.medium.com/v2/resize:fill:128:128/0*FPCVDkHmqtY85uuB)](https://medium.com/@yayangariestys?source=post_page---post_author_info--9ea55a7593d6---------------------------------------)</p>
          <p>[1 following](https://medium.com/@yayangariestys/following?source=post_page---post_author_info--9ea55a7593d6---------------------------------------)</p>
        </article>
      </body>
    </html>
    """

    result = pipeline.run(html)

    assert result.markdown == "# Title\n\nBody paragraph."


def test_medium_adapter_trims_medium_author_footer_with_subdomain() -> None:
    """Medium footer cleanup should also handle author subdomains and bio lines."""

    pipeline = HtmlToMarkdownPipeline(adapters=(MediumAdapter(),))
    html = """
    <html>
      <head>
        <meta property="og:site_name" content="Medium" />
        <meta property="og:url" content="https://medium.com/post" />
      </head>
      <body>
        <article>
          <h1>Title</h1>
          <p>Body paragraph.</p>
          <p>[![Fu'ad Husnan](https://miro.medium.com/v2/resize:fill:64:64/1*NGOUEMkljloDDim6HtZo-g.png)](https://fuadh369.medium.com/?source=post_page---post_author_info--c4a3a5c92571---------------------------------------)</p>
          <p>[Fu'ad Husnan](https://fuadh369.medium.com/?source=post_page---post_author_info--c4a3a5c92571---------------------------------------)</p>
          <p>7 min read</p>
          <p>1 hour ago</p>
          <p>Helping companies grow with Content Writing. [https://telkomuniversity.ac.id/](https://telkomuniversity.ac.id/)</p>
        </article>
      </body>
    </html>
    """

    result = pipeline.run(html)

    assert result.markdown == "# Title\n\nBody paragraph."


def test_medium_adapter_trims_medium_author_footer_on_custom_domain() -> None:
    """Medium author footer cleanup should not depend on the publication domain."""

    pipeline = HtmlToMarkdownPipeline(adapters=(MediumAdapter(),))
    html = """
    <html>
      <head>
        <meta property="og:site_name" content="Medium" />
        <meta property="og:url" content="https://wire.insiderfinance.io/whackd-9c6fe1b489ad" />
      </head>
      <body>
        <article>
          <h1>Title</h1>
          <p>Body paragraph.</p>
          <p>[![Alyze Sam, “I’m just here to serve”](https://miro.medium.com/v2/resize:fill:96:96/1*u0NSPQWAwgqs7kmH_KB70w@2x.jpeg)](https://wire.insiderfinance.io/?source=post_page---post_author_info--9c6fe1b489ad---------------------------------------)</p>
          <p>[Alyze Sam, “I’m just here to serve”](https://wire.insiderfinance.io/?source=post_page---post_author_info--9c6fe1b489ad---------------------------------------)</p>
          <p>2 min read</p>
          <p>1 hour ago</p>
          <p>[5 following](https://wire.insiderfinance.io/following?source=post_page---post_author_info--9c6fe1b489ad---------------------------------------)</p>
        </article>
      </body>
    </html>
    """

    result = pipeline.run(html)

    assert result.markdown == "# Title\n\nBody paragraph."


def test_medium_adapter_keeps_body_between_byline_and_publication_footer() -> None:
    """Medium cleanup should remove chrome without trimming the article body."""

    pipeline = HtmlToMarkdownPipeline(adapters=(MediumAdapter(),))
    html = """
    <html>
      <head>
        <meta property="og:site_name" content="Medium" />
        <meta property="og:url" content="https://infosecwriteups.com/post" />
      </head>
      <body>
        <article>
          <h1>I Pentested a Real CRM System</h1>
          <p>## **Author:** [Shikhali Jamalzade](https://medium.com/u/20557ba7487d?source=post_page---user_mention--98c030a57ab1---------------------------------------)</p>
          <p>[![Shikhali Jamalzade](https://miro.medium.com/v2/resize:fill:64:64/1*1y98p7kVR06Fq8997mI2FQ.png)](https://alisalive.medium.com/?source=post_page---byline--98c030a57ab1---------------------------------------)</p>
          <p>[Shikhali Jamalzade](https://alisalive.medium.com/?source=post_page---byline--98c030a57ab1---------------------------------------)</p>
          <p>12 min read</p>
          <p>May 13, 2026</p>
          <p>Disclosure notice.</p>
          <h2>Background</h2>
          <p>This is the real article body.</p>
          <p>[![InfoSec Write-ups](https://miro.medium.com/v2/resize:fill:96:96/1*SWJxYWGZzgmBP1D0Qg_3zQ.png)](https://infosecwriteups.com/?source=post_page---post_publication_info--98c030a57ab1---------------------------------------)</p>
          <p>[24 following](https://medium.com/@alisalive/following?source=post_page---post_author_info--98c030a57ab1---------------------------------------)</p>
        </article>
      </body>
    </html>
    """

    result = pipeline.run(html)

    assert (
        result.markdown
        == "# I Pentested a Real CRM System\n\nDisclosure notice.\n\n## Background\n\nThis is the real article body."
    )


def test_medium_adapter_trims_byline_after_subtitle() -> None:
    """Medium bylines may appear after a subtitle instead of directly after the title."""

    pipeline = HtmlToMarkdownPipeline(adapters=(MediumAdapter(),))
    html = """
    <html>
      <head>
        <meta property="og:site_name" content="Medium" />
        <meta property="og:url" content="https://medium.com/post" />
      </head>
      <body>
        <article>
          <h1>Tools Give Models Hands</h1>
          <h2>A missing state file let one instruction destroy live infrastructure.</h2>
          <p>[![Dr Peter McCann Strain](https://miro.medium.com/v2/resize:fill:64:64/1*2juj86FdrLWVBk6WU_44Kw.png)](https://medium.com/@peter.mccann.strain?source=post_page---byline--5a3cf8664ce8---------------------------------------)</p>
          <p>[Dr Peter McCann Strain](https://medium.com/@peter.mccann.strain?source=post_page---byline--5a3cf8664ce8---------------------------------------)</p>
          <p>16 min read</p>
          <p>4 days ago</p>
          <p>Body paragraph.</p>
        </article>
      </body>
    </html>
    """

    result = pipeline.run(html)

    assert (
        result.markdown
        == "# Tools Give Models Hands\n\n## A missing state file let one instruction destroy live infrastructure.\n\nBody paragraph."
    )
