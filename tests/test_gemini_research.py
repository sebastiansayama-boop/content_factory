import json

from content_factory.gemini_adapter import GeminiConfig
from content_factory.integrations import ExternalCallResult
from content_factory.research import GeminiWebResearchAdapter


def test_gemini_web_research_builds_native_grounding_request(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-test")
    monkeypatch.setenv("GEMINI_RESEARCH_MODEL", "gemini-research-test")
    adapter = GeminiWebResearchAdapter(GeminiConfig.from_env())

    captured = {}

    class FakeResponse:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return json.dumps({
                "id": "int-1",
                "output_text": "grounded response",
                "steps": [{
                    "type": "model_output",
                    "content": [{
                        "type": "text",
                        "text": "grounded response",
                        "annotations": [{
                            "type": "url_citation",
                            "url": "https://example.com/source",
                            "title": "Example source",
                        }],
                    }],
                }],
            }).encode("utf-8")

    from content_factory import integrations

    def fake_urlopen(request, timeout=30):
        captured["url"] = request.full_url
        captured["headers"] = dict(request.headers)
        captured["payload"] = json.loads(request.data.decode("utf-8"))
        return FakeResponse()

    monkeypatch.setattr(integrations, "urlopen", fake_urlopen)

    result = adapter.research("Research how people imagined the future.")
    assert result.status_code == 200
    assert captured["url"].endswith("/v1beta/interactions")
    assert captured["headers"]["X-goog-api-key"] == "test-key"
    assert captured["payload"]["model"] == "gemini-research-test"
    assert captured["payload"]["tools"] == [{"type": "google_search"}]
    assert adapter.text(result) == "grounded response"
    assert adapter.sources(result) == [{
        "url": "https://example.com/source",
        "title": "Example source",
    }]


def test_gemini_web_research_joins_multiple_text_parts():
    result = ExternalCallResult(
        integration_id="gemini.interactions.google_search",
        status_code=200,
        response_id="int-1",
        payload={
            "steps": [{
                "type": "model_output",
                "content": [{"type": "text", "text": "one "}, {"type": "text", "text": "two"}],
            }]
        },
    )
    assert GeminiWebResearchAdapter.text(result) == "one two"
