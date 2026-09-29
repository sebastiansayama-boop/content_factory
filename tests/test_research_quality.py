from __future__ import annotations

from content_factory.research_quality import (
    is_relevant_claim,
    is_relevant_source,
    validate_research_relevance,
)


def future_brief() -> str:
    return "How people in history imagined the future from ancient times to the nineteenth century"


def test_future_history_source_relevance():
    assert is_relevant_source(
        brief=future_brief(),
        title="History of science fiction",
        extract="The history of science fiction explores ideas about future societies and technology.",
    )
    assert not is_relevant_source(
        brief=future_brief(),
        title="Immortality",
        extract="Immortality is a recurring theme in literature and mythology.",
    )


def test_future_history_claim_relevance():
    assert is_relevant_claim(
        brief=future_brief(),
        claim="People developed changing ideas about future society and technology.",
        evidence="Historical writers imagined future societies shaped by technology.",
    )
    assert not is_relevant_claim(
        brief=future_brief(),
        claim="Immortality is a common theme in literature.",
        evidence="The theme appears in mythology and science fiction.",
    )


def test_research_relevance_passes_when_claims_link_to_relevant_sources():
    research = {
        "claims": [
            {
                "id": "c1",
                "text": "Historical writers imagined future societies.",
                "source_ids": ["s1"],
                "evidence_ids": ["e1"],
            },
            {
                "id": "c2",
                "text": "Utopian works described possible future societies.",
                "source_ids": ["s2"],
                "evidence_ids": ["e2"],
            },
            {
                "id": "c3",
                "text": "Science fiction developed new ways of imagining future technology.",
                "source_ids": ["s3"],
                "evidence_ids": ["e3"],
            },
        ],
        "sources": [
            {"id": "s1", "title": "History of ideas", "url": "https://example.com/1"},
            {"id": "s2", "title": "Utopia", "url": "https://example.com/2"},
            {"id": "s3", "title": "Science fiction", "url": "https://example.com/3"},
        ],
        "evidence": [
            {"id": "e1", "source_id": "s1", "excerpt": "Historical writers imagined future societies.", "locator": "lead", "provenance": "test"},
            {"id": "e2", "source_id": "s2", "excerpt": "Utopian works described possible future societies.", "locator": "lead", "provenance": "test"},
            {"id": "e3", "source_id": "s3", "excerpt": "Science fiction developed new ways of imagining future technology.", "locator": "lead", "provenance": "test"},
        ],
    }

    result = validate_research_relevance(brief=future_brief(), research=research)

    assert result["status"] == "PASS"
    assert result["relevant_claim_count"] == 3
    assert result["relevant_source_count"] == 3


def test_research_relevance_fails_on_irrelevant_claims():
    research = {
        "claims": [
            {
                "id": "c1",
                "text": "Immortality is a common literary theme.",
                "source_ids": ["s1"],
                "evidence_ids": ["e1"],
            },
        ],
        "sources": [{"id": "s1", "title": "Immortality", "url": "https://example.com/1"}],
        "evidence": [
            {
                "id": "e1",
                "source_id": "s1",
                "excerpt": "Immortality is a common literary theme.",
                "locator": "lead",
                "provenance": "test",
            }
        ],
    }

    result = validate_research_relevance(brief=future_brief(), research=research)

    assert result["status"] == "FAIL"
    assert result["relevant_claim_count"] == 0
    assert result["rejected_claim_ids"] == ["c1"]


def test_future_history_research_requires_source_diversity():
    from content_factory.research_quality import validate_research_relevance

    research = {
        "claims": [
            {"id": "c1", "text": "Historical ideas about the future included prophecy and prediction.", "source_ids": ["s1"], "evidence_ids": ["e1"]},
            {"id": "c2", "text": "Utopian writing imagined future societies.", "source_ids": ["s2"], "evidence_ids": ["e2"]},
            {"id": "c3", "text": "Science fiction developed ideas about technological futures.", "source_ids": ["s3"], "evidence_ids": ["e3"]},
        ],
        "sources": [
            {"id": "s1", "title": "History of science fiction", "source_type": "secondary_encyclopedic"},
            {"id": "s2", "title": "Utopia", "source_type": "secondary_encyclopedic"},
            {"id": "s3", "title": "Futurism", "source_type": "secondary_encyclopedic"},
        ],
        "evidence": [
            {"id": "e1", "source_id": "s1", "excerpt": "History of future prophecy and prediction."},
            {"id": "e2", "source_id": "s2", "excerpt": "Utopian future society."},
            {"id": "e3", "source_id": "s3", "excerpt": "Technological futures and science fiction."},
        ],
    }

    result = validate_research_relevance(
        brief="how people in the past imagined the future across ancient and modern history",
        research=research,
    )

    assert result["status"] == "FAIL"
    assert result["relevant_source_count"] == 3
    assert result["relevant_source_types"] == ["secondary_encyclopedic"]
    assert result["minimum_source_types"] == 2


def test_future_history_research_passes_with_scholarly_source_diversity():
    from content_factory.research_quality import validate_research_relevance

    research = {
        "claims": [
            {"id": "c1", "text": "Historical ideas about the future included prophecy and prediction.", "source_ids": ["s1"], "evidence_ids": ["e1"]},
            {"id": "c2", "text": "Utopian writing imagined future societies.", "source_ids": ["s2"], "evidence_ids": ["e2"]},
            {"id": "c3", "text": "Science fiction developed ideas about technological futures.", "source_ids": ["s3"], "evidence_ids": ["e3"]},
        ],
        "sources": [
            {"id": "s1", "title": "History of science fiction", "source_type": "secondary_encyclopedic"},
            {"id": "s2", "title": "Utopia", "source_type": "secondary_encyclopedic"},
            {"id": "s3", "title": "Historical study of imagined futures", "source_type": "scholarly_index"},
        ],
        "evidence": [
            {"id": "e1", "source_id": "s1", "excerpt": "History of future prophecy and prediction."},
            {"id": "e2", "source_id": "s2", "excerpt": "Utopian future society."},
            {"id": "e3", "source_id": "s3", "excerpt": "Historical study of technological futures."},
        ],
    }

    result = validate_research_relevance(
        brief="how people in the past imagined the future across ancient and modern history",
        research=research,
    )

    assert result["status"] == "PASS"
    assert result["relevant_source_types"] == ["scholarly_index", "secondary_encyclopedic"]
