from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

from .content_run import ContentRunStore
from .content_run_planner import ContentRunPlanner
from .assembly import ContentAssembler, QualityGate
from .exporter import ContentExporter
from .knowledge_content import KnowledgeContentBuilder
from .service import FactoryService, Handler
from .workspace import ContentWorkspace
from .vertical_slice import ContentFactoryVerticalSlice


class ProductHandler(Handler):
    workspace: ContentWorkspace
    content_runs: ContentRunStore
    content_run_planner: ContentRunPlanner

    def _body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length < 0 or length > 64 * 1024:
            raise ValueError("request body exceeds maximum size")
        payload = json.loads(self.rfile.read(length).decode("utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("JSON body must be an object")
        return payload

    def _protect_product_api(self) -> bool:
        now = time.monotonic()
        client_ip = self.client_address[0]
        if self._auth_failure_limited(client_ip, now):
            self._json(429, {"error": "too many authentication failures"}, retry_after=60)
            return False
        if not self._authorized():
            self._json(401, {"error": "missing or invalid API token"})
            return False
        if self._rate_limited(self._authorized_requests, 10, now, 60.0):
            self._json(429, {"error": "product rate limit exceeded"}, retry_after=60)
            return False
        return True

    def do_GET(self) -> None:
        if self.path in {"/", "/index.html"}:
            raw = (Path(__file__).parent / "static" / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
            return

        if self.path == "/api/knowledge" or self.path == "/api/runs" or self.path.startswith("/api/runs/"):
            if not self._protect_product_api():
                return
            if self.path == "/api/regenerate":
                if not isinstance(payload.get("story"), dict):
                    raise ValueError("story must be an object")
                if not isinstance(payload.get("package"), dict):
                    raise ValueError("package must be an object")
                changed_claim_ids = payload.get("changed_claim_ids")
                if not isinstance(changed_claim_ids, list) or not all(isinstance(value, str) for value in changed_claim_ids):
                    raise ValueError("changed_claim_ids must be an array of strings")
                result = self.workspace.regenerate(
                    source=str(payload.get("source", "")),
                    story=payload["story"],
                    package=payload["package"],
                    changed_claim_ids=changed_claim_ids,
                )
                self._json(200, result)
                return
            if self.path == "/api/knowledge":
                self._json(200, {"counts": self.service.knowledge.counts()})
                return
            if self.path == "/api/runs":
                self._json(200, {"runs": [run.to_dict() for run in self.content_runs.list()]})
                return
            run_id = self.path.removeprefix("/api/runs/").strip("/")
            if run_id.endswith("/plan"):
                run_id = run_id.removesuffix("/plan").strip("/")
            if run_id.endswith("/jobs"):
                run_id = run_id.removesuffix("/jobs").strip("/")
                run = self.content_runs.get(run_id)
                if run is None:
                    self._json(404, {"error": "content run not found"})
                    return
                self._json(200, {"run_id": run_id, "jobs": [job.to_dict() for job in self.service.asset_jobs.list_for_run(run_id)]})
                return
            run = self.content_runs.get(run_id)
            if run is None:
                self._json(404, {"error": "content run not found"})
                return
            self._json(200, run.to_dict())
            return

        super().do_GET()

    def do_POST(self) -> None:
        is_run_plan = self.path.startswith("/api/runs/") and self.path.endswith("/plan")
        is_run_execute = self.path.startswith("/api/runs/") and self.path.endswith("/execute")
        is_run_build = self.path.startswith("/api/runs/") and self.path.endswith("/build")
        is_run_produce = self.path.startswith("/api/runs/") and self.path.endswith("/produce")
        is_run_produce_execute = self.path.startswith("/api/runs/") and self.path.endswith("/produce/execute")
        is_run_produce_poll = self.path.startswith("/api/runs/") and self.path.endswith("/produce/poll")
        is_run_assemble = self.path.startswith("/api/runs/") and self.path.endswith("/assemble")
        is_run_qc = self.path.startswith("/api/runs/") and self.path.endswith("/qc")
        is_run_approve = self.path.startswith("/api/runs/") and self.path.endswith("/approve")
        is_run_export = self.path.startswith("/api/runs/") and self.path.endswith("/export")
        is_run_factory = self.path.startswith("/api/runs/") and self.path.endswith("/factory")
        is_run_publish = self.path.startswith("/api/runs/") and self.path.endswith("/publish")
        is_run_observe = self.path.startswith("/api/runs/") and self.path.endswith("/observe")
        is_run_learn = self.path.startswith("/api/runs/") and self.path.endswith("/learn")
        is_learning_promote = self.path.startswith("/api/learning/") and self.path.endswith("/promote")
        is_run_replay = self.path.startswith("/api/runs/") and self.path.endswith("/replay")
        is_knowledge_promote = self.path.startswith("/api/knowledge/") and self.path.endswith("/promote")
        if self.path not in {"/api/analyze", "/api/produce", "/api/regenerate", "/api/runs"} and not is_run_plan and not is_run_execute and not is_knowledge_promote and not is_run_build and not is_run_produce and not is_run_produce_execute and not is_run_produce_poll and not is_run_assemble and not is_run_qc and not is_run_approve and not is_run_export and not is_run_factory and not is_run_publish and not is_run_observe and not is_run_learn and not is_learning_promote and not is_run_replay:
            super().do_POST()
            return

        if not self._protect_product_api():
            return

        try:
            if is_learning_promote:
                learning_id = self.path.removeprefix("/api/learning/").removesuffix("/promote").strip("/")
                payload = self._body()
                result = self.service.control.promote_learning(learning_id, str(payload.get("decision_ref", "")))
                self._json(200, result)
                return

            if is_run_replay:
                run_id = self.path.removeprefix("/api/runs/").removesuffix("/replay").strip("/")
                run = self.content_runs.get(run_id)
                if run is None:
                    self._json(404, {"error": "content run not found"})
                    return
                payload = self._body()
                changed = payload.get("changed_claim_ids", [])
                if not isinstance(changed, list) or not all(isinstance(v, str) for v in changed):
                    raise ValueError("changed_claim_ids must be an array of strings")
                result = self.service.control.replay_plan(run.to_dict(), changed_claim_ids=changed, changes=payload.get("changes"))
                self.service.control.record(run_id, "replay.planned", input_refs=tuple(changed), output_refs=tuple(result["regenerate_asset_ids"]))
                self._json(200, result)
                return

            if is_run_publish:
                run_id = self.path.removeprefix("/api/runs/").removesuffix("/publish").strip("/")
                run = self.content_runs.get(run_id)
                if run is None:
                    self._json(404, {"error": "content run not found"})
                    return
                if run.status != "APPROVED":
                    raise ValueError("only APPROVED runs can be published")
                payload = self._body()
                channel = str(payload.get("channel", "")).strip()
                if not channel:
                    raise ValueError("channel is required")
                content_ref = str(payload.get("content_ref") or (run.result or {}).get("export", {}).get("artifact") or run_id)
                prepared = self.service.control.prepare_publication(run_id, channel, content_ref, payload.get("content") if isinstance(payload.get("content"), dict) else (run.result or {}))
                published = self.service.control.publish(
                    prepared["publication_id"],
                    url=os.environ.get("PUBLISH_URL", "").strip() or None,
                    token=os.environ.get("PUBLISH_AUTH_TOKEN"),
                )
                self._json(200, published)
                return

            if is_run_observe:
                run_id = self.path.removeprefix("/api/runs/").removesuffix("/observe").strip("/")
                if self.content_runs.get(run_id) is None:
                    self._json(404, {"error": "content run not found"})
                    return
                payload = self._body()
                publication_id = str(payload.get("publication_id", "")).strip()
                metrics = payload.get("metrics")
                if not publication_id or not isinstance(metrics, dict):
                    raise ValueError("publication_id and metrics object are required")
                result = self.service.control.observe(publication_id, metrics, str(payload.get("source") or "api"))
                self._json(201, result)
                return

            if is_run_learn:
                run_id = self.path.removeprefix("/api/runs/").removesuffix("/learn").strip("/")
                if self.content_runs.get(run_id) is None:
                    self._json(404, {"error": "content run not found"})
                    return
                payload = self._body()
                observations = payload.get("observation_ids", [])
                if not isinstance(observations, list) or not all(isinstance(v, str) for v in observations):
                    raise ValueError("observation_ids must be an array of strings")
                result = self.service.control.create_learning(
                    run_id, observations, str(payload.get("hypothesis", "")),
                    payload.get("proposed_changes") if isinstance(payload.get("proposed_changes"), dict) else {},
                )
                self._json(201, result)
                return

            if is_run_factory:
                run_id = self.path.removeprefix("/api/runs/").removesuffix("/factory").strip("/")
                run = self.content_runs.get(run_id)
                if run is None:
                    self._json(404, {"error": "content run not found"})
                    return
                try:
                    if run.status == "DRAFT":
                        self.content_runs.start_planning(run_id)
                        run = self.content_runs.get(run_id)
                    self.service.control.record(run_id, "factory.started", status="RUNNING", actor="api")
                    result = KnowledgeContentBuilder(self.workspace, self.service.knowledge).build(
                        run_id=run_id, topic=run.title or run.brief, audience=run.audience,
                        goal=run.goal, formats=list(run.formats), constraints=list(run.constraints),
                    )
                    run = self.content_runs.save_result(run_id, {"run_id": run_id, "brief": run.brief, **result})
                    self.service.control.record(run_id, "editorial.built", output_refs=("content_spec", "script", "production_plan"))
                    self.content_runs.start_producing(run_id)
                    jobs = self.service.asset_jobs.create_from_plan(run_id, result["production_plan"])
                    run = self.content_runs.save_production_result(run_id, {
                        **(run.result or {}),
                        "production": {"status": "QUEUED", "job_ids": [j.job_id for j in jobs]},
                    })
                    self.service.control.record(run_id, "production.queued", output_refs=tuple(j.job_id for j in jobs))
                    jobs = self.service.asset_executor.execute_run(run_id)
                    run = self.content_runs.save_production_result(run_id, {
                        **(run.result or {}),
                        "production": {"status": "COMPLETED", "jobs": [j.to_dict() for j in jobs]},
                    })
                    self.service.control.record(run_id, "production.completed", output_refs=tuple(j.job_id for j in jobs))
                    assets = [self.service.asset_registry.register_completed_job(j).to_dict() for j in jobs]
                    output = ContentAssembler(self.service.asset_registry, os.environ.get("FACTORY_DATA_DIR", "./data")).assemble(
                        run_id=run_id, script=run.result.get("script") or {}, production_plan=run.result.get("production_plan") or {}
                    )
                    run = self.content_runs.save_production_result(run_id, {
                        **(run.result or {}), "production": {"status": "ASSEMBLED", "jobs": [j.to_dict() for j in jobs], "assets": assets, "output": output},
                    })
                    self.service.control.record(run_id, "assembly.completed", output_refs=(output["output_id"],))
                    qc = QualityGate().evaluate(run_id=run_id, script=run.result.get("script") or {},
                        production_plan=run.result.get("production_plan") or {}, assets=self.service.asset_registry.list_for_run(run_id), output=output)
                    final = {**(run.result or {}), "production": {**(run.result.get("production") or {}), "status": "READY_FOR_REVIEW" if qc["passed"] else "QC_FAILED", "qc": qc}}
                    run = self.content_runs.save_result(run_id, final) if qc["passed"] else self.content_runs.save_production_result(run_id, final)
                    self.service.control.record(run_id, "qc.completed", status="COMPLETED" if qc["passed"] else "FAILED", output_refs=(qc["qc_id"],), evidence=qc)
                    self._json(200, {"run": run.to_dict(), "qc": qc, "events": [e.to_dict() for e in self.service.control.timeline(run_id)]})
                except Exception:
                    self.content_runs.mark_failed(run_id)
                    self.service.control.record(run_id, "factory.failed", status="FAILED", actor="api")
                    raise
                return

            if is_knowledge_promote:
                claim_id = self.path.removeprefix("/api/knowledge/").removesuffix("/promote").strip("/")
                if not claim_id:
                    raise ValueError("knowledge claim id is required")
                payload = self._body()
                decision_ref = str(payload.get("decision_ref", "")).strip()
                claim = self.service.knowledge.promote_claim(claim_id, decision_ref=decision_ref)
                self._json(200, {
                    "claim_id": claim.claim_id,
                    "status": claim.status,
                    "revision_id": claim.revision_id,
                    "decision_ref": decision_ref,
                    "promoted_at": claim.promoted_at,
                })
                return

            if is_run_build:
                run_id = self.path.removeprefix("/api/runs/").removesuffix("/build").strip("/")
                if not run_id:
                    raise ValueError("content run id is required")
                run = self.content_runs.get(run_id)
                if run is None:
                    self._json(404, {"error": "content run not found"})
                    return
                self.content_runs.start_planning(run_id)
                try:
                    result = KnowledgeContentBuilder(self.workspace, self.service.knowledge).build(
                        run_id=run.run_id,
                        topic=run.title or run.brief,
                        audience=run.audience,
                        goal=run.goal,
                        formats=list(run.formats),
                        constraints=list(run.constraints),
                    )
                    updated = self.content_runs.save_result(run_id, {
                        "run_id": run_id,
                        "brief": run.brief,
                        **result,
                    })
                except Exception:
                    self.content_runs.mark_failed(run_id)
                    raise
                self._json(200, updated.to_dict())
                return

            if is_run_approve:
                run_id = self.path.removeprefix("/api/runs/").removesuffix("/approve").strip("/")
                if not run_id:
                    raise ValueError("content run id is required")
                run = self.content_runs.get(run_id)
                if run is None:
                    self._json(404, {"error": "content run not found"})
                    return
                result = run.result or {}
                production = result.get("production")
                qc = production.get("qc") if isinstance(production, dict) else None
                if not isinstance(qc, dict) or qc.get("status") != "PASSED":
                    raise ValueError("only QC-passed runs can be approved")
                payload = self._body()
                decision_ref = str(payload.get("decision_ref", "")).strip()
                updated = self.content_runs.approve(run_id, decision_ref=decision_ref)
                self._json(200, updated.to_dict())
                return

            if is_run_export:
                run_id = self.path.removeprefix("/api/runs/").removesuffix("/export").strip("/")
                if not run_id:
                    raise ValueError("content run id is required")
                run = self.content_runs.get(run_id)
                if run is None:
                    self._json(404, {"error": "content run not found"})
                    return
                try:
                    export = ContentExporter(os.environ.get("FACTORY_DATA_DIR", "./data")).export(run_id=run_id, result=run.result or {})
                    updated = self.content_runs.mark_exported(run_id, export)
                except Exception:
                    self.content_runs.mark_failed(run_id)
                    raise
                self._json(200, {"run": updated.to_dict(), "export": export})
                return
            if is_run_assemble:
                run_id = self.path.removeprefix("/api/runs/").removesuffix("/assemble").strip("/")
                if not run_id:
                    raise ValueError("content run id is required")
                run = self.content_runs.get(run_id)
                if run is None:
                    self._json(404, {"error": "content run not found"})
                    return
                result = run.result or {}
                production = result.get("production")
                if not isinstance(production, dict):
                    raise ValueError("production has not been executed")
                jobs = self.service.asset_jobs.list_for_run(run_id)
                if not jobs or any(job.status != "COMPLETED" for job in jobs):
                    raise ValueError("all asset jobs must be COMPLETED before assembly")
                try:
                    assets = [self.service.asset_registry.register_completed_job(job).to_dict() for job in jobs]
                    output = ContentAssembler(self.service.asset_registry, os.environ.get("FACTORY_DATA_DIR", "./data")).assemble(
                        run_id=run_id,
                        script=result.get("script") if isinstance(result.get("script"), dict) else {},
                        production_plan=result.get("production_plan") if isinstance(result.get("production_plan"), dict) else {},
                    )
                    updated = self.content_runs.save_production_result(run_id, {
                        **result,
                        "production": {**production, "status": "ASSEMBLED", "assets": assets, "output": output},
                    })
                except Exception:
                    self.content_runs.mark_failed(run_id)
                    raise
                self._json(200, {"run": updated.to_dict(), "output": output})
                return

            if is_run_qc:
                run_id = self.path.removeprefix("/api/runs/").removesuffix("/qc").strip("/")
                if not run_id:
                    raise ValueError("content run id is required")
                run = self.content_runs.get(run_id)
                if run is None:
                    self._json(404, {"error": "content run not found"})
                    return
                result = run.result or {}
                production = result.get("production")
                if not isinstance(production, dict):
                    raise ValueError("production has not been assembled")
                output = production.get("output")
                if not isinstance(output, dict):
                    raise ValueError("production output is missing; run /assemble first")
                assets = self.service.asset_registry.list_for_run(run_id)
                qc = QualityGate().evaluate(
                    run_id=run_id,
                    script=result.get("script") if isinstance(result.get("script"), dict) else {},
                    production_plan=result.get("production_plan") if isinstance(result.get("production_plan"), dict) else {},
                    assets=assets,
                    output=output,
                )
                final_result = {
                    **result,
                    "production": {**production, "status": "READY_FOR_REVIEW" if qc["passed"] else "QC_FAILED", "qc": qc},
                }
                updated = self.content_runs.save_result(run_id, final_result) if qc["passed"] else self.content_runs.save_production_result(run_id, final_result)
                self._json(200, {"run": updated.to_dict(), "qc": qc})
                return
            if is_run_produce_poll:
                run_id = self.path.removeprefix("/api/runs/").removesuffix("/produce/poll").strip("/")
                if not run_id:
                    raise ValueError("content run id is required")
                run = self.content_runs.get(run_id)
                if run is None:
                    self._json(404, {"error": "content run not found"})
                    return
                jobs = self.service.asset_poller.poll_run(run_id)
                statuses = [job.status for job in jobs]
                overall = "COMPLETED" if jobs and all(status == "COMPLETED" for status in statuses) else (
                    "FAILED" if any(status == "FAILED" for status in statuses) else "SUBMITTED"
                )
                result = {
                    **(run.result or {}),
                    "production": {
                        **((run.result or {}).get("production") or {}),
                        "status": overall,
                        "jobs": [job.to_dict() for job in jobs],
                    },
                }
                updated = self.content_runs.save_production_result(run_id, result)
                self._json(200, {"run": updated.to_dict(), "jobs": [job.to_dict() for job in jobs]})
                return

            if is_run_produce_execute:
                run_id = self.path.removeprefix("/api/runs/").removesuffix("/produce/execute").strip("/")
                if not run_id:
                    raise ValueError("content run id is required")
                run = self.content_runs.get(run_id)
                if run is None:
                    self._json(404, {"error": "content run not found"})
                    return
                if not run.result or not isinstance(run.result.get("production"), dict):
                    raise ValueError("production jobs are not queued; run /produce first")
                try:
                    jobs = self.service.asset_executor.execute_run(run_id)
                    statuses = [job.status for job in jobs]
                    overall = "COMPLETED" if jobs and all(status == "COMPLETED" for status in statuses) else (
                        "FAILED" if any(status == "FAILED" for status in statuses) else "SUBMITTED"
                    )
                    result = {
                        **(run.result or {}),
                        "production": {
                            **run.result.get("production", {}),
                            "status": overall,
                            "jobs": [job.to_dict() for job in jobs],
                        },
                    }
                    updated = self.content_runs.save_production_result(run_id, result)
                except Exception:
                    self.content_runs.mark_failed(run_id)
                    raise
                self._json(200, {"run": updated.to_dict(), "jobs": [job.to_dict() for job in jobs]})
                return

            if is_run_produce:
                run_id = self.path.removeprefix("/api/runs/").removesuffix("/produce").strip("/")
                if not run_id:
                    raise ValueError("content run id is required")
                run = self.content_runs.get(run_id)
                if run is None:
                    self._json(404, {"error": "content run not found"})
                    return
                result = run.result or {}
                production_plan = result.get("production_plan") if isinstance(result, dict) else None
                if not isinstance(production_plan, dict):
                    raise ValueError("content run has no production plan; run /build first")
                self.content_runs.start_producing(run_id)
                try:
                    jobs = self.service.asset_jobs.create_from_plan(run_id, production_plan)
                    updated = self.content_runs.save_production_result(run_id, {
                        **result,
                        "production": {
                            "status": "QUEUED",
                            "job_ids": [job.job_id for job in jobs],
                        },
                    })
                except Exception:
                    self.content_runs.mark_failed(run_id)
                    raise
                self._json(200, {
                    "run": updated.to_dict(),
                    "jobs": [job.to_dict() for job in jobs],
                })
                return

            if is_run_execute:
                run_id = self.path.removeprefix("/api/runs/").removesuffix("/execute").strip("/")
                if not run_id:
                    raise ValueError("content run id is required")
                run = self.content_runs.get(run_id)
                if run is None:
                    self._json(404, {"error": "content run not found"})
                    return
                self.content_runs.start_execution(run_id)
                try:
                    result = ContentFactoryVerticalSlice(knowledge_store=self.service.knowledge).run(
                        run_id=run.run_id,
                        brief=run.brief,
                        formats=list(run.formats) or ["article", "social_post", "visual_card"],
                    )
                    updated = self.content_runs.save_result(
                        run_id,
                        ContentFactoryVerticalSlice.to_dict(result),
                    )
                except Exception:
                    self.content_runs.mark_failed(run_id)
                    raise
                self._json(200, updated.to_dict())
                return

            if is_run_plan:
                run_id = self.path.removeprefix("/api/runs/").removesuffix("/plan").strip("/")
                if not run_id:
                    raise ValueError("content run id is required")
                run = self.content_runs.get(run_id)
                if run is None:
                    self._json(404, {"error": "content run not found"})
                    return
                self.content_runs.start_planning(run_id)
                try:
                    plan = self.content_run_planner.plan(
                        run_id=run.run_id,
                        title=run.title,
                        brief=run.brief,
                        audience=run.audience,
                        goal=run.goal,
                        formats=list(run.formats),
                        constraints=list(run.constraints),
                    )
                except Exception:
                    self.content_runs.mark_failed(run_id)
                    raise
                updated = self.content_runs.save_plan(run_id, plan)
                self._json(200, updated.to_dict())
                return

            payload = self._body()
            if self.path == "/api/runs":
                title = str(payload.get("title", "")).strip()
                brief = str(payload.get("brief", "")).strip()
                audience = str(payload.get("audience", "")).strip()
                goal = str(payload.get("goal", "")).strip()
                formats = payload.get("formats", [])
                constraints = payload.get("constraints", [])
                if not title:
                    raise ValueError("title is required")
                if not brief:
                    raise ValueError("brief is required")
                if len(title) > 200:
                    raise ValueError("title exceeds maximum length")
                if len(brief) > 16_000:
                    raise ValueError("brief exceeds maximum length")
                if not isinstance(formats, list) or not all(isinstance(value, str) for value in formats):
                    raise ValueError("formats must be an array of strings")
                if not isinstance(constraints, list) or not all(isinstance(value, str) for value in constraints):
                    raise ValueError("constraints must be an array of strings")
                run = self.content_runs.create(
                    title=title,
                    brief=brief,
                    audience=audience,
                    goal=goal,
                    formats=tuple(value.strip() for value in formats if value.strip()),
                    constraints=tuple(value.strip() for value in constraints if value.strip()),
                )
                self._json(201, run.to_dict())
                return
            if self.path == "/api/analyze":
                result = self.workspace.analyze(
                    source=str(payload.get("source", "")),
                    title=str(payload.get("title", "Untitled source")),
                )
            else:
                formats = payload.get("formats", [])
                if not isinstance(formats, list):
                    raise ValueError("formats must be an array")
                result = self.workspace.produce(
                    source=str(payload.get("source", "")),
                    story=payload.get("story") if isinstance(payload.get("story"), dict) else {},
                    formats=[str(value) for value in formats],
                )
            self._json(200, result)
        except json.JSONDecodeError:
            self._json(400, {"error": "invalid JSON body"})
        except UnicodeDecodeError:
            self._json(400, {"error": "request body must be UTF-8"})
        except ValueError as exc:
            self._json(400, {"error": str(exc)})
        except Exception as exc:
            self._json(400, {"error": str(exc)})


def main() -> None:
    service = FactoryService()
    ProductHandler.service = service
    ProductHandler.workspace = ContentWorkspace(service)
    ProductHandler.content_runs = service.content_runs
    ProductHandler.content_run_planner = ContentRunPlanner(ProductHandler.workspace)
    from http.server import ThreadingHTTPServer

    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8080"))
    server = ThreadingHTTPServer((host, port), ProductHandler)
    try:
        server.serve_forever()
    finally:
        server.server_close()
        service.close()


if __name__ == "__main__":
    main()
