from __future__ import annotations

from uuid import uuid4

from .n8n_adapter import N8nExecutionAdapter, N8nExecutionRequest
from .runtime import Capability, ExecutionResult, WorkItem


def n8n_execution_capability(
    adapter: N8nExecutionAdapter,
    *,
    process_id: str,
    process_revision_id: str,
    capability_id: str,
) -> Capability:
    """Bind an n8n process execution endpoint to the factory capability model."""

    def validate(item: WorkItem) -> None:
        if not item.requested_outcome.strip():
            raise ValueError("requested_outcome must not be empty")

    def execute(item: WorkItem, execution_id: str) -> ExecutionResult:
        operation_id = str(uuid4())
        result = adapter.execute(
            N8nExecutionRequest(
                operation_id=operation_id,
                work_item_id=item.work_item_id,
                revision_id=item.revision_id,
                process_id=process_id,
                process_revision_id=process_revision_id,
                capability_id=capability_id,
                requested_outcome=item.requested_outcome,
                inputs=item.inputs,
                knowledge_basis=item.knowledge_basis,
                constraints=item.constraints,
                success_signals=item.success_signals,
                authority_required=item.acceptance_criteria,
            )
        )
        if result.status != "SUCCEEDED":
            if result.failure is not None:
                raise ValueError(
                    f"n8n execution {result.status.lower()}: "
                    f"{result.failure.code}: {result.failure.message}"
                )
            raise ValueError(f"n8n execution {result.status.lower()}")
        if not result.output_revision_id:
            raise ValueError("n8n execution succeeded without output_revision_id")

        evidence = list(result.evidence_refs)
        evidence.append(f"operation:{result.operation_id}")
        evidence.append(f"n8n-execution:{result.runtime_execution_id}")
        evidence.extend(f"provider:{ref}" for ref in result.provider_refs)
        evidence.extend(
            f"agent:{run.get('agent_run_id')}"
            for run in result.agent_runs
            if isinstance(run, dict) and run.get("agent_run_id")
        )
        evidence.extend(
            f"tool:{call.get('tool_call_id')}"
            for call in result.tool_calls
            if isinstance(call, dict) and call.get("tool_call_id")
        )
        return ExecutionResult(
            execution_id=execution_id,
            capability_id=capability_id,
            output_revision_id=result.output_revision_id,
            payload=result.payload,
            evidence_refs=tuple(evidence),
        )

    return Capability(
        capability_id=capability_id,
        input_contract=validate,
        executor=execute,
        quality_requirements=("n8n execution must return a revision-bound output",),
    )
