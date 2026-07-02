# Adapter Development Guide

Use this guide when you want to add a new adapter for a site family or page shape that needs behavior beyond the generic pipeline.

## Goal

Create the smallest adapter that fixes the target site shape without changing unrelated sites.

## When To Add An Adapter

Add an adapter when:

- The site has repeated chrome or layout patterns that the generic pipeline cannot remove cleanly.
- The site needs page-family-specific matching, preprocessing, metadata refinement, or postprocessing.
- A declarative domain adapter is not enough.

Do not add an adapter when:

- A generic core fix is sufficient.
- The issue can be solved by improving selection or cleanup once for all sources.
- The page is a one-off regression that belongs in a real fixture only.

## Preferred Order

1. Try the generic pipeline first.
2. If the site is domain-based and simple, use a declarative domain adapter.
3. If the site needs richer logic, implement a custom adapter class.
4. Add real fixtures and tests before expanding the adapter further.

## Workflow

1. Use `crawlsmith` to download the HTML for representative pages.
2. Inspect at least one good page and one problematic page from the same site family.
3. Identify the exact shape the adapter must handle:
   - matching
   - preprocessing
   - metadata refinement
   - postprocessing
4. Decide whether the site can be covered by `DomainAdapterSpec`.
5. If not, add a custom adapter under `domdown/adapters/`.
6. Register the adapter in `domdown/adapters/__init__.py`.
7. Add the adapter to the default registry only if it should be enabled globally.
8. Add unit tests under `tests/adapters/`.
9. Add or update real fixtures under `tests/real/` when the site shape is stable.
10. Run the adapter tests and the real-example suite.

## Real Example

Two good examples of site-specific adapters are:

- `https://arxiv.org/abs/2603.28627`
- `https://en.wikipedia.org/wiki/Elliptic-curve_cryptography`

What the adapter does:

- Matches the site family using a stable host or site name signal.
- Keeps the article or abstract body.
- Removes page chrome such as sidebars, navigation, and reference blocks.
- Normalizes the title line so the output starts with the content title instead of the site chrome.
- Uses the page metadata title when it is reliable.

What the implementation and tests include:

- A custom adapter class in `domdown/adapters/`.
- Registration in the default adapter list.
- A focused adapter test in `tests/adapters/`.
- A real fixture pair in `tests/real/` with captured HTML and expected Markdown.

## Design Rules

- Keep matching logic strict enough to avoid false positives.
- Keep preprocessing focused on structure removal, normalization, or wrapper cleanup.
- Keep metadata refinement limited to facts the adapter can determine reliably.
- Keep postprocessing small and predictable.
- Avoid page-specific hacks unless the site family is truly narrow and stable.

## Matching Guidance

An adapter should match only when there is a clear signal such as:

- a stable host or suffix
- a stable `site_name`
- a stable page structure that is unique to the site family
- a combination of host and metadata that reduces false positives

Prefer deterministic matching over fuzzy text matching when possible.

## Test Strategy

Add tests that prove the adapter does not regress other sources:

- A direct adapter test for the intended behavior.
- A negative test when the adapter should not match unrelated pages.
- A real example snapshot if the page family is known and stable.

If the adapter changes the output for unrelated pages, revisit the matching rule before broadening the adapter.

## Acceptance Criteria

An adapter is ready when:

- The target page family renders correctly.
- The change is isolated to the intended sources.
- The rest of the corpus still behaves the same.
- The tests document the behavior clearly.
