import os

import pytest

from content_factory.integrations import IntegrationConfig, IntegrationError
from content_factory.openai_adapter import OpenAIResponsesAdapter, OpenAIResponsesConfig


def test_integration_rejects_non_http_endpoint():
    with pytest.raises(IntegrationError):
        IntegrationConfig("x", "file:///tmp/provider").validate()


def test_integration_requires_declared_secret():
    os.environ.pop("CF_TEST_SECRET", None)
    with pytest.raises(IntegrationError):
        IntegrationConfig("x", "https://example.invalid", "CF_TEST_SECRET").validate()


def test_openai_adapter_uses_responses_endpoint_and_declared_secret(monkeypatch):
    monkeypatch.setenv("CF_TEST_SECRET", "test-secret")
    adapter = OpenAIResponsesAdapter(
        OpenAIResponsesConfig(
            model="test-model",
            endpoint="https://example.invalid/v1/responses",
            secret_env="CF_TEST_SECRET",
        )
    )
    assert adapter.config.model == "test-model"
    assert adapter.config.secret_env == "CF_TEST_SECRET"


def test_openai_response_text_extracts_text_chunks():
    result = type(
        "Result",
        (),
        {
            "payload": {
                "output": [
                    {"content": [{"type": "output_text", "text": "hello"}]},
                    {"content": [{"type": "output_text", "text": " world"}]},
                ]
            }
        },
    )()
    assert OpenAIResponsesAdapter.response_text(result) == "hello world"


def test_openai_response_text_rejects_missing_text():
    result = type("Result", (), {"payload": {"output": []}})()
    with pytest.raises(ValueError, match="no text output"):
        OpenAIResponsesAdapter.response_text(result)
