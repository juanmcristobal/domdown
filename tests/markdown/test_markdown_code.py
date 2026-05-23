from __future__ import annotations

from bs4 import BeautifulSoup

from domdown._core import DomdownOptions
from domdown.markdown.code import render_code_block


def test_render_code_block_outputs_a_fenced_block_with_language() -> None:
    """Code blocks should render as fenced Markdown with a detected language hint."""

    soup = BeautifulSoup('<pre class="language-python"><code>print("hi")</code></pre>', "lxml")

    assert render_code_block(soup.pre, DomdownOptions()) == '```python\nprint("hi")\n```'


def test_render_code_block_uses_a_longer_fence_when_the_code_contains_backticks() -> None:
    """The fence delimiter should expand when the code body already contains backticks."""

    soup = BeautifulSoup("<pre><code>```\ncode\n```</code></pre>", "lxml")

    assert render_code_block(soup.pre, DomdownOptions()).startswith("````")


def test_render_code_block_preserves_multiline_source_with_inline_spans() -> None:
    """Tokenized code blocks should keep their original line structure."""

    soup = BeautifulSoup(
        """
        <pre><code>
          <span>#!/usr/bin/env node</span>
          <span>async function demo() {</span>
          <span>  return 1;</span>
          <span>}</span>
        </code></pre>
        """,
        "lxml",
    )

    assert render_code_block(soup.pre, DomdownOptions()) == "```\n#!/usr/bin/env node\nasync function demo() {\n  return 1;\n}\n```"
