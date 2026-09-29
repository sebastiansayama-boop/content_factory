from __future__ import annotations

import os
from typing import Any

from .agent_os import AgentManager, ContentAgentOS
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
        register_content_tools(self.tool_registry, service=service, workspace=workspace)
        self.agent_os = ContentAgentOS(service.control, self.tool_registry)
        self.agent_manager = AgentManager(self.agent_os)

    def _research(self, run: ContentRun) -> ContentRun:
        prior = self.agent_os.invoke_tool(
            name="researcher",
            tool="knowledge.search",
            run_id=run.run_id,
            run=run,
        )
        if prior["claims"]:
            self.service.control.record(
                run.run_id,
                "research.reused_knowledge",
                status="COMPLETED",
                actor="researcher",
                evidence={"claims": len(prior["claims"])},
            )
            return run
        if run.status in {"DRAFT", "FAILED", "PLANNING"}:
            self.content_runs.start_execution(run.run_id)
        research_result = self.agent_os.invoke_tool(
            name="researcher",
            tool="research.public",
            run_id=run.run_id,
            run=run,
        )
        research_dict = ContentFactoryVerticalSlice.to_dict(research_result)

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
        jobs = self.agent_os.invoke_tool(
            name="producer",
            tool="production.queue",
            run_id=run_id,
            run=run,
            result=result,
        )
        run = self.content_runs.save_production_result(
            run_id,
            {**(run.result or {}), "production": {"status": "QUEUED", "job_ids": [j.job_id for j in jobs]}} ,
        )
        self.service.control.record(run_id, "production.queued", output_refs=tuple(j.job_id for j in jobs))

        jobs = self.agent_os.invoke_tool(
            name="producer",
            tool="production.execute",
            run_id=run_id,
            run=run,
        )
        run = self.content_runs.save_production_result(
            run_id,
            {**(run.result or {}), "production": {"status": "COMPLETED", "jobs": [j.to_dict() for j in jobs]}} ,
        )
        self.service.control.record(run_id, "production.completed", output_refs=tuple(j.job_id for j in jobs))
        assets = [self.service.asset_registry.register_completed_job(j).to_dict() for j in jobs]
        output = self.agent_os.invoke_tool(
            name="producer",
            tool="production.assemble",
            run_id=run_id,
            run=run,
            result=run.result or {},
        )
        run = self.content_runs.save_production_result(
            run_id,
            {
                **(run.result or {}),
                "production": {
                    "status": "ASSEMBLED",
                    "jobs": [j.to_dict() for j in jobs],
                    "assets": assets,
                    "output": output,
                },
            },
        )
        self.service.control.record(run_id, "assembly.completed", output_refs=(output["output_id"],))
        qc = self.agent_os.invoke_tool(
            name="quality",
            tool="quality.check",
            run_id=run_id,
            run=run,
            result=run.result or {},
            assets=self.service.asset_registry.list_for_run(run_id),
            output=output,
        )
        final = {
            **(run.result or {}),
            "production": {
                **(run.result.get("production") or {}),
                "status": "READY_FOR_REVIEW" if qc["passed"] else "QC_FAILED",
                "qc": qc,
            },
        }
        run = self.content_runs.save_result(run_id, final) if qc["passed"] else self.content_runs.save_production_result(run_id, final)
        self.service.control.record(
            run_id,
            "qc.completed",
            status="COMPLETED" if qc["passed"] else "FAILED",
            output_refs=(qc["qc_id"],),
            evidence=qc,
        )
        return run, qc

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
            plan = self.agent_manager.run(
                name="planner",
                run_id=run_id,
                operation="plan",
                action=lambda: self.planner.plan(
                run_id=run.run_id,
                title=run.title,
                brief=run.brief,
                audience=run.audience,
                goal=run.goal,
                formats=list(run.formats),
                constraints=list(run.constraints),
                ),
            )
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
            result = self.agent_manager.run(
                name="writer",
                run_id=run_id,
                operation=f"write-revision-{revision}",
                action=lambda: self._write(run, review_feedback=(
                review_history[-1].get("required_changes", []) if review_history else []
                )),
            )
            self.content_runs.save_result(run_id, {"run_id": run_id, "brief": run.brief, **result})
            self.service.control.record(
                run_id,
                "content.written",
                status="COMPLETED",
                actor="writer",
                evidence={"revision": revision},
            )

            review = self.agent_manager.run(
                name="reviewer",
                run_id=run_id,
                operation=f"review-revision-{revision}",
                action=lambda: self.agent_os.invoke_tool(
                    name="reviewer",
                    tool="content.review",
                    run_id=run_id,
                    run=run,
                    result=result,
                ),
            )
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
        return self.agent_manager.run(
            name="producer",
            run_id=run_id,
            operation="production",
            action=lambda: self._production(run_id, result_with_review),
        )
