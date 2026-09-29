from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .agent_decision import AgentDecision, AgentDecisionContext, AgentDecisionLoop
from .agent_tools import AgentToolRegistry


@dataclass(frozen=True)
class AgentSpec:
    """A bounded specialist in the Content Factory control plane."""

    name: str
    responsibility: str
    input_stage: str
    output_stage: str
    authority: str
    capabilities: tuple[str, ...]


@dataclass(frozen=True)
class AgentInvocation:
    agent: str
    stage: str
    run_id: str
    operation: str


class ContentAgentOS:
    """Small manager-style agent OS for the Content Factory.

    The manager owns the user-facing run. Specialists are bounded capabilities;
    they do not mutate workflow state outside their declared stage. This keeps
    agent boundaries explicit without introducing a second orchestration engine.
    """

    STAGES = (
        "PLANNING",
        "RESEARCH",
        "WRITING",
        "REVIEW",
        "PRODUCTION",
        "QC",
    )

    def __init__(self, control: Any, tools: AgentToolRegistry | None = None) -> None:
        self.control = control
        self.tools = tools or AgentToolRegistry()
        self.agents = {
            "planner": AgentSpec(
                "planner",
                "turn a user brief into an executable content plan",
                "DRAFT",
                "PLANNING",
                "plan",
                ("content_run.plan",),
            ),
            "researcher": AgentSpec(
                "researcher",
                "retrieve and validate evidence for the brief",
                "PLANNING",
                "RESEARCH",
                "read",
                ("research.public_sources", "knowledge.accept"),
            ),
            "writer": AgentSpec(
                "writer",
                "produce an editorial draft grounded in accepted knowledge",
                "RESEARCH",
                "WRITING",
                "write",
                ("content.write",),
            ),
            "reviewer": AgentSpec(
                "reviewer",
                "independently evaluate the draft and request bounded corrections",
                "WRITING",
                "REVIEW",
                "review",
                ("content.review",),
            ),
            "producer": AgentSpec(
                "producer",
                "materialize the approved draft into assets and a package",
                "REVIEW",
                "PRODUCTION",
                "execute",
                ("asset.create", "asset.execute", "assembly"),
            ),
            "quality": AgentSpec(
                "quality",
                "verify the produced package before it is exposed as ready",
                "PRODUCTION",
                "QC",
                "verify",
                ("quality_gate",),
            ),
        }

    def available_tools(self, name: str) -> tuple[Any, ...]:
        return self.tools.for_agent(name)

    def invoke_tool(self, *, name: str, tool: str, run_id: str, **kwargs: Any) -> Any:
        return self.tools.invoke(tool, actor=name, run_id=run_id, control=self.control, **kwargs)

    def available_tools(self, name: str) -> tuple[Any, ...]:
        return self.tools.for_agent(name)

    def invoke_tool(self, *, name: str, tool: str, run_id: str, **kwargs: Any) -> Any:
        return self.tools.invoke(tool, actor=name, run_id=run_id, control=self.control, **kwargs)

    def decision_loop(self, *, max_steps: int = 6) -> AgentDecisionLoop:
        return AgentDecisionLoop(self.tools, self.control, max_steps=max_steps)

    def run_decision_loop(
        self,
        *,
        name: str,
        run_id: str,
        objective: str,
        state: dict[str, Any],
        decide: Callable[[AgentDecisionContext, tuple[Any, ...]], AgentDecision],
        invoke: Callable[[str, AgentDecisionContext], Any],
        evidence: list[dict[str, Any]] | None = None,
        max_steps: int = 6,
    ) -> AgentDecisionContext:
        return self.decision_loop(max_steps=max_steps).run(
            agent=name,
            run_id=run_id,
            objective=objective,
            state=state,
            decide=decide,
            invoke=invoke,
            evidence=evidence,
        )

    def spec(self, name: str) -> AgentSpec:
        try:
            return self.agents[name]
        except KeyError as exc:
            raise ValueError(f"unknown content agent: {name}") from exc

    def begin(self, *, name: str, run_id: str, operation: str) -> AgentInvocation:
        spec = self.spec(name)
        self.control.record(
            run_id,
            "agent.started",
            status="RUNNING",
            actor=spec.name,
            evidence={
                "agent": spec.name,
                "stage": spec.output_stage,
                "responsibility": spec.responsibility,
                "authority": spec.authority,
                "capabilities": list(spec.capabilities),
                "operation": operation,
            },
        )
        return AgentInvocation(
            agent=spec.name,
            stage=spec.output_stage,
            run_id=run_id,
            operation=operation,
        )

    def complete(self, invocation: AgentInvocation, *, evidence: dict[str, Any] | None = None) -> None:
        self.control.record(
            invocation.run_id,
            "agent.completed",
            status="COMPLETED",
            actor=invocation.agent,
            evidence={
                "agent": invocation.agent,
                "stage": invocation.stage,
                "operation": invocation.operation,
                **(evidence or {}),
            },
        )

    def fail(self, invocation: AgentInvocation, *, error: str) -> None:
        self.control.record(
            invocation.run_id,
            "agent.failed",
            status="FAILED",
            actor=invocation.agent,
            evidence={
                "agent": invocation.agent,
                "stage": invocation.stage,
                "operation": invocation.operation,
                "error": error,
            },
        )


class AgentManager:
    """Deterministic manager that maps lifecycle state to one specialist."""

    STAGE_TO_AGENT = {
        "PLANNING": "planner",
        "RESEARCHING": "researcher",
        "RESEARCH_READY": "writer",
        "REVIEW": "reviewer",
        "PRODUCING": "producer",
        "READY_FOR_REVIEW": "quality",
    }

    def __init__(self, agent_os: ContentAgentOS) -> None:
        self.agent_os = agent_os

    def select(self, stage: str) -> AgentSpec:
        name = self.STAGE_TO_AGENT.get(stage)
        if name is None:
            raise ValueError(f"no agent mapped to stage: {stage}")
        return self.agent_os.spec(name)

    def run(
        self,
        *,
        name: str,
        run_id: str,
        operation: str,
        action: Callable[[], Any],
    ) -> Any:
        invocation = self.agent_os.begin(name=name, run_id=run_id, operation=operation)
        try:
            result = action()
        except Exception as exc:
            self.agent_os.fail(invocation, error=str(exc))
            raise
        self.agent_os.complete(invocation)
        return result
