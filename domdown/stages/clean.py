"""Stage interface for structural cleanup."""

from __future__ import annotations

import re
from copy import deepcopy
from dataclasses import dataclass

import soupsieve
from bs4 import BeautifulSoup, Tag

from .._constants import DEFAULT_REMOVE_SELECTORS, JS_SHELL_PHRASES, SKIP_TAGS
from .._core import CriteriaError, ExtractionCriteria, ExtractionTrace, PipelineContext
from .._core.selectors import normalize_selector
from .._document import choose_root, clean_root
from .._document.clean import _promote_image_fallbacks


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
        context.extraction_metrics = {"before": _content_metrics(root)}
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
        context.extraction_metrics["after"] = _content_metrics(root, include_words=False)
        _add_retention_ratio(context.extraction_metrics)
        context.cleaned_html = str(root)
        return context

    def _apply_criteria(self, context: PipelineContext, criteria: ExtractionCriteria) -> PipelineContext:
        document = context.document
        recorded_replay = criteria.has_recorded_replay and criteria.root_node_id is not None
        same_content_scope = False
        if recorded_replay:
            root = _find_node_by_id(document, context.node_ids, criteria.root_node_id)
            if root is None:
                raise CriteriaError(f"Criteria document root {criteria.root_node_id} does not exist in this HTML")
            context.extraction_metrics = {"before": _content_metrics(root)}
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
            synthetic_root = False
            decisions = []
            if criteria.include_fallback:
                fallback_candidates = []
                for selector in criteria.include_fallback:
                    selected = _unique_outermost(list(document.select(normalize_selector(selector))))
                    match_count = len(selected)
                    selected, duplicates_removed = _dedupe_duplicate_content(selected)
                    words = _aggregate_metrics(selected).get("words", 0)
                    decisions.append(
                        {
                            "action": "include-fallback",
                            "selector": selector,
                            "matches": match_count,
                            "duplicates_removed": duplicates_removed,
                            "words": words,
                            "status": "matched" if selected else "no-matches",
                        }
                    )
                    fallback_candidates.append((selected, words, len(decisions) - 1))
                    if selected and words >= criteria.min_words:
                        matches = selected
                        decisions[-1]["status"] = "selected"
                        break
                    if selected:
                        decisions[-1]["status"] = "below-threshold"
                if not matches and fallback_candidates:
                    matches, _, best_index = max(fallback_candidates, key=lambda candidate: candidate[1])
                    if matches:
                        decisions[best_index]["status"] = "selected-best-below-threshold"
            else:
                for selector in criteria.include:
                    selected = list(document.select(normalize_selector(selector)))
                    decisions.append(
                        {
                            "action": "include",
                            "selector": selector,
                            "matches": len(selected),
                            "status": "matched" if selected else "no-matches",
                        }
                    )
                    matches.extend(selected)
                matches = _unique_outermost(matches)
            matches, duplicates_removed = _dedupe_duplicate_content(matches)
            if duplicates_removed:
                decisions.append(
                    {
                        "action": "dedupe-content",
                        "nodes_removed": duplicates_removed,
                        "status": "applied",
                    }
                )
            if not matches:
                if len(context.html) >= 512:
                    raise CriteriaError(
                        "Explicit include selectors matched no elements in a "
                        f"{len(context.html)}-character HTML document; possible empty shell or stale selector"
                    )
                raise CriteriaError("Explicit include selectors matched no elements")
            context.extraction_metrics = {"before": _aggregate_metrics(matches)}
            decisions.append({"action": "include-result", "matches": len(matches)})
            if len(matches) == 1:
                root = matches[0]
            else:
                synthetic_root = True
                soup = BeautifulSoup("<div data-domdown-criteria-root='true'></div>", "lxml")
                root = soup.select_one("[data-domdown-criteria-root]")
                for match in matches:
                    root.append(deepcopy(match))
            same_content_scope = not synthetic_root and (
                criteria.shared_cleanup == "force"
                or (
                    criteria.shared_cleanup == "auto"
                    and _looks_like_article_scope(root, context.extraction_metrics["before"])
                )
            )
            context.selector_apply_shared_cleanup = same_content_scope
            root_was_excluded = False
            for selector in criteria.exclude:
                excluded = ([] if synthetic_root or not _matches(root, selector) else [root]) + list(
                    root.select(normalize_selector(selector))
                )
                if root in excluded:
                    decisions.append(
                        {
                            "action": "exclude",
                            "selector": selector,
                            "matches": len(excluded),
                            "nodes_removed": _count_tags(root),
                            "status": "root-excluded",
                        }
                    )
                else:
                    outermost = _unique_outermost(excluded)
                    removed = sum(_count_tags(node) for node in outermost)
                    decisions.append(
                        {
                            "action": "exclude",
                            "selector": selector,
                            "matches": len(excluded),
                            "nodes_removed": removed,
                            "status": "applied" if excluded else "no-matches",
                        }
                    )
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
                unwrap_nodes = ([] if synthetic_root or not _matches(root, selector) else [root]) + list(
                    root.select(normalize_selector(selector))
                )
                decisions.append(
                    {
                        "action": "unwrap",
                        "selector": selector,
                        "matches": len(unwrap_nodes),
                        "nodes_unwrapped": len(unwrap_nodes),
                        "status": "applied" if unwrap_nodes else "no-matches",
                    }
                )
                for node in unwrap_nodes:
                    if node is root:
                        raise CriteriaError("unwrap cannot target the selected include root")
                    node.unwrap()
            context.extraction_trace = ExtractionTrace(
                selected_root=_css_path(root),
                decisions=tuple(decisions),
            )
            # Adapter extraction filters run only after explicit selection so
            # callers can still select page chrome or content outside the article.
            context.document = root
            for adapter in context.matched_adapters or ():
                if not same_content_scope:
                    break
                before = _present_ids(root, context.node_ids)
                context = adapter.preprocess(context)
                root = context.document
                removed = sorted(before - _present_ids(root, context.node_ids))
                context.adapter_trace.append({"name": adapter.name, "hook": "preprocess", "removed_node_ids": removed})
        root = clean_root(
            root,
            (
                ()
                if recorded_replay or ((criteria.include or criteria.include_fallback) and not same_content_scope)
                else context.options.remove_selectors or DEFAULT_REMOVE_SELECTORS
            ),
            SKIP_TAGS,
            apply_extraction_heuristics=recorded_replay or same_content_scope,
            drop_text_patterns=criteria.drop_text if not recorded_replay else (),
        )
        context.selected_root_id = context.node_ids.get(id(root))
        context.document = root
        context.cleaned_html = str(root)
        context.extraction_metrics["after"] = _content_metrics(root, include_words=False)
        _add_retention_ratio(context.extraction_metrics)
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
        return soupsieve.match(normalize_selector(selector), node)
    except Exception as exc:
        raise CriteriaError(f"Invalid CSS selector {selector!r}: {exc}") from exc


