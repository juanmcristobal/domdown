# Root Python Modularization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Split the remaining root-level Python modules into smaller concern-focused modules while preserving the public API and existing behavior.

**Architecture:** Keep the current root modules as thin facades and move the actual implementation into internal subpackages by responsibility: shared models, document parsing/cleanup, metadata extraction, frontmatter serialization, and text helpers. This keeps imports stable for callers while reducing file size and improving the locality of future changes.

**Tech Stack:** Python 3.10+, BeautifulSoup4, lxml, pytest

---

### Task 1: Split shared models and helpers

**Files:**
- Create: `domdown/core/options.py`
- Create: `domdown/core/metadata.py`
- Create: `domdown/core/result.py`
- Create: `domdown/core/context.py`
- Modify: `domdown/types.py`
- Test: `tests/test_public_api.py`

- [ ] **Step 1: Write the failing test**

```python
from domdown.core.options import DomdownOptions

def test_core_options_module_exports_domdown_options():
    assert DomdownOptions.__name__ == "DomdownOptions"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_public_api.py -v`
Expected: fail with `ModuleNotFoundError` before the new module exists.

- [ ] **Step 3: Write minimal implementation**

```python
from ..types import DomdownOptions

__all__ = ["DomdownOptions"]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_public_api.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add domdown/core domdown/types.py tests/test_public_api.py
git commit -m "refactor(core): split shared models"
```

### Task 2: Split document helpers

**Files:**
- Create: `domdown/document/parse.py`
- Create: `domdown/document/select.py`
- Create: `domdown/document/clean.py`
- Modify: `domdown/document.py`
- Modify: `domdown/stages/parse.py`
- Modify: `domdown/stages/clean.py`
- Test: `tests/test_pipeline_contract.py`

- [ ] **Step 1: Write the failing test**

```python
from domdown.document.parse import parse_html

def test_document_parse_module_exports_parse_html():
    assert callable(parse_html)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_pipeline_contract.py -v`
Expected: fail with `ModuleNotFoundError`.

- [ ] **Step 3: Write minimal implementation**

```python
from ..document import parse_html

__all__ = ["parse_html"]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_pipeline_contract.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add domdown/document domdown/document.py domdown/stages/parse.py domdown/stages/clean.py tests/test_pipeline_contract.py
git commit -m "refactor(document): split document helpers"
```

### Task 3: Split metadata and frontmatter helpers

**Files:**
- Create: `domdown/metadata/extract.py`
- Create: `domdown/frontmatter/compose.py`
- Create: `domdown/frontmatter/serialize.py`
- Modify: `domdown/metadata.py`
- Modify: `domdown/frontmatter.py`
- Modify: `domdown/stages/metadata.py`
- Modify: `domdown/stages/frontmatter.py`
- Test: `tests/test_html_to_markdown_document.py`

- [ ] **Step 1: Write the failing test**

```python
from domdown.metadata.extract import extract_metadata

def test_metadata_extract_module_exports_extract_metadata():
    assert callable(extract_metadata)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_html_to_markdown_document.py -v`
Expected: fail with `ModuleNotFoundError`.

- [ ] **Step 3: Write minimal implementation**

```python
from ..metadata import extract_metadata

__all__ = ["extract_metadata"]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_html_to_markdown_document.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add domdown/metadata domdown/frontmatter domdown/metadata.py domdown/frontmatter.py domdown/stages/metadata.py domdown/stages/frontmatter.py tests/test_html_to_markdown_document.py
git commit -m "refactor(metadata): split metadata and frontmatter"
```

### Task 4: Split text helpers and constants

**Files:**
- Create: `domdown/text/normalize.py`
- Create: `domdown/text/url.py`
- Create: `domdown/text/frontmatter.py`
- Modify: `domdown/text_utils.py`
- Modify: `domdown/constants.py`
- Test: `tests/test_public_api.py`

- [ ] **Step 1: Write the failing test**

```python
from domdown.text.url import resolve_url

def test_text_url_module_exports_resolve_url():
    assert resolve_url("/x", "https://example.com") == "https://example.com/x"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_public_api.py -v`
Expected: fail with `ModuleNotFoundError`.

- [ ] **Step 3: Write minimal implementation**

```python
from ..text_utils import resolve_url

__all__ = ["resolve_url"]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_public_api.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add domdown/text domdown/text_utils.py domdown/constants.py tests/test_public_api.py
git commit -m "refactor(text): split text helpers"
```

