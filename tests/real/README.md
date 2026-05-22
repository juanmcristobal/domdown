# Real Examples

This directory stores curated real-world HTML/Markdown pairs that protect `domdown`
against regressions on live site shapes.

## Layout

- `html/` stores the captured HTML for each case.
- `raw/` stores the expected Markdown output for the same case.
- `manifest.json` declares the cases and their relative fixture paths.

## Adding a case

1. Copy the source HTML into `html/<case-id>.html`.
2. Copy the expected Markdown snapshot into `raw/<case-id>.md`.
3. Add an entry to `manifest.json` with the relative paths.
4. Run `pytest tests/real/test_real_examples.py -q`.

Keep the set small and curated. Use synthetic tests for local behavior and real cases for regressions.
