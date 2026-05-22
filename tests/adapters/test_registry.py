from __future__ import annotations

from dataclasses import dataclass

from domdown._core import DomdownOptions, PipelineContext
from domdown.adapters import AdapterRegistry, build_default_registry
from domdown._pipeline import HtmlToMarkdownPipeline


@dataclass(slots=True)
class FakeAdapter:
    """Small adapter used to verify registry ordering and pipeline hooks."""

    name: str
    should_match: bool = True

    def matches(self, context: PipelineContext) -> bool:
        """Return the configured match result and leave the context untouched."""

        return self.should_match

    def preprocess(self, context: PipelineContext) -> PipelineContext:
        """Record that preprocessing ran."""

        context.warnings.append(f"pre:{self.name}")
        return context

    def postprocess(self, context: PipelineContext) -> PipelineContext:
        """Record that postprocessing ran."""

        context.warnings.append(f"post:{self.name}")
        return context


def test_adapter_registry_filters_and_applies_matching_adapters_in_order() -> None:
    """Registry should only run adapters that match the current document."""

    first = FakeAdapter("first", should_match=True)
    second = FakeAdapter("second", should_match=False)
    third = FakeAdapter("third", should_match=True)
    registry = AdapterRegistry(adapters=(first, second, third))
    context = PipelineContext(html="<html></html>", options=DomdownOptions())

    processed = registry.preprocess(context)
    processed = registry.postprocess(processed)

    assert processed.warnings == ["pre:first", "pre:third", "post:first", "post:third"]


def test_pipeline_runs_adapter_hooks_without_changing_output_when_adapter_is_observational() -> None:
    """A no-op adapter should not change the rendered markdown."""

    pipeline = HtmlToMarkdownPipeline(
        adapters=(FakeAdapter("observer"),),
    )

    result = pipeline.run("<html><body><article><p>Hello world.</p></article></body></html>")

    assert result.markdown == "Hello world."
    assert result.warnings == ("pre:observer", "post:observer")


def test_build_default_registry_returns_an_empty_registry_when_no_adapters_are_supplied() -> None:
    """The default registry should be empty and harmless."""

    registry = build_default_registry()

    assert registry.adapters == ()
