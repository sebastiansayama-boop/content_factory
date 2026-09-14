from __future__ import annotations

from collections.abc import Callable

from .integrations import ExternalCallResult
from .runtime import Capability, ExecutionResult, WorkItem


ProviderAdapter = object


def text_generation_capability(
    *,
    capability_id: str,
    provider: object,
    generate: Callable[[str], ExternalCallResult],
    response_text: Callable[[ExternalCallResult], str],
) -> Capability:
    """Bind any text provider to the factory's stable capability contract."""

    def validate(item: WorkItem) -> None:
        if not item.requested_outcome.strip():
            raise ValueError("requested_outcome must not be empty")

    def execute(item: WorkItem, execution_id: str) -> ExecutionResult:
        result = generate(item.requested_outcome)
        if result.status_code < 200 or result.status_code >= 300:
            raise ValueError(f"provider returned HTTP {result.status_code}")
        if not result.response_id:
            raise ValueError("provider response has no response_id")
        text = response_text(result)
        return ExecutionResult(
            execution_id=execution_id,
            capability_id=capability_id,
            output_revision_id=f"{capability_id}:{result.response_id}",
            payload=text,
            evidence_refs=(result.response_id,),
        )

    return Capability(
        capability_id=capability_id,
        input_contract=validate,
        executor=execute,
        quality_requirements=("provider response must contain text output",),
    )
