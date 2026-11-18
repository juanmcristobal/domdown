from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Sequence

from .._core import (
    CriteriaError,
    DomdownOptions,
    ExtractionCriteria,
    ExtractionPlan,
    ExtractionTrace,
    HtmlToMarkdownResult,
    PipelineContext,
)
from .._version import DOMDOWN_VERSION
from ..adapters import AdapterRegistry, ArticleAdapter, build_default_registry
from ..stages.base import PipelineStage
from ..stages.clean import CleanStage
from ..stages.frontmatter import FrontmatterStage
from ..stages.markdown import MarkdownStage
from ..stages.metadata import MetadataStage
from ..stages.parse import ParseStage
from ..stages.postprocess import PostProcessStage
from ..stages.preserve import PreserveStage
from ..stages.prepare import PrepareDocumentStage
from ..site_criteria import criteria_for_document


@dataclass(slots=True)
class HtmlToMarkdownPipeline:
    """Orchestrate the ordered stages that transform HTML into Markdown."""

    options: DomdownOptions | None = None
    stages: Sequence[PipelineStage] = field(default_factory=tuple)
    adapters: Sequence[ArticleAdapter] = field(default_factory=tuple)
    adapter_registry: AdapterRegistry = field(init=False)

    def __post_init__(self) -> None:
        """Populate the default stage chain when none is supplied."""

        self.adapter_registry = build_default_registry(self.adapters)
        if not self.stages:
            self.stages = (
                ParseStage(),
                PrepareDocumentStage(),
                MetadataStage(),
                CleanStage(),
                PreserveStage(),
                MarkdownStage(),
                PostProcessStage(),
                FrontmatterStage(),
            )

    def run(
        self,
        html: str,
        *,
        criteria: ExtractionCriteria | dict | str | None = None,
    ) -> HtmlToMarkdownResult:
        """Run the configured pipeline over raw HTML and return the result."""

        extraction_criteria = ExtractionCriteria.from_json(criteria) if criteria is not None else None
        criteria_source = "explicit" if extraction_criteria is not None else "discover"
        document_sha256 = hashlib.sha256(html.encode("utf-8")).hexdigest()
        if (
            extraction_criteria is not None
            and extraction_criteria.has_recorded_replay
            and (
                extraction_criteria.document_sha256 != document_sha256
                or extraction_criteria.domdown_version != DOMDOWN_VERSION
            )
        ):
            raise CriteriaError("Recorded extraction criteria require the same HTML and DomDown version")
        context = PipelineContext(
            html=html,
            options=self.options or DomdownOptions(),
            extraction_criteria=extraction_criteria,
            extraction_plan=ExtractionPlan(extraction_criteria) if extraction_criteria is not None else None,
        )
        if extraction_criteria is not None and not extraction_criteria.replayable:
            context.warnings.extend(
                f"Criteria replay is not guaranteed: {limitation}" for limitation in extraction_criteria.limitations
            )
        for stage in self.stages:
            context = stage.run(context)
            stage_name = getattr(stage, "name", "")
            if stage_name == "prepare":
                context.node_refs = list(context.document.find_all(True))
                context.node_ids = {id(node): index for index, node in enumerate(context.node_refs, start=1)}
                context.node_descriptors = {
                    context.node_ids[id(node)]: {
                        "tag": node.name,
                        "id": str(node.get("id")) if node.get("id") is not None else None,
                        "classes": [str(value) for value in (node.get("class") or ())],
                    }
                    for node in context.node_refs
                }
                context.matched_adapters = self.adapter_registry.matching(context)
                for adapter in context.matched_adapters:
                    limitation_hook = getattr(adapter, "criteria_limitations", None)
                    if limitation_hook is not None:
                        context.reproducibility_limitations.extend(limitation_hook(context))
                site_criteria = criteria_for_document(context.document)
                if extraction_criteria is None:
                    if site_criteria is not None:
                        extraction_criteria = site_criteria
                        context.extraction_criteria = site_criteria
                        context.extraction_plan = ExtractionPlan(site_criteria)
                        context.criteria_source = "site"
                        criteria_source = "site"
                        context.site_criteria_scope = True
                elif site_criteria is not None and _same_selector_operations(extraction_criteria, site_criteria):
                    context.site_criteria_scope = True
                    if extraction_criteria.has_recorded_replay:
                        context.criteria_source = "site"
                if extraction_criteria is None:
                    context = self.adapter_registry.preprocess(context)
                elif extraction_criteria.has_recorded_replay:
                    context = self.adapter_registry.preprocess_for_criteria(context)
                    _apply_recorded_adapter_removals(context, extraction_criteria.adapter_removed_node_ids)
            elif stage_name == "metadata":
                context = self.adapter_registry.refine_metadata(context)
            elif stage_name == "clean" and (
                extraction_criteria is None
                or (not extraction_criteria.has_recorded_replay and context.selector_apply_shared_cleanup)
            ):
                context = self.adapter_registry.post_clean(context)
            elif stage_name == "postprocess" and (
                extraction_criteria is None
                or extraction_criteria.has_recorded_replay
                or context.selector_apply_shared_cleanup
            ):
                context = self.adapter_registry.postprocess(context)
        mode = (
            "discover"
            if extraction_criteria is None
            else "exact_replay" if extraction_criteria.has_recorded_replay else "selector_apply"
        )
        criteria_source = (
            context.criteria_source
            if context.criteria_source == "site"
            else "discover"
            if extraction_criteria is None or extraction_criteria.has_recorded_replay
            else "explicit"
        )
        after_metrics = context.extraction_metrics.setdefault("after", {})
        after_metrics["words"] = len(context.markdown.split())
        if after_metrics["words"] < 10:
            if mode == "selector_apply":
                include_decisions = context.extraction_trace.decisions if context.extraction_trace else ()
                selection_result = next(
                    (decision for decision in include_decisions if decision.get("action") == "include-result"),
                    {},
                )
                matches = selection_result.get("matches", 0)
                if matches:
                    context.warnings.append(
                        f"Possible empty shell: include matched {matches} elements but produced "
                        f"{after_metrics['words']} words"
                    )
            elif len(html) >= 512:
                context.warnings.append(
                    f"Possible empty shell: {len(html)} HTML characters produced {after_metrics['words']} words"
                )
        before_words = context.extraction_metrics.get("before", {}).get("words", 0)
        context.extraction_metrics["word_retention"] = (
            round(after_metrics["words"] / before_words, 3) if before_words else None
        )
        if extraction_criteria is None:
            selected_root = _node_selector(context.document)
            retained_ids = (
                tuple(
                    sorted(
                        {context.node_ids.get(id(context.document), context.selected_root_id)}
                        | {
                            context.node_ids[id(node)]
                            for node in context.document.find_all(True)
                            if id(node) in context.node_ids
                        }
                    )
                )
                if context.document is not None and id(context.document) in context.node_ids
                else ()
            )
            adapters = tuple({"name": adapter.name} for adapter in (context.matched_adapters or ()))
            adapter_trace = tuple(context.adapter_trace)
            limitations = tuple(context.reproducibility_limitations)
            criteria_result = ExtractionCriteria(
                include=(selected_root,) if selected_root else (),
                adapters=adapters,
                document_sha256=document_sha256,
                domdown_version=DOMDOWN_VERSION,
                adapter_removed_node_ids=tuple(
                    sorted(
                        {
                            node_id
                            for operation in context.adapter_trace
                            if operation.get("hook") == "preprocess"
                            for node_id in operation.get("removed_node_ids", ())
                        }
                    )
                ),
                limitations=limitations,
                root_node_id=context.selected_root_id,
                retained_node_ids=retained_ids,
                replayable=not limitations,
                generated=True,
            ).with_replay_key()
            trace_result = ExtractionTrace(
                selected_root=selected_root,
                adapters=adapters,
                decisions=(
                    {
                        "action": "select-root",
                        "method": context.selected_strategy or "adapter-special",
                        "selector": selected_root,
                    },
                    {"action": "clean-stage-discard", "node_ids": list(context.cleanup_removed_node_ids)},
                    *adapter_trace,
                ),
                node_references=_trace_node_references(
                    context.node_descriptors,
                    context.cleanup_removed_node_ids,
                    adapter_trace,
                    context.selected_root_id,
                ),
                replayable=criteria_result.replayable,
                limitations=limitations,
                mode=mode,
                criteria_source=criteria_source,
                content_metrics=context.extraction_metrics,
                warnings=tuple(context.warnings),
            )
        elif context.criteria_source == "site" and not extraction_criteria.has_recorded_replay:
            retained_ids = tuple(
                sorted(
                    {context.node_ids.get(id(context.document), context.selected_root_id)}
                    | {
                        context.node_ids[id(node)]
                        for node in context.document.find_all(True)
                        if id(node) in context.node_ids
                    }
                )
            )
            criteria_result = ExtractionCriteria(
                include=extraction_criteria.include,
                exclude=extraction_criteria.exclude,
                unwrap=extraction_criteria.unwrap,
                drop_text=extraction_criteria.drop_text,
                document_sha256=document_sha256,
                domdown_version=DOMDOWN_VERSION,
                root_node_id=context.selected_root_id,
                retained_node_ids=retained_ids,
                generated=True,
                limitations=tuple(context.reproducibility_limitations),
                replayable=not context.reproducibility_limitations,
            ).with_replay_key()
            limitations = tuple(dict.fromkeys(context.reproducibility_limitations))
            trace_result = ExtractionTrace(
                selected_root=context.extraction_trace.selected_root if context.extraction_trace else None,
                adapters=tuple({"name": adapter.name} for adapter in (context.matched_adapters or ())),
                decisions=(
                    *((context.extraction_trace.decisions) if context.extraction_trace else ()),
                    *context.adapter_trace,
                ),
                replayable=not limitations,
                limitations=limitations,
                mode=mode,
                criteria_source=criteria_source,
                content_metrics=context.extraction_metrics,
                warnings=tuple(context.warnings),
            )
        else:
            criteria_result = extraction_criteria
            limitations = tuple(dict.fromkeys((*extraction_criteria.limitations, *context.reproducibility_limitations)))
            decisions = (
                {
                    "action": "apply-criteria",
                    "include": list(extraction_criteria.include),
                    "include_fallback": list(extraction_criteria.include_fallback),
                    "min_words": extraction_criteria.min_words,
                    "exclude": list(extraction_criteria.exclude),
                    "unwrap": list(extraction_criteria.unwrap),
                    "drop_text": list(extraction_criteria.drop_text),
                    "shared_cleanup": extraction_criteria.shared_cleanup,
                },
            )
            if context.extraction_trace is not None:
                decisions += context.extraction_trace.decisions
            decisions += tuple(context.adapter_trace)
            trace_result = ExtractionTrace(
                selected_root=(
                    context.extraction_trace.selected_root
                    if context.extraction_trace is not None and context.extraction_trace.selected_root
                    else _node_selector(context.document)
                ),
                adapters=tuple(
                    {"name": adapter.name, "override": True} for adapter in (context.matched_adapters or ())
                ),
                decisions=decisions,
                replayable=extraction_criteria.replayable and not limitations,
                limitations=limitations,
                mode=mode,
                criteria_source=criteria_source,
                content_metrics=context.extraction_metrics,
                warnings=tuple(context.warnings),
            )
        return HtmlToMarkdownResult(
            markdown=context.markdown,
            cleaned_html=context.cleaned_html,
            metadata=context.metadata,
            frontmatter=context.frontmatter,
            document=context.rendered_document,
            warnings=tuple(context.warnings),
            criteria=criteria_result,
            trace=trace_result,
        )


