import json

import json
from urllib.parse import urlparse

from content_factory.free_research import FreeWebGeminiAdapter, FreeWebRetriever, RetrievalItem, RetrievalPacket
from content_factory.gemini_adapter import GeminiConfig
from content_factory.integrations import ExternalCallResult


class FakeResponse:
    def __init__(self, payload):
        self.status = 200
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        if isinstance(self.payload, str):
            return self.payload.encode("utf-8")
        return json.dumps(self.payload).encode("utf-8")


def test_free_web_retriever_builds_wikipedia_and_openalex_evidence():
    def fake_urlopen(request, timeout=20):
        url = request.full_url
        if "action=opensearch" in url:
            return FakeResponse([
                "convergent evolution",
                ["Convergent evolution"],
                [""],
                ["https://en.wikipedia.org/wiki/Convergent_evolution"],
            ])
        if "action=query" in url:
            return FakeResponse({
                "query": {
                    "pages": [{
                        "title": "Convergent evolution",
                        "extract": "Convergent evolution is the independent evolution of similar traits.",
                    }]
                }
            })
        if "news.google.com/rss/search?" in url:
            return FakeResponse("""<?xml version="1.0"?><rss><channel><item><title>Convergent evolution example</title><link>https://example.org/story</link><description>Independent lineages can evolve similar traits under similar selection pressures.</description></item></channel></rss>""")
        if "api.openalex.org/works?search=" in url:
            return FakeResponse({
                "results": [{
                    "id": "https://openalex.org/W1",
                    "display_name": "Convergent evolution in biology",
                    "doi": "https://doi.org/10.1234/example",
                    "publication_date": "2024-01-01",
                    "updated_date": "2024-02-01",
                    "primary_location": {"license": "cc-by"},
                    "abstract_inverted_index": {
                        "Similar": [0],
                        "traits": [1],
                        "can": [2],
                        "evolve": [3],
                    },
                }]
            })
        raise AssertionError(f"unexpected URL: {url}")

    packet = FreeWebRetriever(
        opener=fake_urlopen,
        wiki_limit=1,
        openalex_limit=1,
    ).retrieve("convergent evolution")

    assert len(packet.items) == 3
    assert {item.provider for item in packet.items} == {"wikipedia", "openalex", "google_news"}
    assert all(item.source_id and item.evidence_id and item.excerpt for item in packet.items)
    assert all(item.url.startswith("http") for item in packet.items)


class FakeGemini:
    def __init__(self):
        self.prompts = []

    def generate(self, prompt):
        self.prompts.append(prompt)
        text = '{"topic":"Convergent evolution","summary":"supported","claims":[],"sources":[],"evidence":[],"editorial_angles":[]}'
        return ExternalCallResult(
            integration_id="gemini.chat.completions",
            status_code=200,
            response_id="g-1",
            payload={
                "choices": [{
                    "message": {
                        "content": text,
                    }
                }]
            },
        )


class FakeRetriever:
    def __init__(self):
        self.calls = 0

    def retrieve(self, query):
        self.calls += 1
        return RetrievalPacket(
            query=query,
            retrieved_at="2026-10-01T00:00:00Z",
            items=(
                RetrievalItem(
                    source_id="source:wikipedia:test",
                    provider="wikipedia",
                    external_id="Test",
                    title="Test source",
                    url="https://en.wikipedia.org/wiki/Test",
                    excerpt="Evidence from the public source.",
                ),
            ),
        )


def test_free_web_retriever_falls_back_to_google_news_when_other_sources_fail():
    def fake_urlopen(request, timeout=20):
        host = urlparse(request.full_url).hostname
        if host == "en.wikipedia.org":
            raise OSError("blocked")
        if host == "api.openalex.org":
            raise OSError("rate limited")
        if "news.google.com/rss/search?" in request.full_url:
            return FakeResponse("""<?xml version="1.0"?><rss><channel><item><title>Fallback story</title><link>https://example.org/fallback</link><description>Fallback evidence text.</description></item></channel></rss>""")
        raise AssertionError(request.full_url)

    packet = FreeWebRetriever(
        opener=fake_urlopen, wiki_limit=1, openalex_limit=1, news_limit=1
    ).retrieve("convergent evolution")
    assert len(packet.items) == 1
    assert packet.items[0].provider == "google_news"
    assert packet.items[0].excerpt == "Fallback evidence text."


def test_free_web_gemini_reuses_retrieval_and_exposes_only_retrieved_sources():
    retriever = FakeRetriever()
    gemini = FakeGemini()
    adapter = FreeWebGeminiAdapter(
        GeminiConfig(model="gemini-test"),
        retriever=retriever,
        gemini=gemini,
    )

    research_prompt = """You are the research stage.
Research the user's brief using live web search.
USER BRIEF:
convergent evolution
"""
    result = adapter.research(research_prompt)

    assert retriever.calls == 1
    assert "SUPPLIED RETRIEVAL PACK" in gemini.prompts[0]
    assert "Do not perform or claim additional web search" in gemini.prompts[0]
    assert "source:wikipedia:test" in gemini.prompts[0]
    assert adapter.sources(result) == [{
        "id": "source:wikipedia:test",
        "title": "Test source",
        "url": "https://en.wikipedia.org/wiki/Test",
    }]

    production_result = adapter.research(
        'Create one article. Return ONLY JSON: {"content":"complete usable content"}'
    )
    assert retriever.calls == 1
    assert "RETRIEVAL PACK USED FOR THIS RUN" in gemini.prompts[1]
    assert adapter.text(production_result).startswith("{")



