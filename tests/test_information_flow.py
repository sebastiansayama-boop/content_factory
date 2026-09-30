import pytest

from content_factory.information_flow import (
    InformationFlowError,
    build_information_flow,
)


def research_payload():
    return {
        "claims": [
            {
                "id": "claim-1",
                "text": "Claim one",
                "confidence": "high",
                "source_ids": ["source-1"],
                "evidence_ids": ["evidence-1"],
                "scope": "bounded",
                "known_unknowns": ["unknown"],
            }
        ],
        "sources": [
            {"id": "source-1", "title": "Source", "url": "https://example.com/source"},
        ],
        "evidence": [
            {
                "id": "evidence-1",
                "source_id": "source-1",
                "excerpt": "Supporting evidence",
                "locator": "paragraph 1",
            }
        ],
        "editorial_angles": ["A defensible angle"],
    }


def package_payload():
    return {
        "topic": "Topic",
        "story": {"id": "story-1", "title": "Topic", "angle": "A defensible angle"},
        "package": [
            {
                "id": "asset-1",
                "format": "article",
                "content": "Grounded content",
                "source_refs": ["source-1"],
                "claim_refs": ["claim-1"],
                "evidence_refs": ["evidence-1"],
            }
        ],
    }


def test_information_flow_materializes_the_full_semantic_chain():
    flow = build_information_flow(
        run_id="run-1",
        research=research_payload(),
        package=package_payload(),
    )

    assert len(flow.sources) == 1
    assert len(flow.evidence) == 1
    assert len(flow.claims) == 1
    assert len(flow.editorial_points) == 1
    assert len(flow.content_elements) == 1
    assert len(flow.artifacts) == 1

    relations = {edge.relation for edge in flow.edges}
    assert {
        "source_to_evidence",
        "evidence_to_claim",
        "claim_to_editorial_point",
        "editorial_point_to_content_element",
        "content_element_to_artifact",
        "claim_to_artifact",
        "evidence_to_artifact",
    }.issubset(relations)


def test_information_flow_rejects_artifact_claim_without_evidence():
    package = package_payload()
    package["package"][0]["evidence_refs"] = []

    with pytest.raises(InformationFlowError, match="must expose evidence_refs"):
        build_information_flow(
            run_id="run-1",
            research=research_payload(),
            package=package,
        )


def test_information_flow_rejects_unknown_artifact_claim():
    package = package_payload()
    package["package"][0]["claim_refs"] = ["claim-missing"]
    package["package"][0]["evidence_refs"] = ["evidence-1"]

    with pytest.raises(InformationFlowError, match="unknown claim"):
        build_information_flow(
            run_id="run-1",
            research=research_payload(),
            package=package,
        )


def test_information_flow_rejects_claim_with_unknown_evidence():
    research = research_payload()
    research["claims"][0]["evidence_ids"] = ["evidence-missing"]

    with pytest.raises(InformationFlowError, match="unknown evidence"):
        build_information_flow(
            run_id="run-1",
            research=research,
            package=package_payload(),
        )