def _node_selector(node) -> str | None:
    if node is None:
        return None
    if node.get("id"):
        identifier = str(node.get("id"))
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]*", identifier):
            return f"#{identifier}"
    classes = node.get("class") or ()
    if classes and all(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]*", str(value)) for value in classes[:2]):
        return node.name + "".join(f".{value}" for value in classes[:2])
    if node.name in {"article", "main", "body"}:
        return node.name
    return None


def _trace_node_references(descriptors, cleanup_removed, adapter_trace, root_id):
    referenced = set(cleanup_removed)
    if root_id is not None:
        referenced.add(root_id)
    for item in adapter_trace:
        referenced.update(item.get("removed_node_ids", ()))
    return tuple(
        {"node_id": node_id, **descriptors[node_id]} for node_id in sorted(referenced) if node_id in descriptors
    )


def _apply_recorded_adapter_removals(context: PipelineContext, node_ids: tuple[int, ...]) -> None:
    if context.document is None or not node_ids:
        return
    wanted = set(node_ids)
    for node in reversed(context.node_refs):
        if context.node_ids.get(id(node)) in wanted and node.parent is not None:
            node.decompose()


def _same_selector_operations(left: ExtractionCriteria, right: ExtractionCriteria) -> bool:
    """Compare the portable CSS operations independently from replay metadata."""

    return (
        left.include == right.include
        and left.exclude == right.exclude
        and left.unwrap == right.unwrap
        and not left.include_fallback
        and left.drop_text == right.drop_text
        and left.shared_cleanup == "auto"
    )
