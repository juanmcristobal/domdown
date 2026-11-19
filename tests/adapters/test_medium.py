from __future__ import annotations

from domdown import DomdownOptions, ExtractionCriteria, HtmlToMarkdownPipeline


def test_medium_document_features_recognize_custom_publication_hosts() -> None:
    html = """
    <html><head>
      <meta property="og:site_name" content="Medium" />
      <meta property="og:url" content="https://infosecwriteups.com/post" />
    </head><body><article><h1>Title</h1><p>Body.</p></article></body></html>
    """

    result = HtmlToMarkdownPipeline(DomdownOptions(emit_frontmatter=False)).run(html)

    assert result.trace.to_dict()["criteria_source"] == "site"
    assert result.markdown == "# Title\n\nBody."


def test_medium_css_and_text_rules_remove_chrome_but_keep_article_body() -> None:
    html = """
    <html><head><meta property="og:site_name" content="Medium" /></head><body>
      <header><nav>InfoSec Write-ups</nav></header>
      <article>
        <p>Mastodon</p>
        <p>Press enter or click to view image in full size</p>
        <h1>Title</h1>
        <p>Body paragraph.</p>
        <p>·</p><p>--</p>
        <p><strong>Help:</strong> <a href="https://help.medium.com/hc/en-us">Help</a></p>
        <p><strong>Privacy:</strong> <a href="https://policy.medium.com">Privacy</a></p>
      </article>
    </body></html>
    """

    result = HtmlToMarkdownPipeline(DomdownOptions(emit_frontmatter=False)).run(html)

    assert result.markdown == "# Title\n\nBody paragraph."


def test_medium_drop_text_removes_lab_preamble_without_dropping_prose() -> None:
    html = """
    <html><head><meta property="og:site_name" content="Medium" /></head><body>
      <article>
        <h1>User ID Controlled By Request Parameter With Password Disclosure</h1>
        <p>Access Control Vulnerabilities — APPRENTICE</p>
        <p>Lab-Access Control Vulnerabilities</p>
        <p>This lab has a user account page.</p>
      </article>
    </body></html>
    """

    result = HtmlToMarkdownPipeline(DomdownOptions(emit_frontmatter=False)).run(html)

    assert result.markdown == (
        "# User ID Controlled By Request Parameter With Password Disclosure\n\n" "This lab has a user account page."
    )


def test_medium_byline_links_and_read_time_are_removed_with_css_and_drop_text() -> None:
    html = """
    <html><head><meta property="og:site_name" content="Medium" /></head><body>
      <article>
        <h1>Title</h1>
        <p><a href="https://medium.com/@author"><img alt="Author" src="https://miro.medium.com/avatar.png"></a></p>
        <p><a href="https://medium.com/@author">Author</a></p>
        <p>3 min read</p><p>Just now</p>
        <p>Body paragraph.</p>
      </article>
    </body></html>
    """

    result = HtmlToMarkdownPipeline(DomdownOptions(emit_frontmatter=False)).run(html)

    assert result.markdown == "# Title\n\nBody paragraph."


def test_medium_author_footer_removes_following_preamble_only_after_footer_marker() -> None:
    html = """
    <html><head><meta property="og:site_name" content="Medium" /></head><body>
      <article>
        <h1>Title</h1><p>Body paragraph.</p>
        <p><a href="https://medium.com/@author?source=post_page---post_author_info--abc"><img alt="Author" src="/avatar.png"></a></p>
        <p><a href="https://medium.com/@author?source=post_page---post_author_info--abc">Author</a></p>
        <p>7 min read</p><p>1 hour ago</p>
        <p>Author biography should be removed with the footer.</p>
      </article>
    </body></html>
    """

    result = HtmlToMarkdownPipeline(DomdownOptions(emit_frontmatter=False)).run(html)

    assert result.markdown == "# Title\n\nBody paragraph."


def test_medium_custom_publication_footer_uses_feature_match_and_replays() -> None:
    html = """
    <html><head>
      <meta property="og:site_name" content="Medium" />
      <meta property="og:url" content="https://wire.example/post" />
    </head><body><article>
      <h1>Title</h1><p>Body paragraph.</p>
      <p><a href="https://wire.example/?source=post_page---post_author_info--abc">Author</a></p>
      <p><a href="https://wire.example/following?source=post_page---post_author_info--abc">5 following</a></p>
      <p>2 min read</p><p>1 hour ago</p>
    </article></body></html>
    """
    pipeline = HtmlToMarkdownPipeline(DomdownOptions(emit_frontmatter=False))

    discovered = pipeline.run(html)
    replayed = pipeline.run(html, criteria=ExtractionCriteria.from_json(discovered.criteria.to_json()))

    assert discovered.trace.to_dict()["criteria_source"] == "site"
    assert discovered.criteria.drop_text
    assert discovered.markdown == replayed.markdown == "# Title\n\nBody paragraph."


def test_medium_byline_before_body_and_publication_footer_preserve_body() -> None:
    html = """
    <html><head><meta property="og:site_name" content="Medium" /></head><body>
      <article>
        <h1>I Pentested a Real CRM System</h1>
        <p><strong>Author:</strong> <a href="https://medium.com/u/person?source=post_page---user_mention--abc">Writer</a></p>
        <p><a href="https://writer.medium.com/?source=post_page---byline--abc"><img alt="Writer" src="/writer.png"></a></p>
        <p><a href="https://writer.medium.com/?source=post_page---byline--abc">Writer</a></p>
        <p>12 min read</p><p>May 13, 2026</p>
        <p>Disclosure notice.</p>
        <h2>Background</h2><p>This is the real article body.</p>
        <p><a href="https://publication.example/?source=post_page---post_publication_info--abc">Publication</a></p>
        <p><a href="https://medium.com/@writer/following?source=post_page---post_author_info--abc">24 following</a></p>
      </article>
    </body></html>
    """

    result = HtmlToMarkdownPipeline(DomdownOptions(emit_frontmatter=False)).run(html)

    assert result.markdown == (
        "# I Pentested a Real CRM System\n\nDisclosure notice.\n\n" "## Background\n\nThis is the real article body."
    )


def test_medium_byline_after_subtitle_does_not_remove_body() -> None:
    html = """
    <html><head><meta property="og:site_name" content="Medium" /></head><body>
      <article>
        <h1>Tools Give Models Hands</h1>
        <h2>A missing state file let one instruction destroy live infrastructure.</h2>
        <p><a href="https://medium.com/@writer?source=post_page---byline--abc"><img alt="Writer" src="/writer.png"></a></p>
        <p><a href="https://medium.com/@writer?source=post_page---byline--abc">Writer</a></p>
        <p>16 min read</p><p>4 days ago</p><p>Body paragraph.</p>
      </article>
    </body></html>
    """

    result = HtmlToMarkdownPipeline(DomdownOptions(emit_frontmatter=False)).run(html)

    assert result.markdown == (
        "# Tools Give Models Hands\n\n## A missing state file let one instruction destroy live infrastructure.\n\n"
        "Body paragraph."
    )
