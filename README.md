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
domdown_version: 0.3.8
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

## Discover and apply extraction criteria

`HtmlToMarkdownPipeline.run()` returns Markdown together with an extraction
criterion and a trace of active adapter and cleanup decisions:

```python
from domdown import DomdownOptions, ExtractionCriteria, HtmlToMarkdownPipeline

pipeline = HtmlToMarkdownPipeline(DomdownOptions(emit_frontmatter=False))
discovered = pipeline.run(html)

print(discovered.markdown)
print(discovered.criteria.to_json())
print(discovered.trace.to_dict())

criteria = ExtractionCriteria.from_json(discovered.criteria.to_json())
replayed = pipeline.run(html, criteria=criteria)
assert replayed.markdown == discovered.markdown
```

Criteria JSON uses schema version 1 and supports `include`, `exclude`, and
`unwrap` CSS selector arrays. The pipeline has three operation modes:

- **Discover** (`run(html)`): automatic root selection, cleanup heuristics, and
  extraction adapter hooks.
- **Exact replay** (`run(html, criteria=discovered.criteria)`): reuses recorded
  node references from the same HTML and DomDown version. It reproduces the
  discovered extraction, including applicable adapter hooks.
- **Selector apply** (`run(html, criteria=manual_criteria)`): applies portable
  selectors to the supplied document. Article-shaped selected roots receive
  the shared cleanup heuristics and adapter hooks.

Selector Apply uses `include`, `exclude`, and `unwrap` to choose and shape the
content. A selected `article` or `main`, or a root with at least 50 words, one
heading, and two paragraphs, receives `DomdownOptions.remove_selectors` (or the
default removal selectors), cleanup heuristics, and matching adapter hooks. If
it selects the same content as Discover with the same modifiers, the Markdown
matches. Smaller or structurally different explicit selections preserve their
selector override behavior and can produce different content by design.
Portable selectors can also select different roots on other documents.
Set `shared_cleanup="force"` on `ExtractionCriteria` to run cleanup and
matching adapter hooks on an alternate selected root. Use `"off"` to suppress
the shared heuristics even for an article-shaped root. The default `"auto"`
enables cleanup for article-shaped selections and preserves smaller or
structurally different selections.

Generated criteria also carry document-specific
node references so they can replay the exact nodes retained by the automatic
pipeline, including adapter and heuristic removals. Those references apply to
the same parsed HTML and DomDown version; they are not portable page selectors.
Editing a selector invalidates the recorded replay and switches to explicit
replace semantics.

Manually authored criteria replace automatic root selection. Article-shaped
selected content goes through the standard cleanup and adapter processing:

```python
criteria = ExtractionCriteria(
    include=("article.main-content",),
    exclude=(".ads", ".newsletter"),
    unwrap=(".content-wrapper",),
)
result = pipeline.run(html, criteria=criteria)
```

`include` must match at least one element. Invalid selectors and unmatched
includes raise `CriteriaError`; unmatched exclusions are allowed. An exclusion
matching an included root produces empty content. `unwrap` cannot target the
included root. Parsing, URL preparation, semantic conversion, rendering, and
frontmatter remain on the existing pipeline.

For pages with more than one layout, `include_fallback` tries selectors in
order and uses the first whose matched content reaches `min_words` (50 by
default). Candidates are exclusive; they are not combined. If none reaches the
threshold, Domdown uses the matched candidate with the most words. The original
`include` array keeps its union behavior.

`drop_text` accepts regular expressions matched against complete, stripped
`NavigableString` nodes. This lets criteria remove standalone labels or
placeholders that CSS cannot target while preserving those phrases inside
ordinary prose. The built-in cleanup also removes standalone numbered markers
such as `placeholder(#1)`. Cleanup detects a compact table of contents only
when it is immediately after the first heading and consists of at least three
in-page anchor links.

Discover and exact replay report a `Possible empty shell` warning when an HTML
source is at least 512 characters and the extraction contains fewer than 10
words. Selector Apply reports the warning whenever an include matches but the
rendered result contains fewer than 10 words, and reports the matched element
count. If no include matches in a larger document, `CriteriaError` identifies
an empty shell or stale selector as likely causes.

GitHub release pages may fetch expanded assets from GitHub during conversion.
Their trace marks replay as conditional on the same external fragment being
available and unchanged.

`result.trace.to_dict()` records the execution mode, selector match and mutation
counts, warnings, and compact content metrics (words, headings, paragraphs,
links, lists, tables, and code blocks before and after extraction). It does not
store the source HTML; `before.words` counts selected source text and `after.words`
counts rendered Markdown words. Zero-valued metric entries are omitted. CSS selectors operate on elements, so direct text nodes
inside an included element cannot be targeted by `exclude` or `unwrap`; preserve
them or wrap the unwanted text in an element and exclude that element.

The convenience `html_to_markdown(html, options, *, criteria=...)` accepts the
same override and continues to return a string. Use `HtmlToMarkdownPipeline`
when Discover metadata and the trace are needed.

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
| `preserve_images` | `True` | Declared option; currently does not change rendering. |
| `preserve_tables` | `True` | Declared option; currently does not change rendering. |
| `preserve_code_blocks` | `True` | Declared option; currently does not change rendering. |
| `strip_hidden` | `True` | Declared option; hidden-element filtering is not currently applied. |
| `remove_selectors` | `()` | CSS selectors to remove. |
| `keep_selectors` | `()` | Declared option; currently does not protect nodes during cleaning. |
| `unwrap_selectors` | `()` | Declared option; use `ExtractionCriteria.unwrap` for Apply. |

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
