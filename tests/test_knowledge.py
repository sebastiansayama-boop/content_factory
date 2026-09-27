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
            }
        ],
        "sources": [
            {
                "id": "source-1",
                "title": "Example source",
                "url": "https://example.com/cities",
            }
        ],
        "editorial_angles": ["technology changes the shape of cities"],
    }


def test_capture_is_durable_and_deduplicates(tmp_path):
    store = KnowledgeStore(tmp_path / "knowledge.sqlite3")
    first = store.capture(run_id="run-1", research=research_payload())
    second = store.capture(run_id="run-2", research=research_payload())

    assert first == {"sources_added": 1, "claims_added": 1, "angles_added": 1}
    assert second == {"sources_added": 0, "claims_added": 0, "angles_added": 0}
    assert store.counts() == {"sources": 1, "claims": 1, "editorial_angles": 1, "runs": 2}

    store.close()
    reopened = KnowledgeStore(tmp_path / "knowledge.sqlite3")
    assert reopened.counts()["claims"] == 1
    result = reopened.search("automobiles urban mobility")
    assert result["claims"][0]["text"] == research_payload()["claims"][0]["text"]
    assert result["sources"][0]["url"] == "https://example.com/cities"
    assert result["editorial_angles"][0]["text"] == "technology changes the shape of cities"
    reopened.close()


def test_search_empty_query_returns_empty(tmp_path):
    store = KnowledgeStore(tmp_path / "knowledge.sqlite3")
    assert store.search("x") == {"claims": [], "sources": [], "editorial_angles": []}
    store.close()
