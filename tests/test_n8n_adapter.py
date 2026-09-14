import pytest

from content_factory.integrations import ExternalCallResult, IntegrationError
from content_factory import n8n_adapter
from content_factory.n8n_adapter import (
    N8nExecutionAdapter,
    N8nExecutionConfig,
    N8nExecutionRequest,
)


class FakeHttpJsonAdapter:
    def __init__(self, result):
        self.result = result

    def call(self, payload):
        self.payload = payload
        return self.result


def request() -> N8nExecutionRequest:
    return N8nExecutionRequest(
        operation_id="op-1",
        work_item_id="wi-1",
        revision_id="r1",
        process_id="content.research.v1",
        process_revision_id="pr-1",
        capability_id="research.web.agent",
        requested_outcome="Research the topic",
        inputs=("input-a",),
        knowledge_basis=("source-a",),
        constraints=("no unsupported claims",),
        success_signals=("evidence-backed",),
        authority_required=("human.accept",),
        authority_grants=(),
    )


def test_request_payload_has_factory_identity_and_authority_context():
    payload = request().as_payload()

    assert payload["contract_version"] == "n8n.execution.v0"
    assert payload["operation_id"] == "op-1"
    assert payload["work_item_id"] == "wi-1"
    assert payload["process_id"] == "content.research.v1"
    assert payload["authority_context"] == {
        "required": ["human.accept"],
        "grants": [],
    }


def test_adapter_normalizes_success_and_preserves_runtime_identity(monkeypatch):
    response = ExternalCallResult(
        integration_id="n8n.execution",
        status_code=200,
        response_id=None,
        payload={
            "contract_version": "n8n.execution.v0",
            "operation_id": "op-1",
            "work_item_id": "wi-1",
            "revision_id": "r1",
            "execution": {
                "runtime_execution_id": "n8n-42",
                "status": "SUCCEEDED",
                "started_at": "2026-09-14T00:00:00Z",
                "completed_at": "2026-09-14T00:00:02Z",
            },
            "output": {
                "output_revision_id": "out-r2",
                "payload": "research result",
                "evidence_refs": ["e1"],
            },
            "provider_refs": ["provider-1"],
            "tool_calls": [{"tool_call_id": "tool-1"}],
            "agent_runs": [{"agent_run_id": "agent-1"}],
            "failure": None,
        },
    )

    monkeypatch.setattr(
        n8n_adapter,
        "HttpJsonAdapter",
        lambda config: FakeHttpJsonAdapter(response),
    )
    adapter = N8nExecutionAdapter(N8nExecutionConfig("https://n8n.example/webhook/factory"))

    result = adapter.execute(request())

    assert result.operation_id == "op-1"
    assert result.runtime_execution_id == "n8n-42"
    assert result.output_revision_id == "out-r2"
    assert result.payload == "research result"
    assert result.evidence_refs == ("e1",)
    assert result.provider_refs == ("provider-1",)


def test_adapter_rejects_identity_mismatch(monkeypatch):
    response = ExternalCallResult(
        integration_id="n8n.execution",
        status_code=200,
        response_id=None,
        payload={
            "contract_version": "n8n.execution.v0",
            "operation_id": "op-other",
            "work_item_id": "wi-1",
            "revision_id": "r1",
            "execution": {"runtime_execution_id": "n8n-42", "status": "SUCCEEDED"},
            "output": {"output_revision_id": "out-r2", "payload": "ok"},
        },
    )
    monkeypatch.setattr(
        n8n_adapter,
        "HttpJsonAdapter",
        lambda config: FakeHttpJsonAdapter(response),
    )
    adapter = N8nExecutionAdapter(N8nExecutionConfig("https://n8n.example/webhook/factory"))

    with pytest.raises(IntegrationError, match="operation_id mismatch"):
        adapter.execute(request())


def test_adapter_preserves_structured_failure_without_secrets(monkeypatch):
    response = ExternalCallResult(
        integration_id="n8n.execution",
        status_code=200,
        response_id=None,
        payload={
            "contract_version": "n8n.execution.v0",
            "operation_id": "op-1",
            "work_item_id": "wi-1",
            "revision_id": "r1",
            "execution": {"runtime_execution_id": "n8n-43", "status": "FAILED"},
            "output": {"output_revision_id": None},
            "failure": {
                "code": "tool_failed",
                "message": "Provider unavailable",
                "details": {"provider": "example"},
            },
        },
    )
    monkeypatch.setattr(
        n8n_adapter,
        "HttpJsonAdapter",
        lambda config: FakeHttpJsonAdapter(response),
    )
    adapter = N8nExecutionAdapter(N8nExecutionConfig("https://n8n.example/webhook/factory"))

    result = adapter.execute(request())

    assert result.status == "FAILED"
    assert result.failure is not None
    assert result.failure.code == "tool_failed"
    assert result.failure.message == "Provider unavailable"
