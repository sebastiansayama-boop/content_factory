from __future__ import annotations

import os

from content_factory.openai_capability import openai_text_capability
from content_factory.runtime import VerificationResult, WorkItem


def main() -> int:
    if not os.getenv("OPENAI_API_KEY"):
        print("OPENAI_API_KEY is not set; no external call was attempted.")
        return 2

    capability = openai_text_capability()
    item = WorkItem(
        work_item_id="phase2-proof",
        revision_id="spec-phase2-r1",
        objective="prove real provider execution",
        requested_outcome="Return exactly one short sentence confirming that the Content Factory provider boundary is reachable.",
        inputs=(),
        knowledge_basis=("phase2-proof-request",),
        required_capabilities=("openai.text.generate",),
        owner="operator",
        acceptance_criteria=("provider response contains text",),
        release_requirements=(),
    )

    capability.input_contract(item)
    execution = capability.executor(item, "phase2-execution-proof")
    verification = VerificationResult(
        output_revision_id=execution.output_revision_id,
        passed=bool(str(execution.payload).strip()),
        evidence_refs=execution.evidence_refs,
        reason="real provider returned non-empty text",
    )
    if not verification.passed:
        print("PHASE 2 PROOF FAILED: verification rejected provider output.")
        return 1

    print("PHASE 2 PROOF PASSED")
    print(f"execution_id={execution.execution_id}")
    print(f"capability_id={execution.capability_id}")
    print(f"output_revision_id={execution.output_revision_id}")
    print(f"verification_revision_id={verification.output_revision_id}")
    print(f"evidence_refs={verification.evidence_refs}")
    print("payload=")
    print(execution.payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