def _unique_outermost(nodes):
    unique = list({id(node): node for node in nodes}.values())
    matched_ids = {id(node) for node in unique}
    outermost = [node for node in unique if not any(id(parent) in matched_ids for parent in node.parents)]
    top = outermost[0] if outermost else None
    while isinstance(top, Tag) and isinstance(top.parent, Tag):
        top = top.parent
    document_order = (
        {id(node): index for index, node in enumerate(top.descendants) if id(node) in matched_ids}
        if isinstance(top, Tag)
        else {}
    )
    if isinstance(top, Tag) and id(top) in matched_ids:
        document_order[id(top)] = -1
    return sorted(outermost, key=lambda node: document_order.get(id(node), -1))


def _dedupe_duplicate_content(nodes: list[Tag]) -> tuple[list[Tag], int]:
    """Collapse separately matched roots whose substantial text is near-identical."""

    if len(nodes) < 2:
        return nodes, 0
    retained: list[tuple[Tag, tuple[str, ...], set[tuple[str, ...]]]] = []
    removed = 0
    for node in nodes:
        words = tuple(re.findall(r"[\w']+", node.get_text(" ", strip=True).casefold()))
        if len(words) < 40:
            retained.append((node, words, set()))
            continue
        shingles = {words[index : index + 5] for index in range(len(words) - 4)}
        duplicate = False
        index = 0
        while index < len(retained):
            previous, previous_words, previous_shingles = retained[index]
            if len(previous_words) < 40:
                index += 1
                continue
            smaller_shingles, larger_shingles = (
                (shingles, previous_shingles) if len(words) <= len(previous_words) else (previous_shingles, shingles)
            )
            if len(smaller_shingles) < 8:
                index += 1
                continue
            overlap = len(smaller_shingles & larger_shingles) / len(smaller_shingles) if smaller_shingles else 0
            if overlap < 0.9:
                index += 1
                continue
            if len(previous_words) >= len(words):
                duplicate = True
                break
            retained.pop(index)
            removed += 1
        if duplicate:
            removed += 1
        else:
            retained.append((node, words, shingles))
    return [node for node, _, _ in retained], removed


