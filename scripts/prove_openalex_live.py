from __future__ import annotations

from datetime import datetime, timezone

from content_factory.external_source import OpenAlexAdapter
from content_factory.openalex_demand import build_content_demand


def main() -> int:
    retrieved_at = datetime.now(timezone.utc).isoformat()
    adapter = OpenAlexAdapter(retrieved_at=retrieved_at)
    sources = adapter.search("artificial intelligence agents")
    if not sources:
        raise RuntimeError("OpenAlex returned no sources")

    source = sources[0]
    evidence = adapter.evidence(source)
    claims = adapter.claims(source, evidence)
    if not claims:
        raise RuntimeError("OpenAlex source produced no claim candidate")

    claim = claims[0]
    demand = build_content_demand(
        source=source,
        evidence=evidence,
        claim=claim,
        demand_id="demand:openalex:live-proof",
        revision_id="revision:openalex:live-proof",
        strategic_intent_ref="intent:live-provider-proof",
        opportunity_or_problem_ref="opportunity:openalex-provider-proof",
        audience_context_ref="audience:technical",
        requested_outcome="Produce an evidence-backed research explainer.",
        content_job_or_product_intent="Research explainer",
        decision_ref="decision:openalex-live-proof",
        authority_ref="authority:openalex-live-proof-operator",
        acceptance_criteria=("Preserve OpenAlex source and evidence provenance",),
    )
    work_item = demand.to_work_item(
        work_item_id="work:openalex:live-proof",
        owner="operator",
        required_capabilities=("content.research.explainer",),
    )

    if demand.decision_status != "AUTHORIZED":
        raise RuntimeError("live proof did not satisfy the explicit intake authorization gate")
    if work_item.knowledge_basis != (source.source_id,):
        raise RuntimeError("WorkItem lost source identity")
    if work_item.inputs != ("opportunity:openalex-provider-proof", evidence.evidence_id):
        raise RuntimeError("WorkItem lost opportunity/evidence references")

    print("OPENALEX LIVE PROOF PASSED")
    print(f"provider={source.provider}")
    print(f"source_id={source.source_id}")
    print(f"external_id={source.external_id}")
    print(f"title={source.title}")
    print(f"evidence_id={evidence.evidence_id}")
    print(f"claim_id={claim.claim_id}")
    print(f"demand_id={demand.demand_id}")
    print(f"work_item_id={work_item.work_item_id}")
    print(f"retrieved_at={source.retrieved_at}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
