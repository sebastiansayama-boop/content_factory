from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable

from .agent_tools import AgentToolRegistry


@dataclass(frozen=True)
class AgentDecision:
    """One bounded decision made by a specialist."""

    tool: str
    reason: str = ""
    terminal: bool = False


@dataclass
class AgentDecisionContext:
    """Small, serializable state exposed to the decision policy."""

    agent: str
    run_id: str
    objective: str
    state: dict[str, Any]
    evidence: list[dict[str, Any]] = field(default_factory=list)
    observations: list[dict[str, Any]] = field(default_factory=list)

    def snapshot(self, tools: tuple[Any, ...]) -> dict[str, Any]:
        return {
            "agent": self.agent,
            "run_id": self.run_id,
            "objective": self.objective,
            "state": self.state,
            "evidence": self.evidence,
            "observations": self.observations,
            "available_tools": [
                {"name": tool.name, "description": tool.description}
                for tool in tools
            ],
        }


class AgentToolExecutionError(RuntimeError):
    """A bounded agent tool failed and the loop must stop with its root cause."""

    def __init__(self, *, agent: str, tool: str, cause: Exception) -> None:
        self.agent = agent
        self.tool = tool
        self.cause = cause
        super().__init__(
            f"agent {agent} tool {tool} failed: "
            f"{type(cause).__name__}: {cause}"
        )


class AgentDecisionLoop:
    """Bounded tool-selection loop for a specialist.

    The policy decides *which* owned tool should run next. Tool arguments and
    business state remain controlled by the caller, so the model cannot invent
    execution authority or bypass the registry.
    """

    def __init__(
        self,
        registry: AgentToolRegistry,
        control: Any,
        *,
        max_steps: int = 6,
    ) -> None:
        if max_steps < 1:
            raise ValueError("max_steps must be >= 1")
        self.registry = registry
        self.control = control
        self.max_steps = max_steps

    def run(
        self,
        *,
        agent: str,
        run_id: str,
        objective: str,
        state: dict[str, Any],
        decide: Callable[[AgentDecisionContext, tuple[Any, ...]], AgentDecision],
        invoke: Callable[[str, AgentDecisionContext], Any],
        evidence: list[dict[str, Any]] | None = None,
    ) -> AgentDecisionContext:
        context = AgentDecisionContext(
            agent=agent,
            run_id=run_id,
            objective=objective,
            state=dict(state),
            evidence=list(evidence or []),
        )
        tools = self.registry.for_agent(agent)
        if not tools:
            raise ValueError(f"agent {agent} has no registered tools")

        for step in range(1, self.max_steps + 1):
            decision = decide(context, tools)
            allowed = {tool.name for tool in tools}
            if decision.terminal:
                successful = next(
                    (item for item in reversed(context.observations) if "result" in item),
                    None,
                )
                if successful is None:
                    self.control.record(
                        run_id,
                        "agent.decision.rejected",
                        status="FAILED",
                        actor=agent,
                        evidence={
                            "step": step,
                            "reason": "terminal decision requires a successful tool observation",
                        },
                    )
                    continue
                self.control.record(
                    run_id,
                    "agent.decision.terminal",
                    status="COMPLETED",
                    actor=agent,
                    evidence={"step": step, "reason": decision.reason},
                )
                return context

            if decision.tool not in allowed:
                raise PermissionError(
                    f"agent {agent} selected unavailable tool: {decision.tool}"
                )

            self.control.record(
                run_id,
                "agent.decision",
                status="RUNNING",
                actor=agent,
                evidence={
                    "step": step,
                    "tool": decision.tool,
                    "reason": decision.reason,
                },
            )
            try:
                observation = invoke(decision.tool, context)
            except Exception as exc:
                observation_record = {
                    "step": step,
                    "tool": decision.tool,
                    "error": str(exc),
                    "error_type": type(exc).__name__,
                }
                context.observations.append(observation_record)
                context.state["last_tool"] = decision.tool
                context.state["last_tool_error"] = str(exc)
                self.control.record(
                    run_id,
                    "agent.observation",
                    status="FAILED",
                    actor=agent,
                    evidence=observation_record,
                )
                raise AgentToolExecutionError(
                    agent=agent,
                    tool=decision.tool,
                    cause=exc,
                ) from exc

            observation_record = {
                "step": step,
                "tool": decision.tool,
                "result_type": type(observation).__name__,
                "result": observation,
            }
            context.observations.append(observation_record)
            context.state["last_tool"] = decision.tool
            context.state["last_tool_result"] = observation

            self.control.record(
                run_id,
                "agent.observation",
                status="COMPLETED",
                actor=agent,
                evidence={
                    "step": step,
                    "tool": decision.tool,
                    "result_type": type(observation).__name__,
                },
            )

        raise RuntimeError(
            f"agent {agent} exceeded decision-loop limit of {self.max_steps}"
        )


class JsonToolDecisionPolicy:
    """Provider-backed policy with strict JSON output.

    The provider is supplied by the application. If it cannot produce a valid
    decision, the caller may fall back to a deterministic policy.
    """

    def __init__(self, generate: Callable[[str], str]) -> None:
        self.generate = generate

    def __call__(
        self,
        context: AgentDecisionContext,
        tools: tuple[Any, ...],
    ) -> AgentDecision:
        prompt = (
            "Choose exactly one next tool for a bounded specialist runtime. "
            "Return JSON only: "
            '{"tool":"tool.name","reason":"short reason","terminal":false}. '
            "Set terminal=true only when the objective is complete. "
            "Never choose a tool not listed in available_tools.\n"
            + json.dumps(context.snapshot(tools), ensure_ascii=False)
        )
        raw = self.generate(prompt)
        if not isinstance(raw, str) or not raw.strip():
            raise ValueError("agent decision provider returned empty output")
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError("agent decision provider returned invalid JSON") from exc
        if not isinstance(value, dict):
            raise ValueError("agent decision must be a JSON object")
        decision = AgentDecision(
            tool=str(value.get("tool") or "").strip(),
            reason=str(value.get("reason") or "").strip(),
            terminal=bool(value.get("terminal", False)),
        )
        if decision.terminal and not any(
            "result" in observation for observation in context.observations
        ):
            first_tool = tools[0].name
            return AgentDecision(
                first_tool,
                reason="terminal decision rejected before any successful observation; execute the first owned tool",
                terminal=False,
            )
        return decision
