from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from uuid import uuid4

from content_factory.artifacts import ArtifactStore
from content_factory.openai_capability import openai_text_capability
from content_factory.runtime import FactoryRuntime, FactoryState, VerificationResult, WorkItem
from content_factory.runtime_store import RuntimeStore

PROOF_MARKER = "CONTENT_FACTORY_EXTERNAL_PROOF_OK"


def _verify_real_output(item: WorkItem, execution) -> VerificationResult:
    payload = str(execution.payload).strip()
    passed = bool(payload) and PROOF_MARKER in payload
    return VerificationResult(
        output_revision_id=execution.output_revision_id,
        passed=passed,
        evidence_refs=execution.evidence_refs,
        reason="real provider output contains the required proof marker" if passed else "proof marker missing from real provider output",
    )


def _proof_report(item: WorkItem, runtime: FactoryRuntime) -> dict[str, object]:
    execution = runtime.executions[item.work_item_id]
    verification = runtime.verifications[item.work_item_id]
    payload = str(execution.payload)
    return {
        "proof": "real_provider_execution",
        "work_item_id": item.work_item_id,
        "revision_id": item.revision_id,
        "operation_id": item.operation_id,
        "state": runtime.states[item.work_item_id].value,
        "execution_id": execution.execution_id,
        "capability_id": execution.capability_id,
        "output_revision_id": execution.output_revision_id,
        "provider_response_id": execution.evidence_refs[0] if execution.evidence_refs else None,
        "verification_passed": verification.passed,
        "verification_revision_id": verification.output_revision_id,
        "payload_sha256": hashlib.sha256(payload.encode("utf-8")).hexdigest(),
        "provenance_event_count": len(runtime.provenance(item.work_item_id)),
    }


def main() -> int:
    if not os.getenv("OPENAI_API_KEY"):
        print("OPENAI_API_KEY is not set; no external call was attempted.")
        return 2

    root = Path(os.getenv("CONTENT_FACTORY_ROOT", ".")).resolve()
    data_root = root / "data"
    data_root.mkdir(parents=True, exist_ok=True)
    report_dir = data_root / "external_proof"
    report_dir.mkdir(parents=True, exist_ok=True)
    db_path = data_root / "runtime.sqlite3"

    work_item_id = f"external-proof-{uuid4().hex[:10]}"
    item = WorkItem(
        work_item_id=work_item_id,
        revision_id="external-proof-r1",
        objective="prove a real provider execution through the factory runtime",
        requested_outcome=(
            f"Return exactly one short sentence containing the marker {PROOF_MARKER}. "
            "Do not add explanations."
        ),
        inputs=("external-proof-request",),
        knowledge_basis=("external-proof-request",),
        required_capabilities=("openai.text.generate",),
        owner="operator",
        acceptance_criteria=("real provider output contains the proof marker",),
        release_requirements=(),
        success_signals=(PROOF_MARKER,),
    )

    with RuntimeStore(db_path) as store:
        runtime = FactoryRuntime(
            publisher=None,
            artifact_store=ArtifactStore(root),
            runtime_store=store,
        )
        runtime.register_capability(openai_text_capability())
        runtime.submit(item, actor="external-proof")

        capability = runtime.capabilities[item.required_capabilities[0]]
        runtime._transition(item, FactoryState.ADMITTED, "admit", "external-proof")
        execution = runtime._execute_with_attempts(item, capability)
        if execution is None:
            raise RuntimeError("external proof produced no execution result")
        runtime.executions[item.work_item_id] = execution
        runtime._save_execution(item, execution)
        runtime._transition(item, FactoryState.PRODUCED, "execute", "external-proof", execution_id=execution.execution_id)

        verification = _verify_real_output(item, execution)
        runtime.verifications[item.work_item_id] = verification
        runtime._save_verification(item, verification)
        if not verification.passed:
            runtime._transition(item, FactoryState.FAILED, "verify", "external-proof", reason=verification.reason)
            print("EXTERNAL PROOF FAILED: real provider output did not satisfy verification.")
            return 1
        runtime._transition(item, FactoryState.VERIFIED, "verify", "external-proof")
        runtime._materialize(item)

        report = _proof_report(item, runtime)
        report_path = report_dir / f"{work_item_id}.json"
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    with RuntimeStore(db_path) as store:
        recovered = FactoryRuntime(runtime_store=store)
        if recovered.states.get(work_item_id) != FactoryState.VERIFIED:
            raise RuntimeError("durable recovery did not reconstruct VERIFIED state")
        if work_item_id not in recovered.executions:
            raise RuntimeError("durable recovery did not reconstruct execution projection")
        if work_item_id not in recovered.verifications:
            raise RuntimeError("durable recovery did not reconstruct verification projection")
        recovered_verification = recovered.verifications[work_item_id]
        if not recovered_verification.passed:
            raise RuntimeError("durable recovery reconstructed a failed verification")

        print("EXTERNAL PROOF PASSED")
        print(f"work_item_id={work_item_id}")
        print(f"operation_id={recovered.operation_ids[work_item_id]}")
        print(f"execution_id={recovered.executions[work_item_id].execution_id}")
        print(f"output_revision_id={recovered.executions[work_item_id].output_revision_id}")
        print(f"provider_response_id={recovered.executions[work_item_id].evidence_refs[0]}")
        print(f"verification_revision_id={recovered_verification.output_revision_id}")
        print(f"events={len(recovered.provenance(work_item_id))}")
        print(f"report={report_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
