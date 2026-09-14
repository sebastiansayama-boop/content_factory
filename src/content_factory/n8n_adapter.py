from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .integrations import ExternalCallResult, HttpJsonAdapter, IntegrationConfig, IntegrationError


@dataclass(frozen=True)
class N8nExecutionConfig:
    endpoint: str
    secret_env: str | None = None


@dataclass(frozen=True)
class N8nExecutionRequest:
    operation_id: str
    work_item_id: str
    revision_id: str
    process_id: str
    process_revision_id: str
    capability_id: str
    requested_outcome: str
    inputs: tuple[str, ...] = ()
    knowledge_basis: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()
    success_signals: tuple[str, ...] = ()
    authority_required: tuple[str, ...] = ()
    authority_grants: tuple[str, ...] = ()

    def as_payload(self) -> dict[str, Any]:
        return {
            "contract_version": "n8n.execution.v0",
            "operation_id": self.operation_id,
            "work_item_id": self.work_item_id,
            "revision_id": self.revision_id,
            "process_id": self.process_id,
            "process_revision_id": self.process_revision_id,
            "capability_id": self.capability_id,
            "requested_outcome": self.requested_outcome,
            "inputs": list(self.inputs),
            "knowledge_basis": list(self.knowledge_basis),
            "constraints": list(self.constraints),
            "success_signals": list(self.success_signals),
            "authority_context": {
                "required": list(self.authority_required),
                "grants": list(self.authority_grants),
            },
        }


@dataclass(frozen=True)
class N8nFailure:
    code: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class N8nExecutionResult:
    operation_id: str
    work_item_id: str
    revision_id: str
    runtime_execution_id: str
    status: str
    output_revision_id: str | None
    payload: Any = None
    evidence_refs: tuple[str, ...] = ()
    provider_refs: tuple[str, ...] = ()
    tool_calls: tuple[dict[str, Any], ...] = ()
    agent_runs: tuple[dict[str, Any], ...] = ()
    started_at: str | None = None
    completed_at: str | None = None
    failure: N8nFailure | None = None


class N8nExecutionAdapter:
    """Factory-facing adapter for an n8n execution endpoint.

    n8n is treated as an execution substrate. The factory contract remains
    provider-neutral and owns operation identity, semantic state and approval.
    """

    def __init__(self, config: N8nExecutionConfig) -> None:
        self.config = config
        self._adapter = HttpJsonAdapter(
            IntegrationConfig("n8n.execution", config.endpoint, config.secret_env)
        )

    def execute(self, request: N8nExecutionRequest) -> N8nExecutionResult:
        result = self._adapter.call(request.as_payload())
        return self._normalize(result, request)

    @staticmethod
    def _normalize(result: ExternalCallResult, request: N8nExecutionRequest) -> N8nExecutionResult:
        if not isinstance(result.payload, dict):
            raise IntegrationError("n8n execution response must be a JSON object")
        body = result.payload
        contract_version = body.get("contract_version")
        if contract_version != "n8n.execution.v0":
            raise IntegrationError("unsupported n8n execution contract version")

        operation_id = body.get("operation_id")
        work_item_id = body.get("work_item_id")
        revision_id = body.get("revision_id")
        execution = body.get("execution")
        if not isinstance(execution, dict):
            raise IntegrationError("n8n execution response missing execution object")

        if operation_id != request.operation_id:
            raise IntegrationError("n8n response operation_id mismatch")
        if work_item_id != request.work_item_id:
            raise IntegrationError("n8n response work_item_id mismatch")
        if revision_id != request.revision_id:
            raise IntegrationError("n8n response revision_id mismatch")

        runtime_execution_id = execution.get("runtime_execution_id")
        status = execution.get("status")
        if not isinstance(runtime_execution_id, str) or not runtime_execution_id:
            raise IntegrationError("n8n execution response missing runtime_execution_id")
        if status not in {"SUCCEEDED", "FAILED", "UNKNOWN", "CANCELLED"}:
            raise IntegrationError("n8n execution response has unsupported status")

        output = body.get("output")
        if output is not None and not isinstance(output, dict):
            raise IntegrationError("n8n execution output must be an object")
        output = output or {}

        failure = None
        raw_failure = body.get("failure")
        if raw_failure is not None:
            if not isinstance(raw_failure, dict):
                raise IntegrationError("n8n failure must be an object")
            code = raw_failure.get("code")
            message = raw_failure.get("message")
            if not isinstance(code, str) or not isinstance(message, str):
                raise IntegrationError("n8n failure requires code and message")
            failure = N8nFailure(code=code, message=message, details=raw_failure.get("details", {}))

        return N8nExecutionResult(
            operation_id=operation_id,
            work_item_id=work_item_id,
            revision_id=revision_id,
            runtime_execution_id=runtime_execution_id,
            status=status,
            output_revision_id=output.get("output_revision_id"),
            payload=output.get("payload"),
            evidence_refs=tuple(map(str, output.get("evidence_refs", []))),
            provider_refs=tuple(map(str, body.get("provider_refs", []))),
            tool_calls=tuple(body.get("tool_calls", [])),
            agent_runs=tuple(body.get("agent_runs", [])),
            started_at=execution.get("started_at"),
            completed_at=execution.get("completed_at"),
            failure=failure,
        )
