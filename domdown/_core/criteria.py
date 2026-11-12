"""Serializable extraction criteria and diagnostics."""

from __future__ import annotations

import json
import hashlib
from dataclasses import dataclass
from typing import Any

from bs4 import BeautifulSoup


class CriteriaError(ValueError):
    """Raised when extraction criteria cannot be validated or applied."""


@dataclass(frozen=True, slots=True)
class ExtractionCriteria:
    """JSON-compatible extraction rules. Document paths are replay-only references."""

    include: tuple[str, ...] = ()
    exclude: tuple[str, ...] = ()
    unwrap: tuple[str, ...] = ()
    schema_version: int = 1
    adapters: tuple[dict[str, Any], ...] = ()
    document_sha256: str | None = None
    domdown_version: str | None = None
    root_node_id: int | None = None
    retained_node_ids: tuple[int, ...] = ()
    adapter_removed_node_ids: tuple[int, ...] = ()
    generated: bool = False
    replay_key: str | None = None
    replayable: bool = True
    limitations: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if type(self.schema_version) is not int or self.schema_version != 1:
            raise CriteriaError(f"Unsupported extraction criteria schema_version: {self.schema_version}")
        for name in ("include", "exclude", "unwrap"):
            values = getattr(self, name)
            if not isinstance(values, (tuple, list)) or any(not isinstance(value, str) or not value.strip() for value in values):
                raise CriteriaError(f"{name} must be a list of non-empty CSS selectors")
        for selector in (*self.include, *self.exclude, *self.unwrap):
            try:
                BeautifulSoup("<html><body></body></html>", "lxml").select(selector)
            except Exception as exc:
                raise CriteriaError(f"Invalid CSS selector {selector!r}: {exc}") from exc

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "schema_version": self.schema_version,
            "include": list(self.include),
            "exclude": list(self.exclude),
            "unwrap": list(self.unwrap),
        }
        if self.adapters:
            result["adapters"] = list(self.adapters)
        if self.document_sha256:
            result["document_sha256"] = self.document_sha256
        if self.domdown_version:
            result["domdown_version"] = self.domdown_version
        if self.root_node_id is not None:
            result["root_node_id"] = self.root_node_id
            result["retained_node_ids"] = list(self.retained_node_ids)
        if self.adapter_removed_node_ids:
            result["adapter_removed_node_ids"] = list(self.adapter_removed_node_ids)
        if self.generated:
            result["generated"] = True
        if self.replay_key:
            result["replay_key"] = self.replay_key
        result["replayable"] = self.replayable
        if self.limitations:
            result["limitations"] = list(self.limitations)
        return result

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True)

    @property
    def has_recorded_replay(self) -> bool:
        if not self.generated or not self.replay_key:
            return False
        payload = self._replay_payload()
        return hashlib.sha256(payload.encode("utf-8")).hexdigest() == self.replay_key

    def with_replay_key(self) -> "ExtractionCriteria":
        from dataclasses import replace
        payload = self._replay_payload()
        return replace(self, replay_key=hashlib.sha256(payload.encode("utf-8")).hexdigest())

    def _replay_payload(self) -> str:
        return json.dumps(
            {
                "include": list(self.include),
                "exclude": list(self.exclude),
                "unwrap": list(self.unwrap),
                "root_node_id": self.root_node_id,
                "retained_node_ids": list(self.retained_node_ids),
                "adapter_removed_node_ids": list(self.adapter_removed_node_ids),
                "adapters": list(self.adapters),
                "document_sha256": self.document_sha256,
                "domdown_version": self.domdown_version,
            },
            sort_keys=True,
            separators=(",", ":"),
        )

    @classmethod
    def from_json(cls, value: str | dict[str, Any] | "ExtractionCriteria") -> "ExtractionCriteria":
        if isinstance(value, cls):
            return value
        try:
            data = json.loads(value) if isinstance(value, str) else dict(value)
        except (ValueError, TypeError) as exc:
            raise CriteriaError(f"Invalid extraction criteria JSON: {exc}") from exc
        allowed = {"schema_version", "include", "exclude", "unwrap", "adapters", "document_sha256", "domdown_version", "root_node_id", "retained_node_ids", "adapter_removed_node_ids", "generated", "replay_key", "replayable", "limitations"}
        if "schema_version" not in data:
            raise CriteriaError("schema_version is required")
        unknown = set(data) - allowed
        if unknown:
            raise CriteriaError(f"Unknown extraction criteria fields: {', '.join(sorted(unknown))}")
        for name in ("include", "exclude", "unwrap", "adapters", "retained_node_ids", "adapter_removed_node_ids", "limitations"):
            if name in data and not isinstance(data[name], list):
                raise CriteriaError(f"{name} must be a JSON array")
        return cls(
            schema_version=data.get("schema_version", 1),
            include=tuple(data.get("include", ())),
            exclude=tuple(data.get("exclude", ())),
            unwrap=tuple(data.get("unwrap", ())),
            adapters=tuple(data.get("adapters", ())),
            document_sha256=data.get("document_sha256"),
            domdown_version=data.get("domdown_version"),
            root_node_id=data.get("root_node_id"),
            retained_node_ids=tuple(data.get("retained_node_ids", ())),
            adapter_removed_node_ids=tuple(data.get("adapter_removed_node_ids", ())),
            generated=data.get("generated", False),
            replay_key=data.get("replay_key"),
            replayable=data.get("replayable", True),
            limitations=tuple(data.get("limitations", ())),
        )


@dataclass(frozen=True, slots=True)
class ExtractionTrace:
    """Compact extraction diagnostics; it intentionally contains no full HTML."""

    selected_root: str | None = None
    adapters: tuple[dict[str, Any], ...] = ()
    decisions: tuple[dict[str, Any], ...] = ()
    node_references: tuple[dict[str, Any], ...] = ()
    replayable: bool = True
    limitations: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "selected_root": self.selected_root,
            "adapters": list(self.adapters),
            "decisions": list(self.decisions),
            "node_references": list(self.node_references),
            "reproducibility": {"replayable": self.replayable, "limitations": list(self.limitations)},
        }


@dataclass(slots=True)
class ExtractionPlan:
    """Internal ordered DOM operations derived from public criteria."""

    criteria: ExtractionCriteria
    explicit: bool = True
