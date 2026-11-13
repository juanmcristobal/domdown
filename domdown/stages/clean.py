"""Stage interface for structural cleanup."""

from __future__ import annotations

from dataclasses import dataclass
from copy import deepcopy

from bs4 import BeautifulSoup, Tag

from .._constants import DEFAULT_REMOVE_SELECTORS, JS_SHELL_PHRASES, SKIP_TAGS
from .._core import PipelineContext
from .._document import choose_root, clean_root
from .._document.clean import _promote_image_fallbacks
from .._core import CriteriaError, ExtractionCriteria, ExtractionTrace


@dataclass(slots=True)
class CleanStage:
    """Remove noise and normalize the document before preservation."""

    name: str = "clean"

    def run(self, context: PipelineContext) -> PipelineContext:
        """Choose the main content root and strip irrelevant nodes."""

        if context.document is None:
            return context
        criteria = context.extraction_criteria
        if criteria is not None:
            return self._apply_criteria(context, criteria)
        present_before = _present_ids(context.document, context.node_ids)
        root = choose_root(context.document, context.options.prefer_article_body)
        strategy = "choose_root"
        preserve_chrome = False
        if _root_is_empty(root):
            fallback = _fallback_root(context.document, root)
            if fallback is not None:
                root.decompose()
                root = fallback
                strategy = "empty-root-fallback"
        elif _looks_like_js_shell(root) and _body_has_more_content(context.document, root):
            body = context.document.body
            if body is not None:
                root.decompose()
                root = body
                preserve_chrome = True
                strategy = "javascript-shell-body-fallback"
        root = clean_root(
            root,
            context.options.remove_selectors or DEFAULT_REMOVE_SELECTORS,
            SKIP_TAGS,
            preserve_chrome=preserve_chrome,
        )
        context.document = root
        context.selected_root_id = context.node_ids.get(id(root))
        context.selected_strategy = strategy
        context.cleanup_removed_node_ids = tuple(sorted(present_before - _present_ids(root, context.node_ids)))
        context.cleaned_html = str(root)
        return context

    def _apply_criteria(self, context: PipelineContext, criteria: ExtractionCriteria) -> PipelineContext:
        document = context.document
        recorded_replay = criteria.has_recorded_replay and criteria.root_node_id is not None
        if recorded_replay:
            root = _find_node_by_id(document, context.node_ids, criteria.root_node_id)
            if root is None:
                raise CriteriaError(f"Criteria document root {criteria.root_node_id} does not exist in this HTML")
            _promote_image_fallbacks(root)
            retained = set(criteria.retained_node_ids)
            for node in list(root.find_all(True)):
                node_id = context.node_ids.get(id(node))
                if node_id is not None and node_id not in retained:
                    node.decompose()
            root_id = context.node_ids.get(id(root))
            if root_id not in retained:
                raise CriteriaError("Criteria retained_node_ids do not include the selected root")
        else:
            matches = []
            for selector in criteria.include:
                matches.extend(document.select(selector))
            matches = _unique_outermost(matches)
            if not matches:
                raise CriteriaError("Explicit include selectors matched no elements")
            if len(matches) == 1:
                root = matches[0]
            else:
                soup = BeautifulSoup("<div data-domdown-criteria-root='true'></div>", "lxml")
                root = soup.select_one("[data-domdown-criteria-root]")
                for match in matches:
                    root.append(deepcopy(match))
            decisions = []
            root_was_excluded = False
            for selector in criteria.exclude:
                excluded = ([root] if _matches(root, selector) else []) + list(root.select(selector))
                decisions.append({"action": "exclude", "selector": selector, "matches": len(excluded)})
                if root in excluded:
                    root_was_excluded = True
                    break
                for node in excluded:
                    node.decompose()
            if root_was_excluded:
                soup = BeautifulSoup("", "lxml")
                root = soup.new_tag("div")
            for selector in criteria.unwrap:
                if root_was_excluded:
                    break
                unwrap_nodes = ([root] if _matches(root, selector) else []) + list(root.select(selector))
                decisions.append({"action": "unwrap", "selector": selector, "matches": len(unwrap_nodes)})
                for node in unwrap_nodes:
                    if node is root:
                        raise CriteriaError("unwrap cannot target the selected include root")
                    node.unwrap()
            context.extraction_trace = ExtractionTrace(
                selected_root=_css_path(root),
                decisions=tuple(decisions),
            )
        root = clean_root(
            root,
            (),
            SKIP_TAGS,
            apply_extraction_heuristics=recorded_replay,
        )
        context.selected_root_id = context.node_ids.get(id(root))
        context.document = root
        context.cleaned_html = str(root)
        return context


def _find_node_by_id(document, node_ids, wanted):
    if node_ids.get(id(document)) == wanted:
        return document
    for node in document.find_all(True):
        if node_ids.get(id(node)) == wanted:
            return node
    return None


def _present_ids(document, node_ids):
    nodes = [document, *document.find_all(True)]
    return {node_ids[id(node)] for node in nodes if id(node) in node_ids}


def _matches(node, selector):
    try:
        return bool(node in node.select(selector))
    except Exception as exc:
        raise CriteriaError(f"Invalid CSS selector {selector!r}: {exc}") from exc


def _unique_outermost(nodes):
    result = []
    seen = set()
    for node in nodes:
        if id(node) in seen:
            continue
        if any(parent in result for parent in node.parents):
            continue
        result.append(node)
        seen.add(id(node))
    return sorted(result, key=lambda node: len(list(node.previous_elements)))


def _css_path(node):
    parts = []
    current = node
    while isinstance(current, Tag) and current.name not in {"[document]", "html"}:
        if current.get("id"):
            parts.append(f"#{current.get('id')}")
            break
        classes = [str(value) for value in current.get("class", []) if str(value)]
        part = current.name + "".join(f".{value}" for value in classes[:2])
        siblings = [item for item in current.parent.find_all(current.name, recursive=False)] if isinstance(current.parent, Tag) else []
        if len(siblings) > 1:
            part += f":nth-of-type({siblings.index(current) + 1})"
        parts.append(part)
        current = current.parent
    return " > ".join(reversed(parts))


def _root_is_empty(root) -> bool:
    """Detect a selected shell that contains no visible text to render."""

    return not root.get_text(" ", strip=True)


def _fallback_root(document, current: Tag) -> Tag | None:
    """Return the first non-empty document-level fallback root."""

    candidates = (document.body, document.select_one("main"), document.html)
    for candidate in candidates:
        if isinstance(candidate, Tag) and candidate is not current and candidate.get_text(" ", strip=True):
            return candidate
    return None


def _looks_like_js_shell(root) -> bool:
    """Detect portal shells that only render placeholder text without JavaScript."""

    text = root.get_text(" ", strip=True).lower()
    return any(phrase in text for phrase in JS_SHELL_PHRASES)


def _body_has_more_content(document, root) -> bool:
    """Require a real body fallback only when the body is materially richer than the shell."""

    body = document.body
    if body is None:
        return False
    body_words = len(body.get_text(" ", strip=True).split())
    root_words = len(root.get_text(" ", strip=True).split())
    return body_words >= max(root_words + 8, 20)
