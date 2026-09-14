import pytest

from content_factory import ContentDemand


def valid_demand(**overrides):
    value = {
        "demand_id": "demand-001",
        "revision_id": "demand-001-r1",
        "strategic_intent_ref": "intent-001",
        "opportunity_or_problem_ref": "opportunity-001",
        "audience_context_ref": "audience-001",
        "requested_outcome": "Create an evidence-backed short-form content package.",
        "content_job_or_product_intent": "Explain the opportunity clearly for the target audience.",
        "knowledge_basis_refs": ("knowledge-001",),
        "evidence_refs": ("evidence-001",),
        "decision_ref": "decision-001",
        "decision_status": "AUTHORIZED",
        "authority_ref": "authority-001",
        "constraints": ("No unsupported claims.",),
        "acceptance_criteria": ("All claims trace to supplied evidence.",),
        "release_requirements": ("Human release approval required.",),
        "success_signals": ("Qualified audience engagement",),
    }
    value.update(overrides)
    return value


def test_authorized_demand_round_trips_and_maps_to_work_item():
    demand = ContentDemand.from_mapping(valid_demand())
    assert demand.to_mapping()["decision_status"] == "AUTHORIZED"

    work_item = demand.to_work_item(
        work_item_id="work-001",
        owner="factory",
        required_capabilities=("text-generation",),
    )
    assert work_item.objective == demand.content_job_or_product_intent
    assert work_item.dependencies == (demand.decision_ref,)
    assert demand.evidence_refs[0] in work_item.inputs


@pytest.mark.parametrize(
    "field, value",
    [
        ("decision_status", "CANDIDATE"),
        ("evidence_refs", ()),
        ("knowledge_basis_refs", ()),
        ("acceptance_criteria", ()),
    ],
)
def test_factory_rejects_unauthorized_or_incomplete_demand(field, value):
    with pytest.raises(ValueError):
        ContentDemand.from_mapping(valid_demand(**{field: value}))


def test_missing_required_field_is_rejected():
    value = valid_demand()
    del value["decision_ref"]
    with pytest.raises(ValueError, match="missing ContentDemand fields"):
        ContentDemand.from_mapping(value)
