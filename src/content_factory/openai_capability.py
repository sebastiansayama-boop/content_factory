from __future__ import annotations

from .openai_adapter import OpenAIResponsesAdapter
from .runtime import Capability, ExecutionResult, WorkItem


def openai_text_capability(
    adapter: OpenAIResponsesAdapter | None = None,
) -> Capability:
    """Bind the real OpenAI Responses adapter to the runtime capability contract."""
    provider = adapter or OpenAIResponsesAdapter()

    def validate(item: WorkItem) -> None:
        if not item.requested_outcome.strip():
            raise ValueError("requested_outcome must not be empty")

    def execute(item: WorkItem, execution_id: str) -> ExecutionResult:
        result = provider.generate(item.requested_outcome)
        if result.status_code < 200 or result.status_code >= 300:
            raise ValueError(f"provider returned HTTP {result.status_code}")
        if not result.response_id:
            raise ValueError("provider response has no response_id")
        text = provider.response_text(result)
        return ExecutionResult(
            execution_id=execution_id,
            capability_id="openai.text.generate",
            output_revision_id=f"openai-response:{result.response_id}",
            payload=text,
            evidence_refs=(result.response_id,),
        )

    return Capability(
        capability_id="openai.text.generate",
        input_contract=validate,
        executor=execute,
        quality_requirements=("provider response must contain text output",),
    )
