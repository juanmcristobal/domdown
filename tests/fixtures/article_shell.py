from __future__ import annotations

ARTICLE_SHELL_HTML = """
<html>
  <head>
    <meta property="og:title" content="Example Article Title" />
    <link rel="canonical" href="https://example.com/articles/example-article" />
    <meta name="description" content="Example description for a synthetic article." />
  </head>
  <body>
    <article class="article-shell article-shell--variant-a">
      <header class="article-shell__header">
        <div class="breadcrumb">section / article</div>
        <div class="published">Aug 16, 2023</div>
        <h1 class="story-title">Example Article Title</h1>
        <div class="author_debug_inline">slug="example-article-slug", total=1</div>
        <div class="postmeta"><a href="/authors/example-author">Example Author</a></div>
        <div class="share-widget">
          <div class="share-widget__title">Share this article</div>
          <a href="https://example.com/share?text=Example">share</a>
        </div>
        <div class="more-link">more</div>
      </header>
      <div class="article-shell__body">
        <div class="content content--narrow">
          <span id="content-root">
            <h3>Background:</h3>
            <p>One paragraph of article content appears here.</p>
            <p><strong>Tool Name</strong></p>
            <p><strong><img src="https://example.com/tool.png" alt="Tool Name" /></strong></p>
            <p>Thanks to the researchers who worked on this example.</p>
          </span>
        </div>
      </div>
      <div class="article-shell__tags single-tags">Example Topic</div>
    </article>
  </body>
</html>
"""

__all__ = ["ARTICLE_SHELL_HTML"]
