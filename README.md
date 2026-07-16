# domdown

![domdown banner](assets/domdown-banner.jpg)

`domdown` turns article-like web pages into clean, structured Markdown.

It is built for pages where the shape matters: long-form posts, research writeups, technical blogs, security reports, and other content-heavy pages that need to become readable Markdown without losing useful structure.

## What it does

`domdown` takes care of the full HTML-to-Markdown pipeline:

- Parses messy web HTML
- Selects the main article content
- Removes navigation, promo blocks, and other chrome
- Extracts metadata
- Preserves images, tables, code blocks, links, and lists
- Optionally emits YAML frontmatter
- Renders the final Markdown document

The result is Markdown that is ready to read, reuse, archive, or feed into another model.

## Why it exists

Most pages are not written like clean documents. They mix article content with menus, banners, share widgets, related links, and other page furniture.

`domdown` is designed for cases where you want the content to stay faithful to the original page while still producing a clean Markdown output that is easy to consume downstream.

## Example

```python
from domdown import DomdownOptions, html_to_markdown

html = """
<html>
  <head>
    <title>Credential theft campaign expands</title>
    <meta name="description" content="A concise security article." />
    <link rel="canonical" href="https://example.com/research/campaign" />
  </head>
  <body>
    <nav>Home Pricing Docs</nav>
    <article>
      <h1>Credential theft campaign expands</h1>
      <p>Researchers observed a new wave of phishing infrastructure.</p>
      <figure>
        <img src="/images/chart.png" alt="Campaign infrastructure chart" />
        <figcaption>Campaign infrastructure by week.</figcaption>
      </figure>
      <ul>
        <li>Windows targets increased.</li>
        <li>Linux staging remained stable.</li>
      </ul>
    </article>
  </body>
</html>
"""

markdown = html_to_markdown(
    html,
    DomdownOptions(
        base_url="https://example.com/research/campaign",
    ),
)

print(markdown)
```

Output:

```markdown
---
title: Credential theft campaign expands
source: "https://example.com/research/campaign"
domdown_version: 0.3.6
description: A concise security article.
---
# Credential theft campaign expands

Researchers observed a new wave of phishing infrastructure.

![Campaign infrastructure chart](https://example.com/images/chart.png)

Campaign infrastructure by week.

- Windows targets increased.
- Linux staging remained stable.
```

## What it preserves

`domdown` is optimized for article-style pages where useful structure should survive the conversion:

- Titles and headings
- Visible author and publication metadata
- Canonical URLs and source references
- Images and captions
- Tables and code blocks
- Inline links and emphasized text
- Lists, quotes, and other document structure

## Using domdown

### Client usage

Use `html_to_markdown()` when you only need the final Markdown document as a string.

```python
from domdown import DomdownOptions, html_to_markdown

markdown = html_to_markdown(
    html,
    DomdownOptions(
        base_url="https://example.com/post",
        emit_frontmatter=False,
    ),
)
```

When `emit_frontmatter=True` or left at the default, the returned string includes YAML frontmatter followed by the Markdown body.

### API usage

Use `HtmlToMarkdownPipeline` when you want structured output.

```python
from domdown import DomdownOptions, HtmlToMarkdownPipeline

pipeline = HtmlToMarkdownPipeline(
    DomdownOptions(base_url="https://example.com/post")
)
result = pipeline.run(html)

print(result.document)
print(result.markdown)
print(result.cleaned_html)
print(result.frontmatter)
print(result.warnings)
```

`HtmlToMarkdownResult` exposes:

| Field | Type | Description |
| --- | --- | --- |
| `markdown` | `str` | Markdown rendered from the selected content. |
| `cleaned_html` | `str \| None` | HTML after parsing, selection, cleaning, and preservation. |
| `metadata` | `HtmlMetadata \| None` | Normalized metadata extracted from the source HTML. |
| `frontmatter` | `str \| None` | YAML frontmatter when enabled. |
| `document` | `str \| None` | Final document string, including frontmatter when enabled. |
| `warnings` | `tuple[str, ...]` | Non-fatal pipeline warnings. |

`HtmlMetadata` exposes:

| Field | Type |
| --- | --- |
| `title` | `str \| None` |
| `site_name` | `str \| None` |
| `source` | `str \| None` |
| `author` | `tuple[str, ...]` |
| `published` | `str \| None` |
| `created` | `str \| None` |
| `description` | `str \| None` |
| `tags` | `tuple[str, ...]` |
| `language` | `str \| None` |
| `canonical_url` | `str \| None` |
| `image` | `str \| None` |

## Options

`DomdownOptions` controls parsing, cleanup, metadata extraction, and output shaping.

| Option | Default | Behavior |
| --- | --- | --- |
| `base_url` | `None` | Source URL used for metadata and relative URL resolution. |
| `frontmatter_opts` | `{}` | Per-key fallback values used when rendering frontmatter. |
| `created` | `None` | Creation date to include in metadata/frontmatter. |
| `extract_metadata` | `True` | Enables metadata extraction. |
| `emit_frontmatter` | `True` | Prepends YAML frontmatter to `document`. |
| `prefer_article_body` | `True` | Prefers article-like containers during selection. |
| `author_priority` | `"visible"` | Chooses visible author text before metadata unless set otherwise. |
| `frontmatter_tags` | `()` | Extra tags to include in generated frontmatter. |
| `preserve_images` | `True` | Keeps images for Markdown rendering. |
| `preserve_tables` | `True` | Keeps tables for Markdown rendering. |
| `preserve_code_blocks` | `True` | Keeps code/preformatted blocks. |
| `strip_hidden` | `True` | Removes hidden or non-visible elements. |
| `remove_selectors` | `()` | CSS selectors to remove. |
| `keep_selectors` | `()` | CSS selectors to protect during cleaning. |
| `unwrap_selectors` | `()` | CSS selectors whose wrapper is removed while children remain. |

Example:

```python
from domdown import DomdownOptions

options = DomdownOptions(
    base_url="https://example.com/article",
    frontmatter_opts={
        "title": "Example Article",
        "source": "https://example.com/article",
    },
    emit_frontmatter=True,
    preserve_images=True,
    remove_selectors=(".share-widget", ".newsletter-signup"),
)
```

## Real-world coverage

`domdown` includes curated real-world HTML/Markdown pairs under `tests/real/` to protect the pipeline against regressions on live site shapes.

- `html/` stores the captured HTML for each case.
- `raw/` stores the expected Markdown output for the same case.
- `manifest.json` declares the cases and their relative fixture paths.

To run the real-example suite:

```bash
pytest tests/real/test_real_examples.py -q
```

## Public API

`domdown` exports these names from `domdown.__init__`:

```python
from domdown import (
    DomdownOptions,
    HtmlMetadata,
    HtmlToMarkdownPipeline,
    HtmlToMarkdownResult,
    html_to_markdown,
)
```

## Installation

Install from this repository:

```bash
pip install domdown
```

Install locally for development:

```bash
git clone https://github.com/juanmcristobal/domdown.git
cd domdown
pip install -e ".[dev]"
```

Runtime dependencies:

- `beautifulsoup4`
- `lxml`
- `soupsieve`
- `httpx`

## Support & Connect

* ⭐ **Star the repo** if you found it useful
* ☕ **Support me:** Say thanks by buying me a coffee! [https://buymeacoffee.com/juanmcristobal](https://buymeacoffee.com/juanmcristobal)
* 💼 **Open to work:** [https://www.linkedin.com/in/jmcristobal/](https://www.linkedin.com/in/jmcristobal/)
