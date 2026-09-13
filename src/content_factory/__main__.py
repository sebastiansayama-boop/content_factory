from __future__ import annotations

import os
from pathlib import Path

from .artifacts import ArtifactStore
from .runtime import (
    AcceptanceDecision,
    Capability,
    ExecutionResult,
    FactoryRuntime,
    PublicationResult,
    VerificationResult,
    WorkItem,
)


class DemoPublisher:
    def publish(self, work_item, execution):
        return PublicationResult(
            publication_id="demo-publication",
            output_revision_id=execution.output_revision_id,
            target="demo://simulated",
            externally_observable=False,
            evidence_refs=("demo-simulation",),
        )


def main() -> None:
    repository_root = Path(os.getenv("CONTENT_FACTORY_ROOT", "."))
    runtime = FactoryRuntime(
        publisher=DemoPublisher(),
        artifact_store=ArtifactStore(repository_root),
    )
    runtime.register_capability(
        Capability(
            capability_id="write",
            input_contract=lambda item: None,
            executor=lambda item, execution_id: ExecutionResult(
                execution_id=execution_id,
                capability_id="write",
                output_revision_id="asset-r1",
                payload="demo content",
            ),
        )
    )
    item = WorkItem(
        work_item_id="demo-work-item",
        revision_id="spec-r1",
        objective="exercise runtime",
        requested_outcome="one simulated delivery",
        inputs=("demo-input",),
        knowledge_basis=("demo-knowledge",),
        required_capabilities=("write",),
        owner="demo",
        acceptance_criteria=("passes demo verification",),
        release_requirements=("demo authority",),
    )
    runtime.submit(item)
    publication = runtime.run(
        item,
        verification=lambda _, execution: VerificationResult(execution.output_revision_id, True),
        acceptance=lambda _, verified: AcceptanceDecision(verified.output_revision_id, True, "demo-approver"),
        release_authority="demo-publisher",
    )
    print(runtime.states[item.work_item_id].value)
    print(publication.publication_id if publication else "FAILED")


if __name__ == "__main__":
    main()
