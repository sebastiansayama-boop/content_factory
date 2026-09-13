import os

import pytest

from content_factory.integrations import ExternalCallResult, IntegrationConfig, IntegrationError
from content_factory.openai_adapter import OpenAIResponsesAdapter, OpenAIResponsesConfig
from content_factory.runtime import WorkItem


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


def test_openai_execute_maps_provider_response_to_execution_result(monkeypatch):
    monkeypatch.setenv("CF_TEST_SECRET", "test-secret")
    adapter = OpenAIResponsesAdapter(
        OpenAIResponsesConfig(
            model="test-model",
            endpoint="https://example.invalid/v1/responses",
            secret_env="CF_TEST_SECRET",
        )
    )
    monkeypatch.setattr(
        adapter,
        "generate",
        lambda _: ExternalCallResult(
            integration_id="openai.responses",
            status_code=200,
            response_id="resp-123",
            payload={"output": [{"content": [{"text": "generated"}]}]},
        ),
    )
    item = WorkItem(
        work_item_id="wi-openai",
        revision_id="spec-r1",
        objective="generate text",
        requested_outcome="generate a short test text",
        inputs=(),
        knowledge_basis=(),
        required_capabilities=("openai.responses.text_generation",),
        owner="test",
        acceptance_criteria=("has text",),
        release_requirements=(),
    )

    execution = adapter.execute(item, "exec-123")

    assert execution.execution_id == "exec-123"
    assert execution.capability_id == "openai.responses.text_generation"
    assert execution.output_revision_id == "resp-123:output"
    assert execution.payload == "generated"
    assert execution.evidence_refs == ("provider:resp-123",)
