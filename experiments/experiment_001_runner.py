from __future__ import annotations

import json
import os
from pathlib import Path

from content_factory.github_publisher import GitHubContentsConfig, GitHubContentsPublisher
from content_factory.runtime import (
    AcceptanceDecision,
    Capability,
    ExecutionResult,
    FactoryRuntime,
    VerificationResult,
    WorkItem,
)

MEMORY_ID = "MEM-2026-09-13-001-r1"
POLICY = "correlation/provider identity is not evidence of duplicate-safe retry; reconcile before retry"
TARGET_PATH = "experiments/external-effect/experiment-001-result.md"


def main() -> None:
    owner = os.environ["GITHUB_REPOSITORY"].split("/", 1)[0]
    repo = os.environ["GITHUB_REPOSITORY"].split("/", 1)[1]
    branch = os.environ.get("GITHUB_REF_NAME", "experiment/001-real-github-publisher")

    publisher = GitHubContentsPublisher(
        GitHubContentsConfig(owner=owner, repo=repo, path=TARGET_PATH, branch=branch)
    )
    content = "\n".join(
        [
            "# Experiment-001 external result",
            "",
            f"memory: {MEMORY_ID}",
            f"decision: {POLICY}",
            "execution: one GitHub Contents mutation followed by reconciliation",
            "purpose: bounded real external-effect learning-loop case",
        ]
    )

    item = WorkItem(
        work_item_id="experiment-001-github-publication",
        revision_id="experiment-001-r1",
        objective="Test whether reusable memory changes external-effect execution control",
        requested_outcome="one bounded GitHub publication with post-effect reconciliation",
        inputs=("MEM-2026-09-13-001-r1",),
        knowledge_basis=(MEMORY_ID,),
        required_capabilities=("github-publish",),
        owner="experiment-001",
        acceptance_criteria=("publication target is the dedicated experiment file",),
        release_requirements=("experiment-001 release authority",),
        constraints=("exactly one mutation attempt", "no automatic retry"),
    )

    runtime = FactoryRuntime(publisher=publisher)
    runtime.register_capability(
        Capability(
            capability_id="github-publish",
            input_contract=lambda _: None,
            executor=lambda _, execution_id: ExecutionResult(
                execution_id=execution_id,
                capability_id="github-publish",
                output_revision_id="experiment-001-output-r1",
                payload=content,
                evidence_refs=(f"memory:{MEMORY_ID}", f"policy:{POLICY}"),
            ),
        )
    )
    runtime.submit(item, actor="experiment-001")
    publication = runtime.run(
        item,
        verification=lambda _, execution: VerificationResult(
            execution.output_revision_id,
            True,
            evidence_refs=("precondition:dedicated-target",),
        ),
        acceptance=lambda _, verified: AcceptanceDecision(
            verified.output_revision_id,
            True,
            "experiment-001-approver",
            reason="bounded real external-effect experiment",
        ),
        release_authority="experiment-001-release-authority",
        actor="experiment-001",
    )
    if publication is None:
        raise RuntimeError("FactoryRuntime did not produce a publication")

    # Memory-informed delta: identity is not treated as duplicate-safe proof;
    # perform reconciliation before any future retry decision.
    reconciliation = publisher.reconcile()
    if not reconciliation.get("exists"):
        raise RuntimeError("reconciliation did not observe the published target")
    if reconciliation.get("content_sha256") is None:
        raise RuntimeError("reconciliation did not provide target content evidence")

    result = {
        "experiment": "EXPERIMENT-001",
        "memory_id": MEMORY_ID,
        "decision_delta": "reconcile after external mutation before considering retry",
        "execution_delta": "one mutation + one read-only reconciliation; no retry",
        "publication_id": publication.publication_id,
        "target": publication.target,
        "evidence_refs": list(publication.evidence_refs),
        "reconciliation": reconciliation,
        "provenance": [event.__dict__ for event in runtime.provenance(item.work_item_id)],
        "memory_evaluation": "UNRESOLVED_FOR_DUPLICATE_SAFETY; SUPPORTED_FOR_RECONCILIATION-FIRST CONTROL",
    }
    Path("experiment-001-result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
