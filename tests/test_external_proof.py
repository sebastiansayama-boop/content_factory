from content_factory.runtime import ExecutionResult, WorkItem
from scripts.prove_real_provider_durable import PROOF_MARKER, _verify_real_output


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
