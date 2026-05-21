# domdown

`domdown` extracts the main content from web pages and returns cleaned HTML, optional markdown, and structured metadata.

It is the Python port of the Node `domdown` package. The goal is functional parity: same intent, same pipeline, same extraction behavior where the DOM model allows it. It is not a byte-for-byte port of the underlying DOM operations because this package uses `beautifulsoup4` and `lxml`.

## What it does

`domdown` is built for content extraction, not generic scraping. It tries to:

- identify the main article or post
- remove navigation, ads, hidden clutter, and other boilerplate
- normalize structure so the output is readable
- extract page metadata like title, author, description, language, published date, site, and word count
- detect site-specific formats such as YouTube transcripts, Reddit threads, GitHub issues, Substack posts, Hacker News stories, and more

The output is a `DomdownResponse` object with cleaned content plus metadata.

## Installation

Install from the repository:

```bash
pip install .
```

Install editable for development:

```bash
pip install -e ".[dev]"
```

This installs the development tools used in the repo, including:

- `pytest`
- `black`
- `isort`
- `flake8`
- `coverage`

## CLI

The installed command is `domdown`.

### Parse a URL

```bash
domdown parse https://example.com/article
```

### Parse a local HTML file

```bash
domdown parse ./page.html
```

### Output markdown

```bash
domdown parse https://example.com/article --markdown
```

### Output JSON

```bash
domdown parse https://example.com/article --json
```

### Output plain text

```bash
domdown parse https://example.com/article --plain-text
```

### Extract a single property

```bash
domdown parse https://example.com/article --property title
domdown parse https://example.com/article --property author
domdown parse https://example.com/article --property domain
```

### Write output to a file

```bash
domdown parse https://example.com/article --markdown --output article.md
```

### Prefer a language

```bash
domdown parse https://example.com/article --lang es
```

### Debug parsing

```bash
domdown parse https://example.com/article --debug
```

## Python API

### Public exports

```python
from domdown import Domdown, DomdownOptions, DomdownResponse
```

### High-level parse helpers

Use `domdown.node.parse()` or `domdown.node.parse_async()` when you have raw HTML and want a ready-to-use result:

```python
from domdown.node import parse, parse_async
```

These helpers:

- create the Beautiful Soup document
- run the extraction pipeline
- apply markdown conversion if requested
- return a `DomdownResponse`

### Synchronous example

```python
from domdown import DomdownOptions
from domdown.node import parse

html = """
<html>
  <head>
    <title>Example</title>
  </head>
  <body>
    <article>
      <h1>Hello</h1>
      <p>This is a test article.</p>
    </article>
  </body>
</html>
"""

result = parse(
    html,
    "https://example.com/article",
    DomdownOptions(markdown=True),
)

print(result.title)
print(result.author)
print(result.word_count)
print(result.content)
```

### Asynchronous example

```python
import asyncio

from domdown import DomdownOptions
from domdown.node import parse_async


async def main() -> None:
    result = await parse_async(
        html="<html><body><article><p>Hello world.</p></article></body></html>",
        url="https://example.com/article",
        options=DomdownOptions(separate_markdown=True),
    )

    print(result.content)
    print(result.content_markdown)


asyncio.run(main())
```

### Low-level parser

If you already have a Beautiful Soup document, you can use the lower-level class directly:

```python
from bs4 import BeautifulSoup

from domdown import DomdownOptions
from domdown.domdown import Domdown
from domdown.markdown import to_markdown

doc = BeautifulSoup("<html><body><article><p>Hello.</p></article></body></html>", "lxml")
opts = DomdownOptions(url="https://example.com", markdown=True)

result = Domdown(doc, opts).parse()
to_markdown(result, opts, opts.url or "")

print(result.content)
```

## Output modes

### Default

The default mode returns cleaned HTML in `content`.

### Markdown

With `markdown=True`, the main `content` field is converted to markdown.

### Separate markdown

With `separate_markdown=True`, the main `content` field stays as HTML and the markdown version is stored in `content_markdown`.

### Plain text

The CLI `--plain-text` flag strips HTML tags from the extracted content before printing.

### JSON

The CLI `--json` flag prints a structured JSON object with metadata and content fields.

## Result object

