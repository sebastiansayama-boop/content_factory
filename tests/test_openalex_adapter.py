from __future__ import annotations

import io
import json

from content_factory.external_source import OpenAlexAdapter
from content_factory.openalex_demand import build_content_demand


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps(self._payload).encode("utf-8")


def test_openalex_source_evidence_claim_to_content_demand():
    work = {
        "id": "https://openalex.org/W123",
        "display_name": "A research result",
        "doi": "https://doi.org/10.1000/example",
        "publication_date": "2026-01-01",
        "abstract_inverted_index": {"Research": [0], "shows": [1], "result": [2]},
        "primary_location": {"license": "cc-by"},
    }
    calls = []

    def opener(request, timeout):
        calls.append(request.full_url)
        if request.full_url.endswith("/works?search=research&per_page=5"):
            return FakeResponse({"results": [work]})
        return FakeResponse(work)

    adapter = OpenAlexAdapter(opener=opener, retrieved_at="2026-09-14T00:00:00Z")
    source = adapter.search("research")[0]
    evidence = adapter.evidence(source)
    claim = adapter.claims(source, evidence)[0]
    demand = build_content_demand(
        source=source,
        evidence=evidence,
        claim=claim,
        demand_id="demand:openalex:1",
        revision_id="revision:1",
        strategic_intent_ref="intent:research-content",
        opportunity_or_problem_ref="opportunity:research-result",
        audience_context_ref="audience:technical",
        requested_outcome="Produce an evidence-backed research explainer.",
        content_job_or_product_intent="Research explainer",
        decision_ref="decision:1",
        authority_ref="authority:1",
        acceptance_criteria=("Preserve source provenance",),
    )

    assert source.provider == "openalex"
    assert evidence.source_id == source.source_id
    assert claim.evidence_refs == (evidence.evidence_id,)
    assert demand.knowledge_basis_refs == (source.source_id,)
    assert demand.evidence_refs == (evidence.evidence_id,)
    assert demand.decision_status == "AUTHORIZED"
    assert calls[0].startswith("https://api.openalex.org/works?search=research")
    assert calls[1] == "https://api.openalex.org/works/W123"
