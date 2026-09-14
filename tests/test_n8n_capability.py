import pytest

from content_factory.n8n_adapter import N8nExecutionResult, N8nFailure
from content_factory.n8n_capability import n8n_execution_capability
from content_factory.runtime import WorkItem


class FakeN8nAdapter:
    def __init__(self, result):
        self.result = result
        self.request = None

    def execute(self, request):
        self.request = request
        return self.result


def item():
    return WorkItem(
        work_item_id="wi-1",
        revision_id="r1",
        objective="research",
        requested_outcome="Produce a bounded research result",
        inputs=("input-1",),
        knowledge_basis=("source-1",),
        required_capabilities=("research.web.agent",),
        owner="factory",
        acceptance_criteria=("human.accept",),
        release_requirements=("human.release",),
        constraints=("no unsupported claims",),
        success_signals=("evidence-backed",),
    )


def test_capability_maps_succeeded_n8n_execution_to_factory_result():
    adapter = FakeN8nAdapter(
        N8nExecutionResult(
            operation_id="op-1",
            work_item_id="wi-1",
            revision_id="r1",
            runtime_execution_id="n8n-1",
            status="SUCCEEDED",
            output_revision_id="out-r2",
            payload={"result": "research"},
            evidence_refs=("e1",),
            provider_refs=("openai-response-1",),
            tool_calls=({"tool_call_id": "tool-1"},),
            agent_runs=({"agent_run_id": "agent-1"},),
        )
    )

    capability = n8n_execution_capability(
        adapter,
        process_id="content.research.v1",
        process_revision_id="pr-1",
        capability_id="research.web.agent",
    )

    result = capability.executor(item(), "factory-exec-1")

    assert result.execution_id == "factory-exec-1"
    assert result.output_revision_id == "out-r2"
    assert "operation:op-1" in result.evidence_refs
    assert "n8n-execution:n8n-1" in result.evidence_refs
    assert "provider:openai-response-1" in result.evidence_refs
    assert "agent:agent-1" in result.evidence_refs
    assert "tool:tool-1" in result.evidence_refs
    assert adapter.request.operation_id == "op-1"
    assert adapter.request.work_item_id == "wi-1"
    assert adapter.request.process_id == "content.research.v1"


def test_capability_fails_closed_on_n8n_failure():
    adapter = FakeN8nAdapter(
        N8nExecutionResult(
            operation_id="op-2",
            work_item_id="wi-1",
            revision_id="r1",
            runtime_execution_id="n8n-2",
            status="FAILED",
            output_revision_id=None,
            failure=N8nFailure("tool_failed", "Provider unavailable"),
        )
    )
    capability = n8n_execution_capability(
        adapter,
        process_id="content.research.v1",
        process_revision_id="pr-1",
        capability_id="research.web.agent",
    )

    with pytest.raises(ValueError, match="n8n execution failed: tool_failed: Provider unavailable"):
        capability.executor(item(), "factory-exec-2")
