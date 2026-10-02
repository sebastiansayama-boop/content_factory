from __future__ import annotations

from copy import deepcopy

import pytest

from scripts.test_impact import load_model, order_gates, plan_for_files, validate_model


@pytest.fixture()
def model():
    value = load_model()
    validate_model(value)
    return value


def test_model_is_acyclic_and_self_consistent(model):
    validate_model(model)


def test_knowledge_content_change_reaches_required_downstream_gates(model):
    plan = plan_for_files(model, ["src/content_factory/knowledge_content.py"])
    assert plan["unknown_files"] == []
    assert plan["fallback_used"] is False
    assert {"T01","T02","T03","T04","T05","T08","T11","T13","T14","T15"}.issubset(set(plan["closure"]))
    assert "T06" not in plan["closure"]
    assert "T12" not in plan["closure"]
    assert plan["ordered_gates"][0] == "T01"


def test_distribution_change_only_reaches_telegram_downstream(model):
    plan = plan_for_files(model, ["src/content_factory/distribution.py"])
    assert plan["unknown_files"] == []
    assert plan["fallback_used"] is False
    assert set(plan["closure"]) == {"T01","T02","T13","T14","T15"}
    assert "T06" not in plan["closure"]
    assert "T08" not in plan["closure"]
    assert plan["ordered_gates"] == ["T01","T02","T13","T14","T15"]


def test_runtime_change_does_not_pull_provider_or_telegram(model):
    plan = plan_for_files(model, ["src/content_factory/runtime.py"])
    assert set(plan["closure"]) == {"T01","T02","T08","T09","T10"}
    assert "T06" not in plan["closure"]
    assert "T11" not in plan["closure"]
    assert "T14" not in plan["closure"]


def test_workflow_change_maps_to_its_direct_gate(model):
    plan = plan_for_files(model, [".github/workflows/ollama-live-main.yml"])
    assert plan["fallback_used"] is False
    assert set(plan["closure"]) == {"T01","T02","T06","T07","T08","T09","T10","T11","T13","T14","T15"}


def test_docs_change_has_no_gates(model):
    plan = plan_for_files(model, ["docs/example.md", "README.md"])
    assert plan["unknown_files"] == []
    assert plan["fallback_used"] is False
    assert plan["closure"] == []
    assert plan["ordered_gates"] == []


def test_unknown_file_fails_closed_to_r0_r1(model):
    plan = plan_for_files(model, ["src/content_factory/new_unknown_module.py"])
    assert plan["fallback_used"] is True
    assert plan["unknown_files"] == ["src/content_factory/new_unknown_module.py"]
    for gate_id, gate in model["gates"].items():
        if gate["risk"] in {"R0","R1"}:
            assert gate_id in plan["closure"]


def test_multiple_changes_are_union_plus_downstream(model):
    plan = plan_for_files(
        model,
        ["src/content_factory/knowledge_content.py", "src/content_factory/distribution.py"],
    )
    assert {"T03","T04","T05","T08","T11","T13","T14","T15"}.issubset(set(plan["closure"]))


def test_order_respects_selected_dependencies(model):
    selected = {"T01","T02","T03","T04","T05","T08"}
    ordered = order_gates(model, selected)
    positions = {gate_id:index for index, gate_id in enumerate(ordered)}
    for gate_id in selected:
        for dep in model["gates"][gate_id]["depends_on"]:
            if dep in selected:
                assert positions[dep] < positions[gate_id]


def test_model_validation_rejects_cycle(model):
    broken = deepcopy(model)
    broken["gates"]["T01"]["depends_on"] = ["T02"]
    with pytest.raises(ValueError, match="cycle"):
        validate_model(broken)
