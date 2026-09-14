import os

import pytest

from content_factory.integrations import ExternalCallResult, IntegrationConfig, IntegrationError
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
    result = ExternalCallResult(
        integration_id="openai.responses",
        status_code=200,
        response_id="resp-1",
        payload={
            "output": [
                {"content": [{"type": "output_text", "text": "hello"}]},
                {"content": [{"type": "output_text", "text": " world"}]},
            ]
        },
    )
    assert OpenAIResponsesAdapter.response_text(result) == "hello world"


def test_openai_response_text_rejects_missing_text():
    result = ExternalCallResult(
        integration_id="openai.responses",
        status_code=200,
        response_id="resp-1",
        payload={"output": []},
    )
    with pytest.raises(ValueError, match="no text output"):
        OpenAIResponsesAdapter.response_text(result)


def test_http_error_preserves_provider_error_code_and_message(monkeypatch):
    from urllib.error import HTTPError

    from content_factory import integrations

    class FakeHttpError(HTTPError):
        def __init__(self):
            super().__init__("https://example.invalid", 429, "Too Many Requests", {}, None)

        def read(self):
            return b'{"error":{"type":"insufficient_quota","code":"credit_balance_exhausted","message":"No credits remain"}}'

    def raise_http_error(*args, **kwargs):
        raise FakeHttpError()

    monkeypatch.setenv("CF_TEST_SECRET", "test-secret")
    monkeypatch.setattr(integrations, "urlopen", raise_http_error)
    adapter = integrations.HttpJsonAdapter(
        IntegrationConfig("test", "https://example.invalid", "CF_TEST_SECRET")
    )

    with pytest.raises(
        IntegrationError,
        match=r"provider HTTP error: 429; type=insufficient_quota; code=credit_balance_exhausted; message=No credits remain",
    ):
        adapter.call({"input": "test"})
