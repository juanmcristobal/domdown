from __future__ import annotations

import re
from dataclasses import dataclass, field
from urllib.parse import urlsplit

from bs4 import Tag

from .._core import PipelineContext


@dataclass(slots=True, frozen=True)
class DomainAdapterSpec:
    """Declarative rules for a family-specific article adapter."""

    name: str
    site_names: tuple[str, ...] = ()
    host_exact: tuple[str, ...] = ()
    host_suffixes: tuple[str, ...] = ()
    host_selectors: tuple[str, ...] = (
        "link[rel='canonical']",
        "meta[property='og:url']",
        "meta[property='twitter:url']",
    )
    remove_selectors: tuple[str, ...] = ()
    trim_before_first_heading: bool = False
    leading_noise_lines: tuple[str, ...] = ()
    leading_noise_prefixes: tuple[str, ...] = ()
    leading_noise_patterns: tuple[str, ...] = ()
    leading_block_patterns: tuple[str, ...] = ()
    rstrip_noise_lines: tuple[str, ...] = ()
    rstrip_noise_patterns: tuple[str, ...] = ()
    trailing_noise_lines: tuple[str, ...] = ()
    trailing_noise_prefixes: tuple[str, ...] = ()
    trailing_noise_patterns: tuple[str, ...] = ()
    noise_lines: tuple[str, ...] = ()
    noise_patterns: tuple[str, ...] = ()


@dataclass(slots=True)
class DeclarativeDomainAdapter:
    """Generic adapter that applies a declarative domain-specific recipe."""

    spec: DomainAdapterSpec
    name: str = field(init=False)

    def __post_init__(self) -> None:
        """Expose the adapter name expected by the registry."""

        self.name = self.spec.name

    def matches(self, context: PipelineContext) -> bool:
        """Return True when the parsed page matches the configured domain."""

        site_name = _site_name(context.document)
        if site_name and site_name.lower() in {name.lower() for name in self.spec.site_names}:
            return True
        host = _page_host(context.document, self.spec.host_selectors)
        return bool(host and _host_matches(host, self.spec.host_exact, self.spec.host_suffixes))

    def preprocess(self, context: PipelineContext) -> PipelineContext:
        """Remove domain chrome before the generic cleanup stages run."""

        _remove_selectors(context.document, self.spec.remove_selectors)
        return context

    def refine_metadata(self, context: PipelineContext) -> PipelineContext:
        """Keep the generic metadata path unless a domain needs custom handling."""

        return context

    def postprocess(self, context: PipelineContext) -> PipelineContext:
        """Apply generic Markdown cleanup rules configured for the domain."""

        context.markdown = _strip_markdown(
            context.markdown,
            trim_before_first_heading=self.spec.trim_before_first_heading,
            leading_noise_lines=self.spec.leading_noise_lines,
            leading_noise_prefixes=self.spec.leading_noise_prefixes,
            leading_noise_patterns=self.spec.leading_noise_patterns,
            leading_block_patterns=self.spec.leading_block_patterns,
            rstrip_noise_lines=self.spec.rstrip_noise_lines,
            rstrip_noise_patterns=self.spec.rstrip_noise_patterns,
            trailing_noise_lines=self.spec.trailing_noise_lines,
            trailing_noise_prefixes=self.spec.trailing_noise_prefixes,
            trailing_noise_patterns=self.spec.trailing_noise_patterns,
            noise_lines=self.spec.noise_lines,
            noise_patterns=self.spec.noise_patterns,
        )
        return context


def make_domain_adapter(spec: DomainAdapterSpec) -> type[DeclarativeDomainAdapter]:
    """Build a small adapter class from a declarative domain spec."""

    class _DomainAdapter(DeclarativeDomainAdapter):
        def __init__(self) -> None:
            super().__init__(spec=spec)

    _DomainAdapter.__name__ = f"{_class_name(spec.name)}Adapter"
    _DomainAdapter.__qualname__ = _DomainAdapter.__name__
    _DomainAdapter.__doc__ = f"Declarative adapter generated for {spec.name}."
    return _DomainAdapter


def _site_name(document: Tag | None) -> str:
    """Read the Open Graph site name from the current document."""

    if document is None:
        return ""
    return _meta_content(document, "meta[property='og:site_name']")


def _page_host(document: Tag | None, selectors: tuple[str, ...]) -> str:
    """Read the canonical host for the current page."""

    if document is None:
        return ""
    for selector in selectors:
        node = document.select_one(selector)
        if not isinstance(node, Tag):
            continue
        url = str(node.get("href") or node.get("content") or "").strip()
        if not url:
            continue
        try:
            host = urlsplit(url).hostname or ""
        except ValueError:
            continue
        if host:
            host = host.lower()
            return host[4:] if host.startswith("www.") else host
    return ""


