from __future__ import annotations

import json

from content_factory.local_research import LocalResearchAdapter


class _Response:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


def test_local_research_web_mode_uses_public_sources(monkeypatch):
    calls = []

    def fake_urlopen(request, timeout=20.0):
        url = request.full_url
        calls.append(url)
        if "list=search" in url:
            return _Response(
                {
                    "query": {
                        "search": [
                            {"title": "History of ideas"},
                            {"title": "Futurism"},
                        ]
                    }
                }
            )
        if "History_of_ideas" in url:
            return _Response(
                {
                    "title": "History of ideas",
                    "extract": "Historians have studied changing ideas about the future.",
                }
            )
        return _Response(
            {
                "title": "Futurism",
                "extract": "Futurism was an artistic and social movement focused on modernity and technology.",
            }
        )

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    adapter = LocalResearchAdapter(fixture=False)
    result = adapter.research(
        "You are the research stage. Research the user's brief using live web search. "
        "USER BRIEF: how people in the past imagined the future"
    )
    data = json.loads(adapter.text(result))

    assert result.integration_id == "wikipedia-public-research"
    assert len(data["claims"]) == 2
    assert len(data["sources"]) == 2
    assert data["claims"][0]["source_ids"] == ["source-1"]
    assert data["claims"][0]["evidence_ids"] == ["evidence-1"]
    assert any("wikipedia.org" in url for url in calls)


def test_local_research_fixture_mode_remains_available(monkeypatch):
    monkeypatch.setenv("FACTORY_LOCAL_RESEARCH_MODE", "fixture")
    adapter = LocalResearchAdapter()
    result = adapter.research(
        "Research the user's brief using live web search. USER BRIEF: test topic"
    )
    data = json.loads(adapter.text(result))

    assert result.integration_id == "local-research-fixture"
    assert data["claims"][0]["id"] == "claim-local-1"
