from __future__ import annotations

from .content_demand import ContentDemand
from .external_source import Claim, Evidence, Source


def build_content_demand(
    *,
    source: Source,
    evidence: Evidence,
    claim: Claim,
    demand_id: str,
    revision_id: str,
    strategic_intent_ref: str,
    opportunity_or_problem_ref: str,
    audience_context_ref: str,
    requested_outcome: str,
    content_job_or_product_intent: str,
    decision_ref: str,
    authority_ref: str,
    acceptance_criteria: tuple[str, ...],
) -> ContentDemand:
    """Map verified external-source evidence into the existing intake contract."""
    if evidence.evidence_id not in claim.evidence_refs:
        raise ValueError("claim must reference the supplied evidence")
    return ContentDemand(
        demand_id=demand_id,
        revision_id=revision_id,
        strategic_intent_ref=strategic_intent_ref,
        opportunity_or_problem_ref=opportunity_or_problem_ref,
        audience_context_ref=audience_context_ref,
        requested_outcome=requested_outcome,
        content_job_or_product_intent=content_job_or_product_intent,
        knowledge_basis_refs=(source.source_id,),
        evidence_refs=(evidence.evidence_id,),
        decision_ref=decision_ref,
        decision_status="AUTHORIZED",
        authority_ref=authority_ref,
        constraints=(),
        acceptance_criteria=acceptance_criteria,
        release_requirements=(),
        success_signals=(),
    )
