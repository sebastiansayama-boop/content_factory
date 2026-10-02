import json

from content_factory.gemini_adapter import GeminiConfig, GeminiOpenAICompatibleAdapter
from content_factory.integrations import ExternalCallResult


def test_gemini_config_reads_model_from_environment(monkeypatch):
    monkeypatch.setenv("GEMINI_MODEL", "gemini-test-model")
    monkeypatch.setenv("GEMINI_ENDPOINT", "https://example.test/chat")
    monkeypatch.setenv("GEMINI_API_KEY_ENV", "TEST_GEMINI_KEY")
    monkeypatch.setenv("GEMINI_RESEARCH_MODEL", "gemini-research-test-model")

    config = GeminiConfig.from_env()

    assert config.model == "gemini-test-model"
    assert config.endpoint == "https://example.test/chat"
    assert config.secret_env == "TEST_GEMINI_KEY"
    assert config.research_model == "gemini-research-test-model"


def test_gemini_response_text_extracts_chat_completion():
    result = ExternalCallResult(
        integration_id="gemini.chat.completions",
        status_code=200,
        response_id="resp-1",
        payload={
            "choices": [
                {"message": {"content": json.dumps({"script": "real material"})}}
            ]
        },
    )

    assert GeminiOpenAICompatibleAdapter.response_text(result) == '{"script": "real material"}'


def test_gemini_response_text_rejects_missing_text():
    result = ExternalCallResult(
        integration_id="gemini.chat.completions",
        status_code=200,
        response_id="resp-1",
        payload={"choices": [{"message": {}}]},
    )

    try:
        GeminiOpenAICompatibleAdapter.response_text(result)
    except ValueError as exc:
        assert str(exc) == "Gemini response contains no text output"
    else:
        raise AssertionError("expected missing Gemini text to fail")

def test_gemini_generate_requests_json_object(monkeypatch):
    adapter = GeminiOpenAICompatibleAdapter()
    captured = {}

    def fake_call(payload):
        captured.update(payload)
        return ExternalCallResult(
            integration_id="gemini.chat.completions",
            status_code=200,
            response_id="resp-1",
            payload={"choices": [{"message": {"content": '{"ok": true}'}}]},
        )

    monkeypatch.setattr(adapter._http, "call", fake_call)

    adapter.generate("return JSON")

    assert captured["response_format"] == {\n        "type": "json_schema",\n        "json_schema": {\n            "name": "content_factory_output",\n            "strict": True,\n            "schema": {\n                "type": "object",\n                "additionalProperties": True,\n            },\n        },\n    }
