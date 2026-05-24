# domdown

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)

`domdown` converts raw HTML into Markdown using the implementation that exists
in this branch: a Python pipeline for article-like content, metadata extraction,
HTML cleaning, Markdown rendering, optional YAML frontmatter, and a small adapter
system.

The current public API is Python-only. This branch does not document a CLI and
does not ship a broad "supported sources" matrix.

## Current Branch Scope

This branch supports:

- raw HTML input as a string
- article/body selection from parsed HTML
- metadata extraction into `HtmlMetadata`
- optional YAML frontmatter
- cleaned HTML output from the pipeline
- Markdown rendering for headings, paragraphs, links, images, captions, lists,
  tables, and code blocks
- configurable removal, preservation, and unwrapping through CSS selectors
- a default GitHub adapter for common GitHub chrome and file/issue page shapes

This branch does not provide:

- browser execution for JavaScript-rendered pages
- network fetching as part of the public API
- a documented command-line interface
- domain-by-domain support guarantees
- byte-for-byte parity with any Node implementation

## Quick Start

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
    DomdownOptions(base_url="https://example.com/research/campaign"),
)

print(markdown)
```

Output:

```markdown
---
title: Credential theft campaign expands
source: "https://example.com/research/campaign"
description: A concise security article.
---
# Credential theft campaign expands

Researchers observed a new wave of phishing infrastructure.

![Campaign infrastructure chart](https://example.com/images/chart.png)

Campaign infrastructure by week.

- Windows targets increased.
- Linux staging remained stable.
```

## Installation

Install from this repository:

```bash
pip install git+https://github.com/juanmcristobal/domdown.git
```

Install locally for development:

```bash
git clone https://github.com/juanmcristobal/domdown.git
cd domdown
pip install -e ".[dev]"
```

Runtime requirements are declared in `requirements.txt`:

- `beautifulsoup4`
- `lxml`
- `soupsieve`
- `httpx`

## Public API

The package exports these names from `domdown.__init__`:

```python
from domdown import (
    DomdownOptions,
    HtmlMetadata,
    HtmlToMarkdownPipeline,
    HtmlToMarkdownResult,
    html_to_markdown,
)
```

### `html_to_markdown`

Use `html_to_markdown()` when you only need the final document string.

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

`html_to_markdown()` runs the default pipeline and returns the final rendered
document. When frontmatter is enabled, that document includes the frontmatter.

### `HtmlToMarkdownPipeline`

Use `HtmlToMarkdownPipeline` when you need structured output.

```python
from domdown import DomdownOptions, HtmlToMarkdownPipeline

result = HtmlToMarkdownPipeline(
    DomdownOptions(base_url="https://example.com/post")
).run(html)

print(result.markdown)
print(result.cleaned_html)
print(result.frontmatter)
print(result.document)
print(result.warnings)

if result.metadata:
    print(result.metadata.title)
    print(result.metadata.source)
    print(result.metadata.canonical_url)
```

`HtmlToMarkdownResult` contains:

| Field | Type | Description |
| --- | --- | --- |
| `markdown` | `str` | Markdown rendered from the selected content. |
| `cleaned_html` | `str \| None` | HTML after parsing, selection, cleaning, and preservation. |
| `metadata` | `HtmlMetadata \| None` | Normalized metadata extracted from the source HTML. |
| `frontmatter` | `str \| None` | YAML frontmatter when enabled. |
| `document` | `str \| None` | Final document string, including frontmatter when enabled. |
| `warnings` | `tuple[str, ...]` | Non-fatal pipeline warnings. |

`HtmlMetadata` contains:

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

`DomdownOptions` controls the pipeline.

| Option | Default | Behavior |
| --- | --- | --- |
| `base_url` | `None` | Source URL used for metadata and relative URL resolution. |
| `created` | `None` | Creation date to include in metadata/frontmatter. |
| `extract_metadata` | `True` | Enables metadata extraction. |
| `emit_frontmatter` | `True` | Prepends YAML frontmatter to `document`. |
| `prefer_article_body` | `True` | Prefers article-like containers during selection. |
| `author_priority` | `"visible"` | Chooses visible author text before metadata unless set otherwise. |
| `frontmatter_tags` | `()` | Extra tags to include in generated frontmatter. |
| `preserve_images` | `True` | Keeps images for Markdown rendering. |
| `preserve_tables` | `True` | Keeps tables for Markdown rendering. |
| `preserve_code_blocks` | `True` | Keeps code/preformatted blocks. |
| `strip_hidden` | `True` | Removes hidden/non-visible elements. |
| `remove_selectors` | `()` | CSS selectors to remove. |
| `keep_selectors` | `()` | CSS selectors to protect during cleaning. |
| `unwrap_selectors` | `()` | CSS selectors whose wrapper is removed while children remain. |

Example:

```python
from domdown import DomdownOptions, HtmlToMarkdownPipeline

options = DomdownOptions(
    base_url="https://example.com/report",
    emit_frontmatter=True,
    remove_selectors=(".newsletter", ".share-buttons", "[data-ad]"),
    keep_selectors=("main", "article"),
    preserve_tables=True,
)

result = HtmlToMarkdownPipeline(options).run(html)
```

## Markdown Behavior

The renderer in this branch covers these structures:

| HTML input | Markdown behavior |
| --- | --- |
| `h1` to `h6` | Markdown headings |
| `p` | Paragraphs |
| `a` | Inline Markdown links |
| `img` | Markdown images, using useful `src`/`srcset` candidates |
| `figcaption` | Caption text near the image |
| `ul`, `ol`, `li` | Ordered and unordered Markdown lists, including nested lists |
| `table` | GitHub-flavored Markdown table syntax |
| `pre`, `code` | Fenced code blocks and inline code |
| metadata tags | `HtmlMetadata` and optional YAML frontmatter |

Relative URLs are resolved when `base_url` is provided.

## Pipeline

The default pipeline runs these stages in order:

1. Parse raw HTML.
2. Extract metadata.
3. Clean boilerplate and hidden content.
4. Preserve structural elements before Markdown conversion.
5. Render Markdown.
6. Post-process Markdown.
7. Compose frontmatter and final document.

The default pipeline also creates an adapter registry. In this branch, the
default adapter list contains `GitHubAdapter`.

## Adapters

Adapters are internal extension points that can:

- preprocess a parsed document
- refine metadata
- post-process rendered output

`GitHubAdapter` currently matches pages whose Open Graph site name is `GitHub`.
It removes common GitHub chrome and narrows some blob/issue pages to more useful
content regions. It is not a guarantee that every GitHub page shape is supported.

## Real Fixtures

`tests/real/` contains curated HTML and Markdown pairs used as regression tests.
Those fixtures cover representative pages from real sites, including GitHub
cases, but they are not a public support matrix.

If behavior changes, update or add fixtures intentionally:

1. Add captured HTML under `tests/real/html/`.
2. Add expected Markdown under `tests/real/raw/`.
3. Register the case in `tests/real/manifest.json`.
4. Run `python3 -m pytest tests/real/test_real_examples.py -q`.

## Development

Run tests:

```bash
python3 -m pytest -q
```

Run coverage:

```bash
python3 -m coverage run --source domdown -m pytest
python3 -m coverage report -m
```

Run formatting and linting:

```bash
python3 -m black domdown tests
python3 -m isort domdown tests
python3 -m flake8 domdown tests
```

## Status

`domdown` is early-stage software. Treat the exports from `domdown.__init__` as
the documented public API for this branch. Internal modules and adapter behavior
may change as extraction quality improves.