`parse()` and `parse_async()` return a `DomdownResponse`.

Common fields:

- `title`
- `description`
- `domain`
- `favicon`
- `image`
- `language`
- `parse_time`
- `published`
- `author`
- `site`
- `schema_org_data`
- `word_count`
- `content`
- `content_markdown`
- `extractor_type`
- `meta_tags`
- `debug`
- `profile`
- `variables`

### Field notes

- `content` is the main extracted body.
- `content_markdown` is populated only when markdown conversion is requested separately.
- `variables` is used by site-specific extractors for extra structured metadata.
- `debug` is filled when `debug=True`.
- `profile` is filled when `profile=True`.

## Options

`DomdownOptions` controls the pipeline:

- `debug`: include debug extraction information
- `url`: canonical URL associated with the document
- `markdown`: convert `content` to markdown
- `separate_markdown`: keep HTML in `content` and markdown in `content_markdown`
- `remove_exact_selectors`: remove exact-match boilerplate selectors
- `remove_partial_selectors`: remove partial-match boilerplate selectors
- `remove_images`: strip image content in the extraction pipeline
- `use_async`: allow async fallback extraction paths
- `remove_hidden_elements`: remove hidden DOM elements
- `remove_low_scoring`: drop low-scoring content blocks
- `remove_small_images`: remove images that look like placeholders or tiny assets
- `standardize`: normalize structure after extraction
- `remove_content_patterns`: remove known boilerplate patterns
- `content_selector`: force a specific content selector
- `language`: preferred language code
- `include_replies`: control whether extractor replies/comments are included
- `profile`: collect timing data
- `fetch`: custom async fetch function for extractors that need network access

## Supported sources

`domdown` includes site-specific extractors for patterns such as:

- YouTube
- GitHub
- Reddit
- Hacker News
- Substack
- LinkedIn
- Mastodon
- Bluesky
- Threads
- X / Twitter
- ChatGPT
- Gemini
- Claude
- Wikipedia
- LeetCode
- LWN
- Discourse
- NYTimes
- BBCode-based content
- and generic extractor paths for normal articles

Coverage is intentionally broad, but the exact extractor chosen depends on the page structure and URL.

## Development

Run the test suite:

```bash
python -m pytest -q
```

Run linting:

```bash
make lint
```

Format code:

```bash
python -m black domdown tests
python -m isort domdown tests
```

Run coverage locally:

```bash
coverage run -m pytest -q
coverage report
```

Or get a quick terminal summary with missing lines:

```bash
coverage run -m pytest -q && coverage report -m
```

If you want an HTML report:

```bash
coverage html
```

The HTML output is written to `htmlcov/`.

## Architecture notes

- The package lives at `domdown/` with no `src/` wrapper.
- The public API is exposed from `domdown.__init__`.
- Internal helpers are split into:
  - `domdown/utils/`
  - `domdown/elements/`
  - `domdown/removals/`
  - `domdown/extractors/`
- The implementation is intentionally conceptually aligned with the Node version, but DOM behavior differs where `bs4` and `lxml` behave differently from the Node DOM stack.

## Behavior notes

- The parser tries to preserve content structure where possible.
- Markdown conversion is a post-processing step on top of extracted content.
- If a site-specific extractor matches, it can override the generic pipeline.
- Some edge cases will not match Node exactly because of parser differences, but the test suite is built to validate the intended behavior.

## Testing

The repository includes fixtures for:

- extraction pipeline behavior
- metadata extraction
- content standardization
- markdown conversion
- site-specific extractors
- debug and profile output
- edge cases such as surrogates, transcripts, and schema fallback

If you change the extraction pipeline, run the full suite before merging.

For development, coverage is configured in `pyproject.toml` to measure the `domdown` package and show missing lines in reports.

## Example workflow

1. Fetch or load HTML.
2. Call `domdown.node.parse()` or `domdown.node.parse_async()`.
3. Inspect `result.content` and metadata fields.
4. Use `result.content_markdown` when markdown was requested separately.
5. Use `--json` if you want a machine-readable summary from the CLI.

## Notes

- `domdown` is intentionally pragmatic rather than perfect.
- The priority is to solve the same extraction problem as the Node package.
- If you need exact DOM parity, you would need a different parser stack.
