from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class DomdownOptions:
    """Configuration for HTML parsing, cleanup, and output shaping.

    `base_url` resolves relative URLs during parsing. `frontmatter_opts`
    provides per-key fallback values when rendering frontmatter.
    """

    base_url: str | None = None
    frontmatter_opts: dict[str, object] = field(default_factory=dict)
    created: str | None = None
    extract_metadata: bool = True
    emit_frontmatter: bool = True
    prefer_article_body: bool = True
    author_priority: str = "visible"
    frontmatter_tags: tuple[str, ...] = ()
    preserve_images: bool = True
    preserve_tables: bool = True
    preserve_code_blocks: bool = True
    strip_hidden: bool = True
    remove_selectors: tuple[str, ...] = ()
    keep_selectors: tuple[str, ...] = ()
    unwrap_selectors: tuple[str, ...] = ()
