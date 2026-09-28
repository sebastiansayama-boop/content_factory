from __future__ import annotations

import io
import json
import urllib.error

import pytest

from content_factory.gemini_research import GeminiGoogleSearchResearchAdapter, GeminiResearchConfig, GeminiResearchError
from content_factory.integrations import ExternalCallResult


def grounded_result():
    payload = {
        "responseId": "resp-1",
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": json.dumps(
                                {
                                    "topic": "History of future",
                                    "summary": "Grounded research.",
                                    "claims": [
                                        {
                                            "id": "claim-1",
                                            "text": "People imagined future societies in utopian works.",
                                            "confidence": "medium",
                                            "source_urls": ["https://example.com/utopia"],
                                            "evidence": [
                                                {
                                                    "source_url": "https://example.com/utopia",
                                                    "excerpt": "A concrete historical excerpt about an imagined future society.",
                                                }
                                            ],
                                            "scope": "historical utopian thought",
                                            "known_unknowns": ["Secondary synthesis remains necessary."],
                                        }
                                    ],
                                }
                            )
                        }
                    ]
                },
                "groundingMetadata": {
                    "webSearchQueries": ["history of future utopia"],
                    "groundingChunks": [
                        {"web": {"uri": "https://example.com/utopia", "title": "Utopia source"}}
                    ],
                },
            }
        ],
    }
    return ExternalCallResult(
        integration_id="gemini.google-search-research",
        status_code=200,
        response_id="resp-1",
        payload=payload,
    )


def test_gemini_grounding_exposes_real_sources():
    result = grounded_result()
    assert GeminiGoogleSearchResearchAdapter.sources(result) == [
        {"url": "https://example.com/utopia", "title": "Utopia source"}
    ]
    assert GeminiGoogleSearchResearchAdapter.search_queries(result) == [
        "history of future utopia"
    ]


def test_gemini_normalization_rejects_unverified_url():
    raw = json.loads(
        GeminiGoogleSearchResearchAdapter.text(grounded_result())
    )
    raw["claims"][0]["source_urls"] = ["https://evil.example/not-grounded"]

    with pytest.raises(ValueError, match="no source URL returned by grounding"):
        GeminiGoogleSearchResearchAdapter.normalize_research(
            raw,
            GeminiGoogleSearchResearchAdapter.sources(grounded_result()),
        )


def test_gemini_normalization_creates_durable_schema():
    raw = json.loads(GeminiGoogleSearchResearchAdapter.text(grounded_result()))
    normalized = GeminiGoogleSearchResearchAdapter.normalize_research(
        raw,
        GeminiGoogleSearchResearchAdapter.sources(grounded_result()),
    )

    assert normalized["sources"][0]["id"] == "source-1"
    assert normalized["claims"][0]["source_ids"] == ["source-1"]
    assert normalized["claims"][0]["evidence_ids"] == ["evidence-1"]
    assert normalized["evidence"][0]["source_id"] == "source-1"


def test_gemini_429_is_classified_as_quota_exhausted(monkeypatch):
    payload = {
        "error": {
            "code": 429,
            "message": "You exceeded your current quota.",
            "status": "RESOURCE_EXHAUSTED",
        }
    }
    body = io.BytesIO(json.dumps(payload).encode("utf-8"))

    def fail(_request, timeout=None):
        raise urllib.error.HTTPError(
            url="https://example.invalid",
            code=429,
            msg="Too Many Requests",
            hdrs=None,
            fp=body,
        )

    monkeypatch.setattr("urllib.request.urlopen", fail)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    with pytest.raises(GeminiResearchError) as exc_info:
        GeminiGoogleSearchResearchAdapter().research("test research")

    assert exc_info.value.http_status == 429
    assert exc_info.value.kind == "quota_exhausted"


def test_gemini_429_triggers_deterministic_fallback(monkeypatch):
    from content_factory.vertical_slice import ContentFactoryVerticalSlice

    class FakeGemini(GeminiGoogleSearchResearchAdapter):
        def __init__(self):
            pass

        def research(self, prompt):
            raise GeminiResearchError(
                "Gemini research provider returned HTTP 429 (RESOURCE_EXHAUSTED): quota",
                http_status=429,
                kind="quota_exhausted",
            )

    class FakeFallback:
        research_provider_id = "fake-fallback"

        def research(self, prompt):
            return "fallback-result"

    factory = ContentFactoryVerticalSlice(FakeGemini())
    monkeypatch.setattr(
        ContentFactoryVerticalSlice,
        "_build_fallback_research_adapter",
        staticmethod(lambda: FakeFallback()),
    )

    result = factory._research_call("test research")

    assert result == "fallback-result"
    assert factory.provider_fallback == {
        "configured_provider": "gemini",
        "fallback_provider": "fake-fallback",
        "reason": "quota_exhausted",
        "http_status": 429,
        "message": "Gemini research provider returned HTTP 429 (RESOURCE_EXHAUSTED): quota",
    }