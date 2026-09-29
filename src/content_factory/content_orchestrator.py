from __future__ import annotations

import os
from typing import Any

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

    def _research(self, run: ContentRun) -> ContentRun:
        prior = self.service.knowledge.search(run.brief)
        if prior["claims"]:
            return run
        if run.status in {"DRAFT", "FAILED", "PLANNING"}:
            self.content_runs.start_execution(run.run_id)
        research_result = ContentFactoryVerticalSlice(knowledge_store=self.service.knowledge).run(
            run_id=run.run_id,
            brief=run.brief,
            formats=list(run.formats) or ["article", "social_post", "visual_card"],
        )
        research_dict = ContentFactoryVerticalSlice.to_dict(research_result)
        self.content_runs.save_research_result(run.run_id, research_dict)
        self.service.control.record(
            run.run_id,
            "research.completed",
            output_refs=tuple(
                research_dict.get("research", {}).get("knowledge_refs", {}).get("claims", {}).values()
            ),
            evidence=research_dict.get("quality", {}),
        )
        candidates = self.service.knowledge.candidates_for_run(run.run_id)
        for candidate in candidates:
            claim_id = str(candidate.get("claim_id") or "").strip()
            if claim_id and str(candidate.get("status") or "").upper() != "ACCEPTED":
                self.service.knowledge.promote_claim(
                    claim_id,
                    decision_ref=f"factory-research-qc:{run.run_id}",
                )
        self.service.control.record(
            run.run_id,
            "research.accepted_for_generation",
            status="COMPLETED",
            actor="factory-research-qc",
            output_refs=tuple(c.get("claim_id", "") for c in candidates if c.get("claim_id")),
            evidence=research_dict.get("quality", {}),
        )
        updated = self.content_runs.get(run.run_id)
        if updated is None:
            raise ValueError("content run not found after research")
        return updated

    def _write(self, run: ContentRun, *, review_feedback: list[str] | None = None) -> dict[str, Any]:
        return KnowledgeContentBuilder(self.workspace, self.service.knowledge).build(
            run_id=run.run_id,
            topic=run.brief,
            audience=run.audience,
            goal=run.goal,
            formats=list(run.formats),
            constraints=list(run.constraints) + list(review_feedback or ()),
            tone=run.tone,
            tone_strength=run.tone_strength,
        )

    def _production(self, run_id: str, result: dict[str, Any]) -> tuple[ContentRun, dict[str, Any]]:
        run = self.content_runs.get(run_id)
        if run is None:
            raise ValueError("content run not found")
        self.content_runs.start_producing(run_id)
        jobs = self.service.asset_jobs.create_from_plan(run_id, result["production_plan"])
        run = self.content_runs.save_production_result(
            run_id,
            {**(run.result or {}), "production": {"status": "QUEUED", "job_ids": [j.job_id for j in jobs]}} ,
        )
        self.service.control.record(run_id, "production.queued", output_refs=tuple(j.job_id for j in jobs))

        jobs = self.service.asset_executor.execute_run(run_id)
        run = self.content_runs.save_production_result(
            run_id,
            {**(run.result or {}), "production": {"status": "COMPLETED", "jobs": [j.to_dict() for j in jobs]}} ,
        )
        self.service.control.record(run_id, "production.completed", output_refs=tuple(j.job_id for j in jobs))
        assets = [self.service.asset_registry.register_completed_job(j).to_dict() for j in jobs]
        output = ContentAssembler(
            self.service.asset_registry,
            os.environ.get("FACTORY_DATA_DIR", "./data"),
        ).assemble(
            run_id=run_id,
            script=run.result.get("script") or {},
            production_plan=run.result.get("production_plan") or {},
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
        qc = QualityGate().evaluate(
            run_id=run_id,
            script=run.result.get("script") or {},
            production_plan=run.result.get("production_plan") or {},
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
            plan = self.planner.plan(
                run_id=run.run_id,
                title=run.title,
                brief=run.brief,
                audience=run.audience,
                goal=run.goal,
                formats=list(run.formats),
                constraints=list(run.constraints),
            )
            self.content_runs.save_plan(run_id, plan)
            self.service.control.record(run_id, "planning.completed", status="COMPLETED", actor="planner")
        run = self.content_runs.get(run_id)
        if run is None:
            raise ValueError("content run not found after planning")
        run = self._research(run)

        review_history: list[dict[str, Any]] = []
        result: dict[str, Any] | None = None

        for revision in range(self.MAX_REVISIONS + 1):
            run = self.content_runs.get(run_id)
            if run is None:
                raise ValueError("content run not found before write")
            result = self._write(run, review_feedback=(
                review_history[-1].get("required_changes", []) if review_history else []
            ))
            self.content_runs.save_result(run_id, {"run_id": run_id, "brief": run.brief, **result})
            self.service.control.record(
                run_id,
                "content.written",
                status="COMPLETED",
                actor="writer",
                evidence={"revision": revision},
            )

            review = self.reviewer.review(
                run_id=run_id,
                brief=run.brief,
                audience=run.audience,
                goal=run.goal,
                result=result,
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
        return self._production(run_id, result_with_review)