def _host_matches(host: str, exact_hosts: tuple[str, ...], host_suffixes: tuple[str, ...]) -> bool:
    """Return True when the current host belongs to the configured family."""

    normalized_exact = {_normalize_host(value) for value in exact_hosts}
    normalized_suffixes = tuple(_normalize_suffix(value) for value in host_suffixes)
    normalized_host = _normalize_host(host)
    if normalized_host in normalized_exact:
        return True
    return any(normalized_host == suffix or normalized_host.endswith(suffix) for suffix in normalized_suffixes)


def _normalize_suffix(value: str) -> str:
    """Normalize a host suffix so callers can pass either form with or without a dot."""

    suffix = _normalize_host(value)
    if suffix and not suffix.startswith("."):
        suffix = f".{suffix}"
    return suffix


def _normalize_host(value: str) -> str:
    """Normalize a host name for family matching."""

    host = value.lower().strip()
    return host[4:] if host.startswith("www.") else host


def _remove_selectors(document: Tag | None, selectors: tuple[str, ...]) -> None:
    """Remove a list of selectors from the parsed document in place."""

    if document is None:
        return
    for selector in selectors:
        for node in document.select(selector):
            if isinstance(node, Tag):
                node.decompose()


def _strip_markdown(
    markdown: str,
    *,
    trim_before_first_heading: bool,
    leading_noise_lines: tuple[str, ...],
    leading_noise_prefixes: tuple[str, ...],
    leading_noise_patterns: tuple[str, ...],
    leading_block_patterns: tuple[str, ...],
    rstrip_noise_lines: tuple[str, ...],
    rstrip_noise_patterns: tuple[str, ...],
    trailing_noise_lines: tuple[str, ...],
    trailing_noise_prefixes: tuple[str, ...],
    trailing_noise_patterns: tuple[str, ...],
    noise_lines: tuple[str, ...],
    noise_patterns: tuple[str, ...],
) -> str:
    """Remove common article chrome from rendered Markdown."""

    text = markdown.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.splitlines()
    if trim_before_first_heading:
        lines = _trim_before_first_heading(lines)
    lines = _trim_leading_boilerplate(lines, leading_noise_lines, leading_noise_prefixes, leading_noise_patterns)
    if leading_block_patterns:
        lines = _trim_leading_blocks(lines, leading_block_patterns)
    if (
        trailing_noise_lines
        or trailing_noise_prefixes
        or trailing_noise_patterns
        or rstrip_noise_lines
        or rstrip_noise_patterns
    ):
        lines = _trim_from_footer(
            lines,
            rstrip_noise_lines,
            rstrip_noise_patterns,
            trailing_noise_lines,
            trailing_noise_prefixes,
            trailing_noise_patterns,
        )
    cleaned: list[str] = []
    in_code_block = False
    normalized_leading_noise = {line.lower() for line in leading_noise_lines}
    normalized_noise_lines = {line.lower() for line in noise_lines}
    compiled_noise_patterns = tuple(re.compile(pattern) for pattern in noise_patterns)
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            cleaned.append(line)
            continue
        if not in_code_block and stripped:
            lowered = stripped.lower()
            if lowered in normalized_leading_noise or lowered in normalized_noise_lines:
                continue
            if any(pattern.search(stripped) for pattern in compiled_noise_patterns):
                continue
        cleaned.append(line)
    return _collapse_blank_lines(cleaned).strip()


def _collapse_blank_lines(lines: list[str]) -> str:
    """Collapse repeated blank lines without altering fenced code blocks."""

    collapsed: list[str] = []
    blank_count = 0
    in_code_block = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            blank_count = 0
            collapsed.append(line)
            continue
        if in_code_block:
            collapsed.append(line)
            continue
        if not stripped:
            blank_count += 1
            if blank_count <= 1:
                collapsed.append("")
            continue
        blank_count = 0
        collapsed.append(line)
    return "\n".join(collapsed)


def _trim_leading_boilerplate(
    lines: list[str],
    leading_noise_lines: tuple[str, ...],
    leading_noise_prefixes: tuple[str, ...],
    leading_noise_patterns: tuple[str, ...],
) -> list[str]:
    """Remove leading metadata-like lines after the title heading."""

    if not lines:
        return lines
    heading_index = next((index for index, line in enumerate(lines) if line.lstrip().startswith("# ")), None)
    if heading_index is None:
        return lines
    index = heading_index + 1
    removed_any = False
    patterns = tuple(re.compile(pattern) for pattern in leading_noise_patterns)
    normalized_lines = {line.lower() for line in leading_noise_lines}
    normalized_prefixes = tuple(prefix.lower() for prefix in leading_noise_prefixes)
    while index < len(lines):
        stripped = lines[index].strip()
        if not stripped:
            removed_any = True
            index += 1
            continue
        if _is_leading_noise_line(stripped, normalized_lines, normalized_prefixes, patterns):
            removed_any = True
            index += 1
            continue
        break
    if removed_any and index < len(lines) and lines[index].strip():
        return lines[: heading_index + 1] + [""] + lines[index:]
    return lines[: heading_index + 1] + lines[index:]


