from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ArtifactStore:
    """Explicit filesystem sink for durable runtime evidence.

    The store writes only runtime observations/projections. It never promotes
    execution output to knowledge, strategy, acceptance, or publication truth.
    """

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)

    def record(self, work_item: Any, runtime: Any) -> None:
        work_id = work_item.work_item_id
        self._write("03_working_context", work_id, {
            "type": "working_context_projection",
            "work_item": self._work_item(work_item),
            "state": runtime.states[work_id].value,
        })

        if work_id in runtime.executions:
            execution = runtime.executions[work_id]
            self._write("06_production", work_id, {
                "type": "production_execution",
                "work_item_id": work_id,
                "revision_id": execution.output_revision_id,
                "execution_id": execution.execution_id,
                "capability_id": execution.capability_id,
                "evidence_refs": list(execution.evidence_refs),
            })

        if work_id in runtime.verifications:
            verification = runtime.verifications[work_id]
            self._write("07_verification", work_id, {
                "type": "verification_result",
                "work_item_id": work_id,
                "revision_id": verification.output_revision_id,
                "passed": verification.passed,
                "reason": verification.reason,
                "evidence_refs": list(verification.evidence_refs),
            })

        if work_id in runtime.acceptances:
            acceptance = runtime.acceptances[work_id]
            self._write("05_decision", work_id, {
                "type": "acceptance_decision",
                "work_item_id": work_id,
                "revision_id": acceptance.output_revision_id,
                "accepted": acceptance.accepted,
                "authority": acceptance.authority,
                "reason": acceptance.reason,
            })

        if work_id in runtime.publications:
            publication = runtime.publications[work_id]
            self._write("08_effects_feedback", work_id, {
                "type": "external_effect_observation",
                "work_item_id": work_id,
                "revision_id": publication.output_revision_id,
                "publication_id": publication.publication_id,
                "target": publication.target,
                "externally_observable": publication.externally_observable,
                "evidence_refs": list(publication.evidence_refs),
            })
            self._write("01_observation", work_id, {
                "type": "runtime_observation",
                "work_item_id": work_id,
                "revision_id": publication.output_revision_id,
                "state": runtime.states[work_id].value,
                "publication_id": publication.publication_id,
                "evidence_refs": list(publication.evidence_refs),
            })

        self._write("10_records", work_id, {
            "type": "runtime_case_record",
            "work_item_id": work_id,
            "revision_id": work_item.revision_id,
            "state": runtime.states[work_id].value,
            "events": [
                {
                    "event_id": event.event_id,
                    "timestamp": event.timestamp,
                    "revision_id": event.revision_id,
                    "state": event.state,
                    "operation": event.operation,
                    "actor": event.actor,
                    "data": event.data,
                }
                for event in runtime.provenance(work_id)
            ],
        })

    def _write(self, zone: str, work_id: str, payload: dict[str, Any]) -> None:
        directory = self.root / zone
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{work_id}.json"
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    @staticmethod
    def _work_item(item: Any) -> dict[str, Any]:
        return {
            "work_item_id": item.work_item_id,
            "revision_id": item.revision_id,
            "objective": item.objective,
            "requested_outcome": item.requested_outcome,
            "inputs": list(item.inputs),
            "knowledge_basis": list(item.knowledge_basis),
            "required_capabilities": list(item.required_capabilities),
            "owner": item.owner,
            "acceptance_criteria": list(item.acceptance_criteria),
            "release_requirements": list(item.release_requirements),
            "constraints": list(item.constraints),
            "dependencies": list(item.dependencies),
            "success_signals": list(item.success_signals),
        }
