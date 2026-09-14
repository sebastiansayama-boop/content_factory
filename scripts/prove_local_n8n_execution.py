from __future__ import annotations

import json
import os
from pathlib import Path
from uuid import uuid4

from content_factory.n8n_adapter import N8nExecutionAdapter, N8nExecutionConfig
from content_factory.n8n_capability import n8n_execution_capability
from content_factory.runtime import Event, FactoryState, VerificationResult, WorkItem
from content_factory.runtime_store import RuntimeStore


DEFAULT_ENDPOINT = "http://localhost:5678/webhook-test/factory-execution"


def _event(work_item: WorkItem, state: FactoryState, operation: str, actor: str) -> dict[str, object]:
    return Event(
        event_id=str(uuid4()),
        timestamp="proof",
        work_item_id=work_item.work_item_id,
        revision_id=work_item.revision_id,
        state=state.value,
        operation=operation,
        actor=actor,
        data={"operation_id": work_item.operation_id},
    ).__dict__


def main() -> int:
    repository_root = Path(os.getenv("CONTENT_FACTORY_ROOT", ".")).resolve()
    endpoint = os.getenv("N8N_FACTORY_WEBHOOK_URL", DEFAULT_ENDPOINT)
    data_root = repository_root / "data"
    data_root.mkdir(parents=True, exist_ok=True)
    db = data_root / "runtime.sqlite3"

    work_item = WorkItem(
        work_item_id=f"external-proof-n8n-{uuid4().hex[:8]}",
        revision_id="external-proof-r1",
        objective="prove real external execution without a paid provider",
        requested_outcome="Return one short sentence proving the n8n execution boundary is reachable.",
        inputs=("external-proof-input",),
        knowledge_basis=("local-n8n-proof",),
        required_capabilities=("n8n.external-proof",),
        owner="operator",
        acceptance_criteria=("n8n returns a non-empty output bound to this operation",),
        release_requirements=(),
    )

    adapter = N8nExecutionAdapter(N8nExecutionConfig(endpoint=endpoint))
    capability = n8n_execution_capability(
        adapter,
        process_id="external-proof.n8n",
        process_revision_id="v0",
        capability_id="n8n.external-proof",
    )

    with RuntimeStore(db) as store:
        received = _event(work_item, FactoryState.RECEIVED, "submit", "external-proof")
        store.create_work_item(
            work_item_id=work_item.work_item_id,
            operation_id=work_item.operation_id,
            revision_id=work_item.revision_id,
            state=FactoryState.RECEIVED.value,
            updated_at="proof",
            event=received,
        )
        store.transition(
            work_item_id=work_item.work_item_id,
            operation_id=work_item.operation_id,
            revision_id=work_item.revision_id,
            state=FactoryState.ADMITTED.value,
            updated_at="proof",
            event=_event(work_item, FactoryState.ADMITTED, "admit", "external-proof"),
        )

        execution_id = f"n8n-proof-execution-{uuid4().hex[:8]}"
        attempt_id = str(uuid4())
        store.start_attempt(
            attempt_id=attempt_id,
            work_item_id=work_item.work_item_id,
            operation_id=work_item.operation_id,
            execution_id=execution_id,
            attempt_no=1,
            started_at="proof",
        )

        try:
            capability.input_contract(work_item)
            execution = capability.executor(work_item, execution_id)
            if execution.execution_id != execution_id:
                raise AssertionError("execution identity was not preserved")
            if not execution.output_revision_id:
                raise AssertionError("n8n returned no output revision")
            if not str(execution.payload).strip():
                raise AssertionError("n8n returned an empty payload")
            verification = VerificationResult(
                output_revision_id=execution.output_revision_id,
                passed=True,
                evidence_refs=execution.evidence_refs,
                reason="local n8n returned a non-empty revision-bound result",
            )
            if verification.output_revision_id != execution.output_revision_id:
                raise AssertionError("verification is not revision-bound")

            store.finish_attempt(attempt_id, status="SUCCEEDED", completed_at="proof")
            store.save_record(
                work_item.work_item_id,
                "execution",
                {
                    "execution_id": execution.execution_id,
                    "capability_id": execution.capability_id,
                    "output_revision_id": execution.output_revision_id,
                    "payload": execution.payload,
                    "evidence_refs": list(execution.evidence_refs),
                },
            )
            store.transition(
                work_item_id=work_item.work_item_id,
                operation_id=work_item.operation_id,
                revision_id=work_item.revision_id,
                state=FactoryState.PRODUCED.value,
                updated_at="proof",
                event=_event(work_item, FactoryState.PRODUCED, "execute", "external-proof"),
            )
            store.save_record(
                work_item.work_item_id,
                "verification",
                {
                    "output_revision_id": verification.output_revision_id,
                    "passed": verification.passed,
                    "evidence_refs": list(verification.evidence_refs),
                    "reason": verification.reason,
                },
            )
            store.transition(
                work_item_id=work_item.work_item_id,
                operation_id=work_item.operation_id,
                revision_id=work_item.revision_id,
                state=FactoryState.VERIFIED.value,
                updated_at="proof",
                event=_event(work_item, FactoryState.VERIFIED, "verify", "external-proof"),
            )
        except Exception as exc:
            store.finish_attempt(attempt_id, status="FAILED", completed_at="proof", error=str(exc))
            print(f"EXTERNAL PROOF FAILED: {exc}")
            return 1

    with RuntimeStore(db) as reopened:
        items = {x.work_item_id: x for x in reopened.load_work_items()}
        persisted = items[work_item.work_item_id]
        execution = reopened.load_record(work_item.work_item_id, "execution")
        verification = reopened.load_record(work_item.work_item_id, "verification")
        events = reopened.load_events(work_item.work_item_id)
        attempts = reopened.load_attempts(work_item.work_item_id)

    assert persisted.operation_id == work_item.operation_id
    assert persisted.state == FactoryState.VERIFIED.value
    assert execution and execution["output_revision_id"] == verification["output_revision_id"]
    assert verification and verification["passed"] is True
    assert attempts and attempts[0]["status"] == "SUCCEEDED"
    assert any(e["operation"] == "execute" for e in events)
    assert any(e["operation"] == "verify" for e in events)

    print("EXTERNAL PROOF PASSED")
    print(f"work_item_id={work_item.work_item_id}")
    print(f"operation_id={work_item.operation_id}")
    print(f"execution_id={execution['execution_id']}")
    print(f"output_revision_id={execution['output_revision_id']}")
    print(f"evidence_refs={json.dumps(execution['evidence_refs'])}")
    print(f"recovered_state={persisted.state}")
    print(f"recovered_events={len(events)}")
    print("provider=openai:not_used")
    print("execution_substrate=n8n:local")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
