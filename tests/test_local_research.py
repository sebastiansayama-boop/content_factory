from __future__ import annotations

import json
import urllib.parse

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
            return _Response({"query": {"search": [{"title": "History of ideas"}]}})
        title = urllib.parse.unquote(url.rsplit("/", 1)[-1]).replace("_", " ")
        return _Response(
            {
                "title": title,
                "extract": f"{title} documents a historical development related to ideas about the future.",
            }
        )

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    adapter = LocalResearchAdapter(fixture=False)
    result = adapter.research(
        "You are the research stage. Research the user's brief using live web search. "
        "USER BRIEF: how people in the past imagined the future across ancient and modern history"
    )
    data = json.loads(adapter.text(result))
    titles = {source["title"] for source in data["sources"]}

    assert result.integration_id == "public-research-wikipedia-openalex"
    assert len(data["claims"]) >= 2
    assert len(data["sources"]) >= 2
    assert data["claims"][0]["source_ids"] == ["source-1"]
    assert data["claims"][0]["evidence_ids"] == ["evidence-1"]
    assert "History of science fiction" in titles
    assert any(urllib.parse.urlparse(url).hostname == "en.wikipedia.org" for url in calls)


def test_local_research_fixture_mode_remains_available(monkeypatch):
    monkeypatch.setenv("FACTORY_LOCAL_RESEARCH_MODE", "fixture")
    adapter = LocalResearchAdapter()
    result = adapter.research(
        "Research the user's brief using live web search. USER BRIEF: test topic"
    )
    data = json.loads(adapter.text(result))

    assert result.integration_id == "local-research-fixture"
    assert data["claims"][0]["id"] == "claim-local-1"


def test_local_research_adds_openalex_abstract_evidence(monkeypatch):
    def fake_urlopen(request, timeout=20.0):
        url = request.full_url
        if "api.openalex.org/works" in url:
            return _Response({
                "results": [{
                    "id": "https://openalex.org/W1",
                    "display_name": "History of future expectations",
                    "publication_year": 2020,
                    "primary_location": {"landing_page_url": "https://example.org/paper"},
                    "abstract_inverted_index": {
                        "Historical": [0], "actors": [1], "imagined": [2], "future": [3]
                    },
                }]
            })
        if "list=search" in url:
            return _Response({"query": {"search": [{"title": "History of ideas"}]}})
        title = urllib.parse.unquote(url.rsplit("/", 1)[-1]).replace("_", " ")
        return _Response({
            "title": title,
            "extract": f"{title} documents a historical development related to ideas about the future.",
        })

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    adapter = LocalResearchAdapter(fixture=False)
    result = adapter.research(
        "Research the user's brief using live web search. USER BRIEF: how people in the past imagined the future across ancient and modern history"
    )
    data = json.loads(adapter.text(result))
    assert any(source["url"] == "https://example.org/paper" for source in data["sources"])
    assert any(e["provenance"] == "openalex-public-api" for e in data["evidence"])
    assert any("Historical actors imagined future" in claim["text"] for claim in data["claims"])
