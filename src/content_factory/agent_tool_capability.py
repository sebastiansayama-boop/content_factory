from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .agent_tools import AgentToolRegistry
from .runtime import Capability, ExecutionResult, WorkItem


@dataclass(frozen=True)
class AgentToolCapabilitySpec:
    """Maps one registered AgentTool directly into a Runtime capability."""

    capability_id: str
    tool_name: str
    actor: str
    build_kwargs: Callable[[WorkItem, Any], dict[str, Any]]


def register_agent_tool_capabilities(
    runtime: Any,
    registry: AgentToolRegistry,
    *,
    run_loader: Callable[[str], Any],
    control: Any,
    specs: tuple[AgentToolCapabilitySpec, ...],
) -> None:
    """Expose existing AgentTools to FactoryRuntime without duplicating their logic.

    Runtime owns lifecycle/execution identity. AgentToolRegistry remains the
    owner of tool authorization and the actual factory operation.
    """

    for spec in specs:
        if spec.capability_id in runtime.capabilities:
            raise ValueError(f"runtime capability already registered: {spec.capability_id}")

        def execute(
            item: WorkItem,
            execution_id: str,
            *,
            _spec: AgentToolCapabilitySpec = spec,
        ) -> ExecutionResult:
            run = run_loader(item.work_item_id)
            if run is None:
                raise ValueError(f"content run not found: {item.work_item_id}")
            kwargs = _spec.build_kwargs(item, run)
            payload = registry.invoke(
                _spec.tool_name,
                actor=_spec.actor,
                run_id=run.run_id,
                control=control,
                **kwargs,
            )
            return ExecutionResult(
                execution_id=execution_id,
                capability_id=_spec.capability_id,
                output_revision_id=f"{item.revision_id}:execution",
                payload=payload,
            )

        runtime.register_capability(
            Capability(
                capability_id=spec.capability_id,
                input_contract=lambda item: None,
                executor=execute,
            )
        )


def content_tool_capability_specs() -> tuple[AgentToolCapabilitySpec, ...]:
    """Minimal production mapping for currently bounded content tools."""

    return (
        AgentToolCapabilitySpec(
            capability_id="knowledge.search",
            tool_name="knowledge.search",
            actor="researcher",
            build_kwargs=lambda item, run: {"run": run},
        ),
        AgentToolCapabilitySpec(
            capability_id="content.write",
            tool_name="content.write",
            actor="writer",
            build_kwargs=lambda item, run: {"run": run, "review_feedback": [], "knowledge": _previous_payload(item), "previous_result": run.result if isinstance(run.result, dict) else None},
        ),
        AgentToolCapabilitySpec(
            capability_id="content.review",
            tool_name="content.review",
            actor="reviewer",
            build_kwargs=lambda item, run: {"run": run, "result": _previous_payload(item)},
        ),
    )


def _previous_payload(item: WorkItem) -> dict[str, Any]:
    prefix = "capability_input:"
    for value in reversed(item.inputs):
        if value.startswith(prefix):
            import json

            payload = json.loads(value[len(prefix):])
            if isinstance(payload, dict):
                return payload
            return {"input": payload}
    return {}
