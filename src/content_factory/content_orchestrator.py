from __future__ import annotations

import os
from typing import Any

from .agent_decision import AgentDecision, JsonToolDecisionPolicy
from .agent_os import AgentManager, ContentAgentOS
from .gemini_adapter import GeminiOpenAICompatibleAdapter
from .openai_adapter import OpenAIResponsesAdapter
from .agent_tools import AgentToolRegistry, register_content_tools
from .assembly import ContentAssembler, QualityGate
from .content_reviewer import ContentReviewer
from .content_run import ContentRun, ContentRunStore
from .content_run_planner import ContentRunPlanner
from .knowledge_content import KnowledgeContentBuilder
from .vertical_slice import ContentFactoryVerticalSlice


class ContentOrchestrator:
    """Own the product-level ContentRun lifecycle.

    HTTP handlers only adapt requests/responses. This class owns the
    deterministic sequence and the bounded WRITE -> REVIEW -> REVISE/PASS loop.
    """

    MAX_REVISIONS = 2

    def __init__(
        self,
        *,
        service: Any,
        workspace: Any,
        content_runs: ContentRunStore,
        planner: ContentRunPlanner | None = None,
        reviewer: ContentReviewer | None = None,
    ) -> None:
        self.service = service
        self.workspace = workspace
        self.content_runs = content_runs
        self.planner = planner or ContentRunPlanner(workspace)
        self.reviewer = reviewer or ContentReviewer(workspace)
        self.tool_registry = AgentToolRegistry()
        register_content_tools(
            self.tool_registry,
            service=service,
            workspace=workspace,
            reviewer=self.reviewer,
        )
        self.agent_os = ContentAgentOS(service.control, self.tool_registry)
        self.agent_manager = AgentManager(self.agent_os)
        self._decision_policy = self._build_decision_policy()

    def _build_decision_policy(self):
        provider = os.environ.get("FACTORY_AGENT_DECISION_PROVIDER", "local").strip().lower()
        if provider == "openai" and os.environ.get("OPENAI_API_KEY", "").strip():
            adapter = OpenAIResponsesAdapter()
            return JsonToolDecisionPolicy(lambda prompt: adapter.response_text(adapter.generate(prompt)))
        if provider == "gemini" and os.environ.get("GEMINI_API_KEY", "").strip():
            adapter = GeminiOpenAICompatibleAdapter()
            return JsonToolDecisionPolicy(lambda prompt: adapter.response_text(adapter.generate(prompt)))
        return self._deterministic_decision

    @staticmethod
    def _deterministic_decision(context, tools):
        names = [tool.name for tool in tools]
        observations = context.observations
        if context.agent == "planner":
            if not observations:
                return AgentDecision("content_run.plan", reason="turn the brief into an executable content plan")
            if observations[-1].get("tool") == "content_run.plan" and "result" in observations[-1]:
                return AgentDecision("", reason="content plan created", terminal=True)
            return AgentDecision("content_run.plan", reason="retry planning after unsuccessful observation")
        if context.agent == "researcher":
            if not observations:
                return AgentDecision("knowledge.search", reason="check existing accepted knowledge")
            first = observations[0].get("result")
            if observations[-1]["tool"] == "knowledge.search":
                if isinstance(first, dict) and first.get("claims"):
                    return AgentDecision("", reason="accepted knowledge is sufficient", terminal=True)
                return AgentDecision("research.public", reason="no accepted knowledge; research public sources")
            return AgentDecision("", reason="research observation collected", terminal=True)
        if context.agent == "producer":
            sequence = ["production.queue", "production.execute", "production.assemble"]
            for tool in sequence:
                if tool in names and not any(item["tool"] == tool for item in observations):
                    return AgentDecision(tool, reason=f"continue production with {tool}")
            return AgentDecision("", reason="production package assembled", terminal=True)
        if not observations and names:
            return AgentDecision(names[0], reason="perform the specialist action")
        return AgentDecision("", reason="specialist objective complete", terminal=True)

    def _run_agent_loop(self, *, agent, run, objective, state, invoke):
        evidence = [event.to_dict() for event in self.service.control.timeline(run.run_id)[-12:]]
        return self.agent_os.run_decision_loop(
            name=agent,
            run_id=run.run_id,
            objective=objective,
            state=state,
            evidence=evidence,
            decide=self._decision_policy,
            invoke=invoke,
        )

    @staticmethod
    def _last_observation_result(context) -> Any:
        for observation in reversed(context.observations):
            if "result" in observation:
                return observation["result"]
            if "error" in observation:
                raise RuntimeError(
                    f"agent {context.agent} tool {observation.get('tool')} failed: "
                    f"{observation['error']}"
                )
        raise RuntimeError(
            f"agent {context.agent} completed without a successful tool observation"
        )

    def _research(self, run: ContentRun) -> ContentRun:
        def invoke(tool, context):
            current = self.content_runs.get(run.run_id) or run
            result = self.agent_os.invoke_tool(
                name="researcher", tool=tool, run_id=run.run_id, run=current
            )
            if tool == "research.public":
                if current.status in {"DRAFT", "FAILED", "PLANNING"}:
                    self.content_runs.start_execution(run.run_id)
                research_dict = ContentFactoryVerticalSlice.to_dict(result)
                self.content_runs.save_research_result(run.run_id, research_dict)

                # A factory run is an explicit production request, so the
                # research it just validated becomes reusable knowledge for
                # this run. Promotion is still explicit and auditable; it is
                # never performed by KnowledgeStore.capture().
                knowledge_refs = (research_dict.get("research") or {}).get("knowledge_refs") or {}
                promoted_claims = []
                for claim_id in (knowledge_refs.get("claims") or {}).values():
                    claim = self.service.knowledge.promote_claim(
                        str(claim_id),
                        decision_ref=f"factory-research-qc:{run.run_id}",
                    )
                    promoted_claims.append(claim.claim_id)

                self.service.control.record(
                    run.run_id, "research.completed", status="COMPLETED", actor="researcher",
                    evidence={
                        "claims": len(research_dict.get("claims") or []),
                        "sources": len(research_dict.get("sources") or []),
                        "promoted_claims": len(promoted_claims),
                        "decision_ref": f"factory-research-qc:{run.run_id}",
                    },
                )
            return result

        context = self._run_agent_loop(
            agent="researcher", run=run, objective="obtain sufficient evidence for the content brief",
            state=run.to_dict(), invoke=invoke,
        )
        if context.observations and context.observations[0]["tool"] == "knowledge.search":
            prior = context.observations[0]["result"]
            if isinstance(prior, dict) and prior.get("claims"):
                self.service.control.record(run.run_id, "research.reused_knowledge", status="COMPLETED", actor="researcher", evidence={"claims": len(prior["claims"])})
        saved = self.content_runs.get(run.run_id)
        if saved is None:
            raise ValueError("content run not found after research")
        return saved

    def _write(self, run: ContentRun, *, review_feedback: list[str] | None = None) -> dict[str, Any]:
        return self.agent_os.invoke_tool(
            name="writer",
            tool="content.write",
            run_id=run.run_id,
            run=run,
            review_feedback=list(review_feedback or ()),
        )

    def _production(self, run_id: str, result: dict[str, Any]) -> tuple[ContentRun, dict[str, Any]]:
        run = self.content_runs.get(run_id)
        if run is None:
            raise ValueError("content run not found")
        self.content_runs.start_producing(run_id)
        observations: dict[str, Any] = {}

        def invoke(tool, context):
            current = self.content_runs.get(run_id)
            if current is None:
                raise ValueError("content run disappeared during production")
            if tool == "production.queue":
                value = self.agent_os.invoke_tool(name="producer", tool=tool, run_id=run_id, run=current, result=result)
                observations[tool] = value
                self.content_runs.save_production_result(
                    run_id,
                    {**(current.result or {}), "production": {"status": "QUEUED", "job_ids": [j.job_id for j in value]}},
                )
                self.service.control.record(run_id, "production.queued", output_refs=tuple(j.job_id for j in value))
                return value
            if tool == "production.execute":
                value = self.agent_os.invoke_tool(name="producer", tool=tool, run_id=run_id, run=current)
                observations[tool] = value
                jobs = value
                self.content_runs.save_production_result(
                    run_id,
                    {**(current.result or {}), "production": {"status": "COMPLETED", "jobs": [j.to_dict() for j in jobs]}},
                )
                self.service.control.record(run_id, "production.completed", output_refs=tuple(j.job_id for j in jobs))
                return value
            if tool == "production.assemble":
                # Assembly reads the durable AssetRegistry. Register completed
                # executor jobs before invoking the assembler, not after it.
                jobs = observations.get("production.execute", [])
                assets = [self.service.asset_registry.register_completed_job(j).to_dict() for j in jobs]
                value = self.agent_os.invoke_tool(name="producer", tool=tool, run_id=run_id, run=current, result=current.result or result)
                observations[tool] = value
                self.content_runs.save_production_result(
                    run_id,
                    {**(current.result or {}), "production": {"status": "ASSEMBLED", "jobs": [j.to_dict() for j in jobs], "assets": assets, "output": value}},
                )
                self.service.control.record(run_id, "assembly.completed", output_refs=(value["output_id"],))
                return value
            raise ValueError(f"producer selected unsupported tool: {tool}")

        self._run_agent_loop(
            agent="producer",
            run=run,
            objective="materialize the approved content package into production assets and an assembled output",
            state={**run.to_dict(), "result": result},
            invoke=invoke,
        )
        final_run = self.content_runs.get(run_id)
        if final_run is None:
            raise ValueError("content run not found after production")
        output = observations.get("production.assemble")
        if not isinstance(output, dict):
            raise ValueError("producer did not assemble an output")
        return final_run, output

    def run(self, run_id: str) -> tuple[ContentRun, dict[str, Any]]:
        run = self.content_runs.get(run_id)
        if run is None:
            raise ValueError("content run not found")

        if run.status in {"DRAFT", "RESEARCH_READY"}:
            self.content_runs.start_planning(run_id)
            run = self.content_runs.get(run_id)
            if run is None:
                raise ValueError("content run disappeared during planning")

        self.service.control.record(run_id, "factory.started", status="RUNNING", actor="orchestrator")
        if run.status == "PLANNING" and not run.plan:
            planner_context = self._run_agent_loop(
                agent="planner",
                run=run,
                objective="turn the user brief into an executable content plan",
                state=run.to_dict(),
                invoke=lambda tool, context: self.agent_os.invoke_tool(
                    name="planner", tool=tool, run_id=run_id, run=run
                ),
            )
            plan = self._last_observation_result(planner_context)
            self.content_runs.save_plan(run_id, plan)
            self.service.control.record(run_id, "planning.completed", status="COMPLETED", actor="planner")
        run = self.content_runs.get(run_id)
        if run is None:
            raise ValueError("content run not found after planning")
        run = self.agent_manager.run(
            name="researcher",
            run_id=run_id,
            operation="research",
            action=lambda: self._research(run),
        )

        review_history: list[dict[str, Any]] = []
        result: dict[str, Any] | None = None

        for revision in range(self.MAX_REVISIONS + 1):
            run = self.content_runs.get(run_id)
            if run is None:
                raise ValueError("content run not found before write")
            feedback = review_history[-1].get("required_changes", []) if review_history else []
            writer_context = self._run_agent_loop(
                agent="writer",
                run=run,
                objective="produce the requested content package",
                state={**run.to_dict(), "review_feedback": feedback},
                invoke=lambda tool, context: self.agent_os.invoke_tool(
                    name="writer", tool=tool, run_id=run_id, run=run, review_feedback=feedback
                ),
            )
            result = self._last_observation_result(writer_context)
            self.content_runs.save_result(run_id, {"run_id": run_id, "brief": run.brief, **result})
            self.service.control.record(
                run_id,
                "content.written",
                status="COMPLETED",
                actor="writer",
                evidence={"revision": revision},
            )

            reviewer_context = self._run_agent_loop(
                agent="reviewer",
                run=run,
                objective="evaluate the current content package and decide whether it is acceptable",
                state={**run.to_dict(), "candidate_result": result},
                invoke=lambda tool, context: self.agent_os.invoke_tool(
                    name="reviewer", tool=tool, run_id=run_id, run=run, result=result
                ),
            )
            review = self._last_observation_result(reviewer_context)
            review["revision"] = revision
            review_history.append(review)
            self.content_runs.save_result(
                run_id,
                {
                    "run_id": run_id,
                    "brief": run.brief,
                    **result,
                    "review": review,
                    "review_history": review_history,
                },
            )
            self.service.control.record(
                run_id,
                f"content.review.{review['status'].lower()}",
                status=review["status"],
                actor="content-reviewer",
                evidence=review,
            )

            if review["status"] == "PASS":
                break
            if review["status"] == "FAIL":
                raise ValueError("content reviewer returned FAIL")
            if revision >= self.MAX_REVISIONS:
                raise ValueError("content reviewer requested more revisions than allowed")

        assert result is not None
        run = self.content_runs.get(run_id)
        if run is None:
            raise ValueError("content run not found after review")
        result_with_review = dict(run.result or {})
        result_with_review["review_history"] = review_history
        run = self.content_runs.save_result(run_id, result_with_review)
        produced_run, output = self._production(run_id, result_with_review)
        quality_context = self._run_agent_loop(
            agent="quality",
            run=produced_run,
            objective="verify the assembled output before exposing it as ready",
            state={**produced_run.to_dict(), "output": output},
            invoke=lambda tool, context: self.agent_os.invoke_tool(
                name="quality",
                tool=tool,
                run_id=run_id,
                run=produced_run,
                result=produced_run.result or {},
                assets=self.service.asset_registry.list_for_run(run_id),
                output=output,
            ),
        )
        qc = self._last_observation_result(quality_context)
        final = {
            **(produced_run.result or {}),
            "production": {
                **((produced_run.result or {}).get("production") or {}),
                "status": "READY_FOR_REVIEW" if qc["passed"] else "QC_FAILED",
                "qc": qc,
            },
        }
        final_run = self.content_runs.save_result(run_id, final) if qc["passed"] else self.content_runs.save_production_result(run_id, final)
        self.service.control.record(
            run_id,
            "qc.completed",
            status="COMPLETED" if qc["passed"] else "FAILED",
            output_refs=(qc["qc_id"],),
            evidence=qc,
        )
        return final_run, qc