def test_free_web_gemini_topic_research_reuses_packet_for_production():
    retriever = FakeRetriever()
    gemini = FakeGemini()
    adapter = FreeWebGeminiAdapter(
        GeminiConfig(model="gemini-test"),
        retriever=retriever,
        gemini=gemini,
    )

    research_prompt = (
        "You are the research stage. Research this topic and return JSON.\n"
        "TOPIC:\nМалоизвестные факты из истории человечества\n"
    )
    adapter.research(research_prompt)
    assert retriever.calls == 1
    assert "SUPPLIED RETRIEVAL PACK" in gemini.prompts[0]
    assert adapter._packet.query == "Малоизвестные факты из истории человечества"

    # A generation prompt can contain TOPIC without starting a new research run.
    production_prompt = (
        "Write one finished Telegram publication in Russian.\n"
        "TOPIC:\nМалоизвестные факты из истории человечества\n"
        "ACCEPTED KNOWLEDGE: provided claims and evidence\n"
    )
    adapter.research(production_prompt)
    assert retriever.calls == 1
    assert "RETRIEVAL PACK USED FOR THIS RUN" in gemini.prompts[1]


def test_free_web_gemini_rejects_production_without_retrieval():
    import pytest

    retriever = FakeRetriever()
    adapter = FreeWebGeminiAdapter(
        GeminiConfig(model="gemini-test"),
        retriever=retriever,
        gemini=FakeGemini(),
    )
    with pytest.raises(RuntimeError, match="production requested before retrieval-backed research"):
        adapter.research("Write a Telegram post.\nTOPIC:\nHistory\n")
    assert retriever.calls == 0


def test_free_web_gemini_uses_plain_gemini_chat_api_without_search_tool(monkeypatch):
    import content_factory.integrations as integrations

    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    captured = {}

    def fake_urlopen(request, timeout=30):
        captured["url"] = request.full_url
        captured["headers"] = dict(request.headers)
        captured["payload"] = json.loads(request.data.decode("utf-8"))
        return FakeResponse({
            "id": "chat-1",
            "choices": [{
                "message": {"content": "ok"}
            }],
        })

    monkeypatch.setattr(integrations, "urlopen", fake_urlopen)

    adapter = FreeWebGeminiAdapter(
        GeminiConfig(model="gemini-test"),
        retriever=FakeRetriever(),
    )
    adapter.research("USER BRIEF:\nconvergent evolution")

    assert captured["url"].endswith("/v1beta/openai/chat/completions")
    assert captured["headers"]["Authorization"] == "Bearer test-key"
    assert captured["payload"]["model"] == "gemini-test"
    assert "tools" not in captured["payload"]


def test_free_web_retriever_retries_wikipedia_with_compact_query():
    from urllib.parse import parse_qs

    def fake_urlopen(request, timeout=20):
        url = request.full_url
        if "action=opensearch" in url:
            query_value = parse_qs(urlparse(url).query)["search"][0]
            if query_value == "Explain how volcanic lightning forms during explosive eruptions and what remains uncertain.":
                return FakeResponse(["query", [], [], []])
            return FakeResponse([
                "volcanic lightning",
                ["Volcanic lightning"],
                [""],
                ["https://en.wikipedia.org/wiki/Volcanic_lightning"],
            ])
        if "action=query" in url:
            return FakeResponse({
                "query": {
                    "pages": [{
                        "title": "Volcanic lightning",
                        "extract": "Volcanic lightning is a luminous electrical discharge observed in volcanic plumes.",
                    }]
                }
            })
        if "api.openalex.org/works?search=" in url:
            raise OSError("rate limited")
        if "news.google.com/rss/search?" in url:
            return FakeResponse("""<?xml version="1.0"?><rss><channel></channel></rss>""")
        raise AssertionError(f"unexpected URL: {url}")

    packet = FreeWebRetriever(
        opener=fake_urlopen,
        wiki_limit=1,
        openalex_limit=1,
        news_limit=1,
    ).retrieve(
        "Explain how volcanic lightning forms during explosive eruptions and what remains uncertain."
    )

    assert len(packet.items) == 1
    assert packet.items[0].provider == "wikipedia"
    assert packet.items[0].external_id == "Volcanic lightning"


def test_free_web_retriever_retries_wikipedia_with_compact_query():
    from urllib.parse import parse_qs

    def fake_urlopen(request, timeout=20):
        url = request.full_url
        if "action=opensearch" in url:
            query_value = parse_qs(urlparse(url).query)["search"][0]
            if query_value.startswith("Explain how volcanic"):
                return FakeResponse(["query", [], [], []])
            return FakeResponse([
                "volcanic lightning",
                ["Volcanic lightning"],
                [""],
                ["https://en.wikipedia.org/wiki/Volcanic_lightning"],
            ])
        if "action=query" in url:
            return FakeResponse({
                "query": {
                    "pages": [{
                        "title": "Volcanic lightning",
                        "extract": "Volcanic lightning is a luminous electrical discharge observed in volcanic plumes.",
                    }]
                }
            })
        if "api.openalex.org/works?search=" in url:
            raise OSError("rate limited")
        if "news.google.com/rss/search?" in url:
            return FakeResponse("""<?xml version="1.0"?><rss><channel></channel></rss>""")
        raise AssertionError(f"unexpected URL: {url}")

    packet = FreeWebRetriever(
        opener=fake_urlopen,
        wiki_limit=1,
        openalex_limit=1,
        news_limit=1,
    ).retrieve(
        "Explain how volcanic lightning forms during explosive eruptions and what remains uncertain."
    )

    assert len(packet.items) == 1
    assert packet.items[0].provider == "wikipedia"
    assert packet.items[0].external_id == "Volcanic lightning"
