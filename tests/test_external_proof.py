import json
from pathlib import Path

from content_factory.runtime import ExecutionResult, WorkItem
from scripts.prove_real_provider_durable import PROOF_MARKER, _verify_real_output


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
N8N_WORKFLOW = REPOSITORY_ROOT / "integrations" / "n8n" / "factory_execution_proof.workflow.json"


def _item() -> WorkItem:
    return WorkItem(
        work_item_id="proof-test",
        revision_id="spec-r1",
        objective="proof",
        requested_outcome=f"return {PROOF_MARKER}",
        inputs=(),
        knowledge_basis=(),
        required_capabilities=("openai.text.generate",),
        owner="test",
        acceptance_criteria=("marker is present",),
        release_requirements=(),
    )


def test_external_proof_verifier_binds_exact_output_revision():
    item = _item()
    execution = ExecutionResult(
        execution_id="exec-proof",
        capability_id="openai.text.generate",
        output_revision_id="openai-response:resp-proof",
        payload=f"One sentence: {PROOF_MARKER}",
        evidence_refs=("resp-proof",),
    )

    result = _verify_real_output(item, execution)

    assert result.passed is True
    assert result.output_revision_id == execution.output_revision_id
    assert result.evidence_refs == execution.evidence_refs


def test_external_proof_verifier_rejects_missing_marker():
    item = _item()
    execution = ExecutionResult(
        execution_id="exec-proof",
        capability_id="openai.text.generate",
        output_revision_id="openai-response:resp-proof",
        payload="provider returned text but not the required marker",
        evidence_refs=("resp-proof",),
    )

    result = _verify_real_output(item, execution)

    assert result.passed is False
    assert result.output_revision_id == execution.output_revision_id


def test_local_n8n_proof_workflow_matches_factory_contract():
    workflow = json.loads(N8N_WORKFLOW.read_text(encoding="utf-8"))
    nodes = {node["name"]: node for node in workflow["nodes"]}

    webhook = nodes["Factory Webhook"]
    builder = nodes["Build Factory Execution Result"]

    assert webhook["type"] == "n8n-nodes-base.webhook"
    assert webhook["typeVersion"] == 2.1
    assert webhook["parameters"]["httpMethod"] == "POST"
    assert webhook["parameters"]["path"] == "factory-execution"
    assert webhook["parameters"]["responseMode"] == "lastNode"

    assert builder["type"] == "n8n-nodes-base.code"
    assert builder["typeVersion"] == 2

    code = builder["parameters"]["jsCode"]
    for required in (
        "n8n.execution.v0",
        "operation_id",
        "work_item_id",
        "revision_id",
        "runtime_execution_id",
        "SUCCEEDED",
        "output_revision_id",
        "evidence_refs",
    ):
        assert required in code

    connection = workflow["connections"]["Factory Webhook"]["main"][0][0]
    assert connection["node"] == "Build Factory Execution Result"
