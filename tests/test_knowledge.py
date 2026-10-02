from content_factory.knowledge import KnowledgeStore


def research_payload():
    return {
        "topic": "Future cities",
        "summary": "Cities were imagined around new transportation.",
        "claims": [
            {
                "id": "claim-1",
                "text": "Automobiles changed expectations about urban mobility.",
                "confidence": "high",
                "source_ids": ["source-1"],
                "evidence_ids": ["evidence-1"],
                "scope": "urban mobility in the twentieth century",
                "known_unknowns": ["The claim does not establish causality for every city."],
            }
        ],
        "sources": [
            {
                "id": "source-1",
                "title": "Example source",
                "url": "https://example.com/cities",
            }
        ],
        "evidence": [
            {
                "id": "evidence-1",
                "source_id": "source-1",
                "excerpt": "Automobiles changed expectations about urban mobility.",
                "locator": "example paragraph",
                "provenance": "example-source",
            }
        ],
        "editorial_angles": ["technology changes the shape of cities"],
    }


def test_capture_is_durable_and_requires_explicit_promotion(tmp_path):
    store = KnowledgeStore(tmp_path / "knowledge.sqlite3")
    first = store.capture(run_id="run-1", research=research_payload())
    second = store.capture(run_id="run-2", research=research_payload())

    assert first == {
        "sources_added": 1,
        "evidence_added": 1,
        "claims_added": 1,
        "angles_added": 1,
    }
    assert second == {
        "sources_added": 0,
        "evidence_added": 0,
        "claims_added": 0,
        "angles_added": 0,
    }
    assert store.counts() == {
        "sources": 1,
        "evidence": 1,
        "claims": 1,
        "accepted_claims": 0,
        "candidate_claims": 1,
        "editorial_angles": 1,
        "runs": 2,
    }

    # Captured research is a candidate, not reusable knowledge.
    assert store.search("automobiles urban mobility") == {
        "claims": [],
        "sources": [],
        "editorial_angles": [],
    }

    claim = store.get_claim(store._connection.execute(
        "SELECT claim_id FROM knowledge_claims"
    ).fetchone()["claim_id"])
    assert claim is not None
    promoted = store.promote_claim(claim.claim_id, decision_ref="DEC-TEST-001")
    assert promoted.status == KnowledgeStore.ACCEPTED
    assert promoted.evidence_ids

    store.close()
    reopened = KnowledgeStore(tmp_path / "knowledge.sqlite3")
    result = reopened.search("automobiles urban mobility")
    assert result["claims"][0]["text"] == research_payload()["claims"][0]["text"]
    assert result["claims"][0]["revision_id"] == promoted.revision_id
    assert result["claims"][0]["evidence_ids"]
    assert result["sources"][0]["url"] == "https://example.com/cities"
    reopened.close()


def test_promotion_requires_evidence(tmp_path):
    store = KnowledgeStore(tmp_path / "knowledge.sqlite3")
    payload = research_payload()
    payload["claims"][0]["evidence_ids"] = ["missing"]
    try:
        store.capture(run_id="run-1", research=payload)
    except ValueError as exc:
        assert "invalid evidence_ids" in str(exc)
    else:
        raise AssertionError("claim without stored evidence must fail closed")
    store.close()


def test_search_empty_query_returns_empty(tmp_path):
    store = KnowledgeStore(tmp_path / "knowledge.sqlite3")
    assert store.search("x") == {"claims": [], "sources": [], "editorial_angles": []}
    store.close()


def test_resolve_research_refs_returns_durable_ids(tmp_path):
    store = KnowledgeStore(tmp_path / "knowledge.sqlite3")
    payload = research_payload()
    store.capture(run_id="run-refs", research=payload)

    refs = store.resolve_research_refs(payload)

    assert set(refs) == {"claims", "sources", "evidence"}
    assert refs["claims"]["claim-1"].startswith("kc-")
    assert refs["sources"]["source-1"].startswith("ks-")
    assert refs["evidence"]["evidence-1"].startswith("ke-")
    store.close()


def test_accepted_knowledge_usage_is_explicit_and_candidates_are_blocked(tmp_path):
    store = KnowledgeStore(tmp_path / "knowledge.sqlite3")
    store.capture(run_id="run-1", research=research_payload())
    claim_id = store._connection.execute(
        "SELECT claim_id FROM knowledge_claims"
    ).fetchone()["claim_id"]

    try:
        store.record_usage(
            run_id="run-2",
            target_ref="content-run:run-2",
            claim_ids=[claim_id],
        )
    except ValueError as exc:
        assert "cannot be used as reusable knowledge" in str(exc)
    else:
        raise AssertionError("candidate knowledge must not be recorded as reusable usage")

    promoted = store.promote_claim(claim_id, decision_ref="DEC-TEST-002")
    assert promoted.decision_ref == "DEC-TEST-002"
    assert promoted.promoted_at

    assert store.record_usage(
        run_id="run-2",
        target_ref="content-run:run-2",
        claim_ids=[claim_id],
    ) == 1
    assert store.record_usage(
        run_id="run-2",
        target_ref="content-run:run-2",
        claim_ids=[claim_id],
    ) == 0

    usages = store.usages_for_claim(claim_id)
    assert len(usages) == 1
    assert usages[0]["run_id"] == "run-2"
    assert usages[0]["target_ref"] == "content-run:run-2"
    store.close()


def test_candidates_for_run_ignores_lexical_overlap(tmp_path):
    store = KnowledgeStore(tmp_path / "knowledge.sqlite3")
    store.capture(run_id="run-gemini", research=research_payload())

    candidates = store.candidates_for_run("run-gemini")

    assert len(candidates) == 1
    assert candidates[0]["text"] == research_payload()["claims"][0]["text"]
    assert candidates[0]["status"] == KnowledgeStore.CANDIDATE
    assert store.candidates_for_run("other-run") == []
    store.close()


def test_search_ignores_weak_single_token_overlap(tmp_path):
    store = KnowledgeStore(tmp_path / "knowledge.sqlite3")
    store.capture(run_id="run-1", research=research_payload())
    claim_id = store._connection.execute(
        "SELECT claim_id FROM knowledge_claims"
    ).fetchone()["claim_id"]
    store.promote_claim(claim_id, decision_ref="DEC-TEST-RELEVANCE")

    assert store.search("automobiles sculpture exhibition") == {
        "claims": [],
        "sources": [],
        "editorial_angles": [],
    }
    assert store.search("automobiles urban mobility")["claims"][0]["claim_id"] == claim_id
    store.close()