def _count_tags(node: Tag) -> int:
    return 1 + len(node.find_all(True))


def _looks_like_article_scope(node: Tag, metrics: dict[str, int]) -> bool:
    """Enable shared automatic cleanup for article-shaped selected content."""

    tag_name = node.name.lower()
    if tag_name in {"article", "main"}:
        return True
    return (
        tag_name not in {"body", "html"}
        and metrics.get("words", 0) >= 50
        and metrics.get("headings", 0) >= 1
        and metrics.get("paragraphs", 0) >= 2
    )


_METRIC_TEXT_TYPES = tuple(Tag.MAIN_CONTENT_STRING_TYPES)
_METRIC_TAGS = {
    **{f"h{level}": "headings" for level in range(1, 7)},
    "p": "paragraphs",
    "a": "links",
    "ul": "lists",
    "ol": "lists",
    "dl": "lists",
    "table": "tables",
    "pre": "code_blocks",
}


def _empty_metrics() -> dict[str, int]:
    return {"words": 0, "headings": 0, "paragraphs": 0, "links": 0, "lists": 0, "tables": 0, "code_blocks": 0}


def _accumulate_content_metrics(node: Tag, metrics: dict[str, int], *, include_words: bool = True) -> None:
    """Count rendered text and semantic tags in one DOM traversal."""

    for descendant in node.descendants:
        if isinstance(descendant, Tag):
            metric = _METRIC_TAGS.get(descendant.name.lower())
            if metric is not None:
                metrics[metric] += 1
        elif include_words and type(descendant) in _METRIC_TEXT_TYPES:
            metrics["words"] += len(str(descendant).strip().split())


def _content_metrics(node: Tag, *, include_words: bool = True) -> dict[str, int]:
    metrics = _empty_metrics()
    _accumulate_content_metrics(node, metrics, include_words=include_words)
    return {key: value for key, value in metrics.items() if value}


def _aggregate_metrics(nodes: list[Tag]) -> dict[str, int]:
    metrics = _empty_metrics()
    for node in nodes:
        _accumulate_content_metrics(node, metrics)
    return {key: value for key, value in metrics.items() if value}


def _add_retention_ratio(metrics: dict) -> None:
    before = metrics.get("before", {}).get("words", 0)
    after = metrics.get("after", {}).get("words", 0)
    metrics["word_retention"] = round(after / before, 3) if before else None


def _css_path(node):
    parts = []
    current = node
    while isinstance(current, Tag) and current.name not in {"[document]", "html"}:
        if current.get("id"):
            parts.append(f"#{current.get('id')}")
            break
        classes = [str(value) for value in current.get("class", []) if str(value)]
        part = current.name + "".join(f".{value}" for value in classes[:2])
        siblings = (
            [item for item in current.parent.find_all(current.name, recursive=False)]
            if isinstance(current.parent, Tag)
            else []
        )
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