def _trim_leading_blocks(lines: list[str], leading_block_patterns: tuple[str, ...]) -> list[str]:
    """Remove a contiguous leading block after the title when it matches configured patterns."""

    if not lines:
        return lines
    heading_index = next((index for index, line in enumerate(lines) if line.lstrip().startswith("# ")), None)
    if heading_index is None:
        return lines
    index = heading_index + 1
    patterns = tuple(re.compile(pattern) for pattern in leading_block_patterns)
    start = index
    while index < len(lines):
        stripped = lines[index].strip()
        if not stripped:
            index += 1
            continue
        if any(pattern.search(stripped) for pattern in patterns):
            index += 1
            continue
        break
    if index > start:
        if index < len(lines) and lines[index].strip():
            return lines[: heading_index + 1] + [""] + lines[index:]
        return lines[: heading_index + 1] + lines[index:]
    return lines


def _trim_before_first_heading(lines: list[str]) -> list[str]:
    """Remove leading chrome before the article's first Markdown heading."""

    for index, line in enumerate(lines):
        if line.lstrip().startswith("# "):
            return lines[index:]
    return lines


def _trim_from_footer(
    lines: list[str],
    rstrip_noise_lines: tuple[str, ...],
    rstrip_noise_patterns: tuple[str, ...],
    trailing_noise_lines: tuple[str, ...],
    trailing_noise_prefixes: tuple[str, ...],
    trailing_noise_patterns: tuple[str, ...],
) -> list[str]:
    """Remove a trailing footer block and everything after it."""

    normalized_rstrip_lines = {line.lower() for line in rstrip_noise_lines}
    rstrip_patterns = tuple(re.compile(pattern) for pattern in rstrip_noise_patterns)
    normalized_lines = {line.lower() for line in trailing_noise_lines}
    normalized_prefixes = tuple(prefix.lower() for prefix in trailing_noise_prefixes)
    patterns = tuple(re.compile(pattern) for pattern in trailing_noise_patterns)
    for index, line in enumerate(lines):
        stripped = line.strip()
        if _is_trailing_noise_line(stripped, normalized_lines, normalized_prefixes, patterns):
            return _rstrip_noise_lines(
                lines[:index],
                normalized_rstrip_lines | normalized_lines,
                normalized_prefixes,
                rstrip_patterns + patterns,
            )
    return _rstrip_noise_lines(lines, normalized_rstrip_lines, (), rstrip_patterns)


def _rstrip_noise_lines(
    lines: list[str],
    trailing_noise_lines: set[str],
    trailing_noise_prefixes: tuple[str, ...],
    trailing_noise_patterns: tuple[re.Pattern[str], ...],
) -> list[str]:
    """Drop trailing empty and decorative lines from a Markdown block."""

    end = len(lines)
    while end > 0 and _is_noise_line(
        lines[end - 1].strip(),
        trailing_noise_lines,
        trailing_noise_prefixes,
        trailing_noise_patterns,
    ):
        end -= 1
    return lines[:end]


def _is_noise_line(
    line: str,
    trailing_noise_lines: set[str],
    trailing_noise_prefixes: tuple[str, ...],
    trailing_noise_patterns: tuple[re.Pattern[str], ...],
) -> bool:
    """Return True for common decorative separators and configured footer markers."""

    if not line:
        return True
    lowered = line.lower()
    if line in {"·", "--"}:
        return True
    if lowered in trailing_noise_lines:
        return True
    if any(pattern.search(line) for pattern in trailing_noise_patterns):
        return True
    return any(lowered.startswith(prefix.lower()) for prefix in trailing_noise_prefixes)


def _is_trailing_noise_line(
    line: str,
    trailing_noise_lines: set[str],
    trailing_noise_prefixes: tuple[str, ...],
    trailing_noise_patterns: tuple[re.Pattern[str], ...],
) -> bool:
    """Return True when a line marks the start of a footer block."""

    if not line:
        return False
    lowered = line.lower()
    return (
        lowered in trailing_noise_lines
        or any(lowered.startswith(prefix) for prefix in trailing_noise_prefixes)
        or any(pattern.search(line) for pattern in trailing_noise_patterns)
    )


def _is_leading_noise_line(
    line: str,
    leading_noise_lines: set[str],
    leading_noise_prefixes: tuple[str, ...],
    leading_noise_patterns: tuple[re.Pattern[str], ...],
) -> bool:
    """Return True for boilerplate lines that should be removed before article body text."""

    lowered = line.lower()
    if lowered in leading_noise_lines:
        return True
    if any(lowered.startswith(prefix) for prefix in leading_noise_prefixes):
        return True
    if any(pattern.search(line) for pattern in leading_noise_patterns):
        return True
    return False


def _meta_content(document: Tag, selector: str) -> str:
    """Read a meta content value from the parsed document."""

    node = document.select_one(selector)
    if node is None:
        return ""
    return str(node.get("content") or node.get("href") or "").strip()


def _class_name(value: str) -> str:
    """Convert a domain name into a CamelCase class stem."""

    parts = [part for part in re.split(r"[^a-zA-Z0-9]+", value) if part]
    if not parts:
        return "Domain"
    return "".join(part[:1].upper() + part[1:] for part in parts)
