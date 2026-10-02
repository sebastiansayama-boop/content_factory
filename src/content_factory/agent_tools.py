from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class AgentTool:
    name: str
    description: str
    owner: str
    execute: Callable[..., Any]


class AgentToolRegistry:
    """Runtime registry for bounded tools exposed to Content Factory agents."""

    def __init__(self) -> None:
        self._tools: dict[str, AgentTool] = {}

    def register(self, tool: AgentTool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"agent tool already registered: {tool.name}")
        self._tools[tool.name] = tool

    def get(self, name: str) -> AgentTool:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise ValueError(f"unknown agent tool: {name}") from exc

    def for_agent(self, owner: str) -> tuple[AgentTool, ...]:
        return tuple(tool for tool in self._tools.values() if tool.owner == owner)

    def invoke(self, name: str, *, actor: str, run_id: str, control: Any, **kwargs: Any) -> Any:
        tool = self.get(name)
        if tool.owner != actor:
            raise PermissionError(
                f"agent {actor} cannot invoke tool owned by {tool.owner}: {name}"
            )
        control.record(
            run_id,
            "agent.tool.started",
            status="RUNNING",
            actor=actor,
            evidence={"tool": name, "description": tool.description},
        )
        try:
            result = tool.execute(**kwargs)
        except Exception as exc:
            control.record(
                run_id,
                "agent.tool.failed",
                status="FAILED",
                actor=actor,
                evidence={"tool": name, "error": str(exc)},
            )
            raise
        control.record(
            run_id,
            "agent.tool.completed",
            status="COMPLETED",
            actor=actor,
            evidence={
                "tool": name,
                "result_type": type(result).__name__,
            },
        )
        return result


def register_content_tools(
    registry: AgentToolRegistry,
    *,
    service: Any,
    workspace: Any,
    reviewer: Any | None = None,
) -> None:
    """Bind real Content Factory capabilities to agent-owned tools."""

    def knowledge_search(*, run: Any) -> Any:
        return service.knowledge.search(run.brief)

    def public_research(*, run: Any) -> Any:
        from .vertical_slice import ContentFactoryVerticalSlice

        return ContentFactoryVerticalSlice(
            knowledge_store=service.knowledge
        ).run(
            run_id=run.run_id,
            brief=run.brief,
            formats=list(run.formats) or ["article", "social_post", "visual_card"],
        )

    def write_content(*, run: Any, review_feedback: list[str], knowledge: dict[str, Any] | None = None) -> Any:
        from .knowledge_content import KnowledgeContentBuilder

        return KnowledgeContentBuilder(
            workspace,
            service.knowledge,
        ).build(
            run_id=run.run_id,
            topic=run.brief,
            audience=run.audience,
            goal=run.goal,
            formats=list(run.formats),
            constraints=list(run.constraints) + list(review_feedback),
            knowledge_context=knowledge,
        )

    def review_content(*, run: Any, result: dict[str, Any]) -> Any:
        from .content_reviewer import ContentReviewer

        reviewer_impl = reviewer or ContentReviewer(workspace)
        return reviewer_impl.review(
            run_id=run.run_id,
            brief=run.brief,
            audience=run.audience,
            goal=run.goal,
            result=result,
        )

    def queue_production(*, run: Any, result: dict[str, Any]) -> Any:
        return service.asset_jobs.create_from_plan(run.run_id, result["production_plan"])

    def execute_production(*, run: Any) -> Any:
        return service.asset_executor.execute_run(run.run_id)

    def assemble_production(*, run: Any, result: dict[str, Any]) -> Any:
        from .assembly import ContentAssembler

        return ContentAssembler(
            service.asset_registry,
            service._data_dir if hasattr(service, "_data_dir") else "./data",
        ).assemble(
            run_id=run.run_id,
            script=result.get("script") or {},
            production_plan=result.get("production_plan") or {},
        )

    def quality_check(*, run: Any, result: dict[str, Any], assets: list[Any], output: dict[str, Any]) -> Any:
        from .assembly import QualityGate

        return QualityGate().evaluate(
            run_id=run.run_id,
            script=result.get("script") or {},
            production_plan=result.get("production_plan") or {},
            assets=assets,
            output=output,
        )

    registry.register(AgentTool(
        "knowledge.search", "search accepted knowledge for the current brief", "researcher", knowledge_search
    ))
    registry.register(AgentTool(
        "research.public", "research public sources and produce evidence", "researcher", public_research
    ))
    registry.register(AgentTool(
        "content.write", "write a content package from accepted knowledge", "writer", write_content
    ))
    registry.register(AgentTool(
        "content.review", "evaluate a generated content package", "reviewer", review_content
    ))
    registry.register(AgentTool(
        "production.queue", "create production jobs from the production plan", "producer", queue_production
    ))
    registry.register(AgentTool(
        "production.execute", "execute pending production jobs", "producer", execute_production
    ))
    registry.register(AgentTool(
        "production.assemble", "assemble completed assets into the output package", "producer", assemble_production
    ))
    registry.register(AgentTool(
        "quality.check", "evaluate the assembled output", "quality", quality_check
    ))
