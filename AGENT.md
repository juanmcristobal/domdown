# AGENT.md

This repository uses a source-driven workflow for HTML-to-Markdown regressions.

When a new source is provided for investigation:

1. Use `crawlsmith` to download the HTML for that exact source.
2. Reproduce the current output against that downloaded HTML.
3. Inspect the extracted structure, not just the final Markdown.
4. Prefer the smallest generic fix that improves the source without harming nearby cases.
5. Add or update a real fixture when the source is stable and representative.
6. Verify the change with targeted tests and the real example suite.
7. Keep the rest of the corpus behaving the same. If the change does not preserve that behavior, investigate whether the new source is actually better or worse before keeping the fix.

For the full procedure, see [docs/source-fix-investigation.md](docs/source-fix-investigation.md).
For adapter work, see [docs/adapter-development-guide.md](docs/adapter-development-guide.md).
