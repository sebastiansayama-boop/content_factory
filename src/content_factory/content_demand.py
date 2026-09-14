from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


AUTHORIZED_STATUS = "AUTHORIZED"


@dataclass(frozen=True)
class ContentDemand:
    """Normalized intake contract from an upstream discovery/decision system.

    This is a receiving-boundary contract. It does not claim ownership of the
    upstream discovery lifecycle or decision authority.
    """

    demand_id: str
    revision_id: str
    strategic_intent_ref: str
    opportunity_or_problem_ref: str
    audience_context_ref: str
    requested_outcome: str
    content_job_or_product_intent: str
    knowledge_basis_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    decision_ref: str
    decision_status: str
    authority_ref: str
    constraints: tuple[str, ...]
    acceptance_criteria: tuple[str, ...]
    release_requirements: tuple[str, ...]
    success_signals: tuple[str, ...]

    def __post_init__(self) -> None:
        for name in (
            "demand_id",
            "revision_id",
            "strategic_intent_ref",
            "opportunity_or_problem_ref",
            "audience_context_ref",
            "requested_outcome",
            "content_job_or_product_intent",
            "decision_ref",
            "decision_status",
            "authority_ref",
        ):
            if not getattr(self, name).strip():
                raise ValueError(f"{name} must not be empty")
        if self.decision_status != AUTHORIZED_STATUS:
            raise ValueError("ContentDemand must be AUTHORIZED before factory intake")
        if not self.evidence_refs:
            raise ValueError("ContentDemand requires at least one evidence reference")
        if not self.knowledge_basis_refs:
            raise ValueError("ContentDemand requires at least one knowledge basis reference")
        if not self.acceptance_criteria:
            raise ValueError("ContentDemand requires acceptance criteria")

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "ContentDemand":
        fields = {
            "demand_id": value.get("demand_id"),
            "revision_id": value.get("revision_id"),
            "strategic_intent_ref": value.get("strategic_intent_ref"),
            "opportunity_or_problem_ref": value.get("opportunity_or_problem_ref"),
            "audience_context_ref": value.get("audience_context_ref"),
            "requested_outcome": value.get("requested_outcome"),
            "content_job_or_product_intent": value.get("content_job_or_product_intent"),
            "knowledge_basis_refs": tuple(value.get("knowledge_basis_refs", ())),
            "evidence_refs": tuple(value.get("evidence_refs", ())),
            "decision_ref": value.get("decision_ref"),
            "decision_status": value.get("decision_status"),
            "authority_ref": value.get("authority_ref"),
            "constraints": tuple(value.get("constraints", ())),
            "acceptance_criteria": tuple(value.get("acceptance_criteria", ())),
            "release_requirements": tuple(value.get("release_requirements", ())),
            "success_signals": tuple(value.get("success_signals", ())),
        }
        missing = [key for key, item in fields.items() if item is None]
        if missing:
            raise ValueError(f"missing ContentDemand fields: {', '.join(missing)}")
        return cls(**fields)

    def to_mapping(self) -> dict[str, Any]:
        return {
            "demand_id": self.demand_id,
            "revision_id": self.revision_id,
            "strategic_intent_ref": self.strategic_intent_ref,
            "opportunity_or_problem_ref": self.opportunity_or_problem_ref,
            "audience_context_ref": self.audience_context_ref,
            "requested_outcome": self.requested_outcome,
            "content_job_or_product_intent": self.content_job_or_product_intent,
            "knowledge_basis_refs": list(self.knowledge_basis_refs),
            "evidence_refs": list(self.evidence_refs),
            "decision_ref": self.decision_ref,
            "decision_status": self.decision_status,
            "authority_ref": self.authority_ref,
            "constraints": list(self.constraints),
            "acceptance_criteria": list(self.acceptance_criteria),
            "release_requirements": list(self.release_requirements),
            "success_signals": list(self.success_signals),
        }

    def to_work_item(self, *, work_item_id: str, owner: str, required_capabilities: tuple[str, ...]):
        from .runtime import WorkItem

        return WorkItem(
            work_item_id=work_item_id,
            revision_id=self.revision_id,
            objective=self.content_job_or_product_intent,
            requested_outcome=self.requested_outcome,
            inputs=(self.opportunity_or_problem_ref, *self.evidence_refs),
            knowledge_basis=self.knowledge_basis_refs,
            required_capabilities=required_capabilities,
            owner=owner,
            acceptance_criteria=self.acceptance_criteria,
            release_requirements=self.release_requirements,
            constraints=self.constraints,
            dependencies=(self.decision_ref,),
            success_signals=self.success_signals,
        )
