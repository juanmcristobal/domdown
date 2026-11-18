from dataclasses import replace

import pytest

from domdown import CriteriaError, ExtractionCriteria


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"include": ("",)}, "include must be a list"),
        ({"drop_text": ("",)}, "drop_text must be a list"),
        ({"min_words": True}, "min_words must be a non-negative integer"),
        ({"shared_cleanup": "sometimes"}, "shared_cleanup must be"),
        ({"include": (".main",), "include_fallback": ("article",)}, "mutually exclusive"),
        ({"drop_text": ("[",)}, "Invalid drop_text regex"),
    ],
)
def test_criteria_reject_invalid_values(kwargs, message) -> None:
    with pytest.raises(CriteriaError, match=message):
        ExtractionCriteria(**kwargs)


def test_criteria_serializes_optional_replay_and_fallback_fields() -> None:
    criteria = ExtractionCriteria(
        include_fallback=("article", ".content"),
        min_words=12,
        drop_text=(r"^Advertisement$",),
        shared_cleanup="force",
        adapters=({"name": "test", "data": {"version": 1}},),
        document_sha256="abc123",
        domdown_version="1.2.3",
        root_node_id=4,
        retained_node_ids=(4, 5),
        adapter_removed_node_ids=(6,),
        generated=True,
        replayable=False,
        limitations=("external assets",),
    ).with_replay_key()

    payload = criteria.to_dict()
    restored = ExtractionCriteria.from_json(criteria.to_json())

    assert payload["include_fallback"] == ["article", ".content"]
    assert payload["min_words"] == 12
    assert payload["shared_cleanup"] == "force"
    assert payload["root_node_id"] == 4
    assert payload["retained_node_ids"] == [4, 5]
    assert payload["adapter_removed_node_ids"] == [6]
    assert restored == criteria
    assert criteria.has_recorded_replay
    assert not replace(criteria, replay_key="bad-key").has_recorded_replay


def test_criteria_omits_default_optional_json_fields() -> None:
    assert ExtractionCriteria().to_dict() == {
        "schema_version": 1,
        "include": [],
        "exclude": [],
        "unwrap": [],
        "replayable": True,
    }
    assert ExtractionCriteria(min_words=42).to_dict()["min_words"] == 42
    assert ExtractionCriteria(generated=True).to_dict()["generated"] is True


@pytest.mark.parametrize(
    ("value", "message"),
    [
        ("{", "Invalid extraction criteria JSON"),
        ({}, "schema_version is required"),
        ({"schema_version": 1, "unknown": True}, "Unknown extraction criteria fields"),
        ({"schema_version": 1, "include": ".main"}, "include must be a JSON array"),
    ],
)
def test_criteria_from_json_reports_invalid_documents(value, message) -> None:
    with pytest.raises(CriteriaError, match=message):
        ExtractionCriteria.from_json(value)


def test_criteria_from_json_returns_an_existing_criteria_unchanged() -> None:
    criteria = ExtractionCriteria(include=("article",))
    assert ExtractionCriteria.from_json(criteria) is criteria
