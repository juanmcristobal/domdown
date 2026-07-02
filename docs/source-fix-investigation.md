# Source Fix Investigation Playbook

Use this guide when a user gives you a new source URL or raw page and asks you to investigate a fix.

## Goal

Find the narrowest change that improves extraction for the provided source while keeping the rest of the corpus stable.
The rest of the corpus should keep working the same unless the change is a deliberate, verified improvement.

## Inputs

- The source URL or raw HTML.
- The observed failure mode, if any.
- Any nearby failing tests or snapshots.
- Use `crawlsmith` to download the HTML that will be inspected and compared.

## Workflow

1. Reproduce the source locally.
2. Use `crawlsmith` to download the source HTML you will inspect.
3. Compare the current Markdown output with the expected behavior.
4. Determine where the failure happens:
   - source fetching
   - root selection
   - cleanup
   - metadata extraction
   - adapter-specific behavior
5. Decide whether the issue is:
   - source-specific and should stay in a fixture
   - generic enough to fix in core logic
   - better handled with a small targeted exception
6. Implement the smallest generic fix that addresses the observed shape.
7. Add a regression test that proves the fix.
8. Prefer a real example fixture when the source is stable and useful.
9. Run the smallest relevant test set first, then the real suite.

## Fix Strategy

Use this order of preference:

1. Generic core fix.
2. Small selector or cleanup heuristic.
3. Adapter-specific handling only when the page shape is truly unique.
4. Source-specific snapshot only when the page is a stable regression case.

Avoid fixes that:

- Make one source better by making another known source worse.
- Remove content that could be legitimate on other pages.
- Encode brittle page-specific selectors unless no safer option exists.

## Fixture Strategy

When adding a new real example:

- Store the crawlsmith-captured HTML under `tests/real/html/`.
- Store the expected Markdown under `tests/real/raw/`.
- Register the case in `tests/real/manifest.json`.
- Keep the fixture small but representative.
- Include the problematic structure that triggered the bug.
- Preserve any sidebar, promo, TOC, or navigation shape needed to exercise the fix.

## Validation

Always validate with:

1. The targeted document test, if one exists.
2. The real example suite.
3. Any nearby regression tests that might be affected.

If the new source improves but another curated case regresses, do not stop at the first fix. Reassess the heuristic and make it more generic.
If behavior changes elsewhere, investigate whether the new source is improving or worsening overall before deciding to keep the change.

## Reporting Back

When you finish, report:

- What broke.
- Where the fix lives.
- Why the fix is generic.
- Which tests you ran.
- Whether any sources were left unchanged by design.
