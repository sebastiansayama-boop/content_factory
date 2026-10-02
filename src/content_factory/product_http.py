from __future__ import annotations

import hmac
import json
import mimetypes
import os
import threading
import time
from pathlib import Path
from typing import Any

from .content_run import ContentRunStore
from .content_run_planner import ContentRunPlanner
from .assembly import ContentAssembler, QualityGate
from .exporter import ContentExporter
from .knowledge_content import KnowledgeContentBuilder, build_replay_production_package
from .information_flow import attach_publication, build_information_flow
from .service import FactoryService, Handler
from .runtime import FactoryRuntime, WorkItem
from .workspace import ContentWorkspace
from .vertical_slice import ContentFactoryVerticalSlice
from .distribution import TelegramDistributionAdapter, FakeTelegramDistributionAdapter
from .content_package import apply_package_edit, build_content_package, platform_from_constraints
from .integrations import IntegrationError
from .telegram_bot import FactoryHttpClient, TelegramApi, TelegramFactoryBot


class ProductHandler(Handler):
    workspace: ContentWorkspace
    content_runs: ContentRunStore
    content_run_planner: ContentRunPlanner
    telegram_bot: TelegramFactoryBot | None = None

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

    def _trace_runtime(self, run_id: str, revision_id: str = "r1") -> tuple[FactoryRuntime, WorkItem]:
        runtime = FactoryRuntime(runtime_store=self.service.runtime_store)
        item = WorkItem(
            work_item_id=run_id,
            operation_id=f"content-run:{run_id}",
            revision_id=f"content-run:{run_id}:{revision_id}",
            objective="execute content factory stages",
            requested_outcome="durable research, editorial, production and QC trace",
            inputs=(run_id,),
            knowledge_basis=(),
            required_capabilities=("content.factory.vertical_slice",),
            owner="product-api",
            acceptance_criteria=("stage execution is recorded",),
            release_requirements=(),
        )
        if run_id not in runtime.states:
            runtime.submit(item, actor="api")
        elif runtime.operation_ids.get(run_id) != item.operation_id:
            raise ValueError("runtime operation_id conflicts with content run")
        return runtime, item

    def _record_trace(self, run_id: str, revision_id: str = "r1", **kwargs: Any) -> None:
        runtime, item = self._trace_runtime(run_id, revision_id=revision_id)
        runtime.record_trace(item, **kwargs, actor="api")

    def _handle_telegram_webhook(self) -> None:
        expected_secret = os.environ.get("TELEGRAM_WEBHOOK_SECRET", "").strip()
        if not expected_secret:
            self._json(503, {"error": "Telegram webhook is not configured"})
            return
        presented_secret = self.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if not hmac.compare_digest(presented_secret, expected_secret):
            self._json(401, {"error": "invalid Telegram webhook secret"})
            return
        bot = type(self).telegram_bot
        if bot is None:
            self._json(503, {"error": "Telegram bot is not configured"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 0 or length > 64 * 1024:
                raise ValueError("Telegram webhook payload exceeds maximum size")
            raw = self.rfile.read(length)
            if len(raw) != length:
                raise ValueError("incomplete Telegram webhook payload")
            payload = json.loads(raw.decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("Telegram webhook JSON body must be an object")
        except json.JSONDecodeError:
            self._json(400, {"error": "invalid Telegram webhook JSON"})
            return
        except (UnicodeDecodeError, ValueError) as exc:
            self._json(400, {"error": str(exc)})
            return
        threading.Thread(target=bot.handle_update, args=(payload,), daemon=True).start()
        self._json(200, {"ok": True})

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
            if self.path == "/api/knowledge":
                self._json(200, {"counts": self.service.knowledge.counts()})
                return
            if self.path == "/api/runs":
                self._json(200, {"runs": [run.to_dict() for run in self.content_runs.list()]})
                return
            raw_run_path = self.path.removeprefix("/api/runs/").strip("/")
            if "/assets/" in raw_run_path:
                run_id, asset_id = raw_run_path.split("/assets/", 1)
                run_id = run_id.strip("/")
                asset_id = asset_id.strip("/")
                if not run_id or not asset_id or "/" in asset_id:
                    self._json(400, {"error": "run id and asset id are required"})
                    return
                if self.content_runs.get(run_id) is None:
                    self._json(404, {"error": "content run not found"})
                    return
                asset = self.service.asset_registry.get(asset_id)
                if asset is None or asset.run_id != run_id:
                    self._json(404, {"error": "asset not found"})
                    return
                asset_path = Path(asset.uri).resolve()
                data_root = Path(os.environ.get("FACTORY_DATA_DIR", "./data")).resolve()
                try:
                    asset_path.relative_to(data_root)
                except ValueError:
                    self._json(404, {"error": "asset not found"})
                    return
                if not asset_path.is_file():
                    self._json(404, {"error": "asset file not found"})
                    return
                raw = asset_path.read_bytes()
                content_type = mimetypes.guess_type(asset_path.name)[0] or "application/octet-stream"
                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(raw)))
                self.send_header("Cache-Control", "private, max-age=300")
                self.end_headers()
                self.wfile.write(raw)
                return

            if raw_run_path.endswith("/export/download"):
                run_id = raw_run_path.removesuffix("/export/download").strip("/")
                run = self.content_runs.get(run_id)
                if run is None:
                    self._json(404, {"error": "content run not found"})
                    return
                export = (run.result or {}).get("export")
                if not isinstance(export, dict) or not export.get("artifact"):
                    self._json(404, {"error": "export not found"})
                    return
                filename = str(export["artifact"]).strip()
                if not filename or Path(filename).name != filename:
                    self._json(404, {"error": "export artifact not found"})
                    return
                export_path = (Path(os.environ.get("FACTORY_DATA_DIR", "./data")) / "exports" / run_id / filename).resolve()
                export_root = (Path(os.environ.get("FACTORY_DATA_DIR", "./data")) / "exports" / run_id).resolve()
                try:
                    export_path.relative_to(export_root)
                except ValueError:
                    self._json(404, {"error": "export artifact not found"})
                    return
                if not export_path.is_file():
                    self._json(404, {"error": "export artifact not found"})
                    return
                raw = export_path.read_bytes()
                content_type = mimetypes.guess_type(export_path.name)[0] or "application/octet-stream"
                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(raw)))
                self.send_header("Content-Disposition", f'attachment; filename="{export_path.name}"')
                self.end_headers()
                self.wfile.write(raw)
                return

            if raw_run_path.endswith("/package"):
                run_id = raw_run_path.removesuffix("/package").strip("/")
                run = self.content_runs.get(run_id)
                if run is None:
                    self._json(404, {"error": "content run not found"})
                    return
                result = run.result or {}
                package = result.get("package") if isinstance(result.get("package"), dict) else None
                if package is None:
                    platform = platform_from_constraints(run.constraints)
                    package = build_content_package(run_id=run_id, result=result, platform=platform)
                self._json(200, {"run_id": run_id, "package": package})
                return

            run_id = raw_run_path
            if run_id.endswith("/plan"):
                run_id = run_id.removesuffix("/plan").strip("/")
            if run_id.endswith("/content-brief/revisions"):
                run_id = run_id.removesuffix("/content-brief/revisions").strip("/")
                if self.content_runs.get(run_id) is None:
                    self._json(404, {"error": "content run not found"})
                    return
                self._json(200, {
                    "run_id": run_id,
                    "revisions": [item.to_dict() for item in self.content_runs.list_content_brief_revisions(run_id)],
                })
                return
            if "/content-brief/" in run_id:
                base_run_id, revision_id = run_id.split("/content-brief/", 1)
                brief = self.content_runs.get_content_brief(base_run_id, revision_id=revision_id.strip("/"))
                if self.content_runs.get(base_run_id) is None:
                    self._json(404, {"error": "content run not found"})
                    return
                if brief is None:
                    self._json(404, {"error": "content brief revision not found"})
                    return
                self._json(200, brief.to_dict())
                return
            if run_id.endswith("/content-brief"):
                run_id = run_id.removesuffix("/content-brief").strip("/")
                if self.content_runs.get(run_id) is None:
                    self._json(404, {"error": "content run not found"})
                    return
                brief = self.content_runs.get_content_brief(run_id)
                if brief is None:
                    self._json(404, {"error": "content brief not found"})
                    return
                self._json(200, brief.to_dict())
                return

            if run_id.endswith("/jobs"):
                run_id = run_id.removesuffix("/jobs").strip("/")
                run = self.content_runs.get(run_id)
                if run is None:
                    self._json(404, {"error": "content run not found"})
                    return
                self._json(200, {"run_id": run_id, "jobs": [job.to_dict() for job in self.service.asset_jobs.list_for_run(run_id)]})
                return
            if run_id.endswith("/execution-trace"):
                run_id = run_id.removesuffix("/execution-trace").strip("/")
                if self.content_runs.get(run_id) is None:
                    self._json(404, {"error": "content run not found"})
                    return
                events = [
                    event for event in self.service.runtime_store.load_events()
                    if event["work_item_id"] == run_id
                ]
                self._json(200, {"run_id": run_id, "events": events})
                return

            if run_id.endswith("/timeline"):
                run_id = run_id.removesuffix("/timeline").strip("/")
                if self.content_runs.get(run_id) is None:
                    self._json(404, {"error": "content run not found"})
                    return
                self._json(200, {"run_id": run_id, "events": [event.to_dict() for event in self.service.control.timeline(run_id)]})
                return
            if run_id.endswith("/publications"):
                run_id = run_id.removesuffix("/publications").strip("/")
                if self.content_runs.get(run_id) is None:
                    self._json(404, {"error": "content run not found"})
                    return
                self._json(200, {"run_id": run_id, "publications": self.service.control.list_publications(run_id)})
                return
            if run_id.endswith("/observations"):
                run_id = run_id.removesuffix("/observations").strip("/")
                if self.content_runs.get(run_id) is None:
                    self._json(404, {"error": "content run not found"})
                    return
                self._json(200, {"run_id": run_id, "observations": self.service.control.observations(run_id)})
                return
            run = self.content_runs.get(run_id)
            if run is None:
                self._json(404, {"error": "content run not found"})
                return
            self._json(200, run.to_dict())
            return

        super().do_GET()

    def do_POST(self) -> None:
        if self.path == "/telegram/webhook":
            self._handle_telegram_webhook()
            return

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
        is_run_regenerate = self.path.startswith("/api/runs/") and self.path.endswith("/regenerate")
        is_run_publish = self.path.startswith("/api/runs/") and self.path.endswith("/publish")
        is_run_package_edit = self.path.startswith("/api/runs/") and self.path.endswith("/package")
        is_run_observe = self.path.startswith("/api/runs/") and self.path.endswith("/observe")
        is_run_learn = self.path.startswith("/api/runs/") and self.path.endswith("/learn")
        is_learning_promote = self.path.startswith("/api/learning/") and self.path.endswith("/promote")
        is_run_replay = self.path.startswith("/api/runs/") and self.path.endswith("/replay")
        is_knowledge_promote = self.path.startswith("/api/knowledge/") and self.path.endswith("/promote")
        if self.path not in {"/api/analyze", "/api/produce", "/api/regenerate", "/api/runs"} and not is_run_plan and not is_run_execute and not is_knowledge_promote and not is_run_build and not is_run_produce and not is_run_produce_execute and not is_run_produce_poll and not is_run_assemble and not is_run_qc and not is_run_approve and not is_run_export and not is_run_factory and not is_run_regenerate and not is_run_publish and not is_run_package_edit and not is_run_observe and not is_run_learn and not is_learning_promote and not is_run_replay:
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
                source_run_id = self.path.removeprefix("/api/runs/").removesuffix("/replay").strip("/")
                source_run = self.content_runs.get(source_run_id)
                if source_run is None:
                    self._json(404, {"error": "content run not found"})
                    return
                payload = self._body()
                changed = payload.get("changed_claim_ids", [])
                if not isinstance(changed, list) or not all(isinstance(v, str) for v in changed):
                    raise ValueError("changed_claim_ids must be an array of strings")
                brief_id = str(payload.get("brief_id", "")).strip()
                revision_id = str(payload.get("revision_id", "")).strip()
                if not brief_id or not revision_id:
                    raise ValueError("brief_id and revision_id are required")
                persisted_brief = self.content_runs.get_content_brief(source_run_id, revision_id=revision_id)
                if persisted_brief is None:
                    self._json(404, {"error": "content brief revision not found"})
                    return
                if persisted_brief.brief_id != brief_id:
                    raise ValueError("content brief id does not match revision")
                exact_brief = dict(persisted_brief.payload)
                exact_brief["_revision_id"] = persisted_brief.revision_id
                self._record_trace(
                    source_run_id,
                    revision_id=persisted_brief.revision_id,
                    stage="REPLAY",
                    task="load_content_brief",
                    tool="ContentRunStore",
                    action="load_revision",
                    result={"status": "loaded", "revision_id": persisted_brief.revision_id},
                    decision="ACCEPT",
                )

                replay_run = self.content_runs.create(
                    title=f"{source_run.title} — replay {persisted_brief.revision_id}",
                    brief=source_run.brief,
                    audience=source_run.audience,
                    goal=source_run.goal,
                    formats=source_run.formats,
                    constraints=source_run.constraints,
                )
                self.content_runs.start_planning(replay_run.run_id)
                self._record_trace(
                    replay_run.run_id,
                    revision_id=persisted_brief.revision_id,
                    stage="REPLAY",
                    task="load_content_brief",
                    tool="ContentRunStore",
                    action="load_revision",
                    result={"status": "loaded", "source_run_id": source_run_id, "revision_id": persisted_brief.revision_id},
                    decision="ACCEPT",
                )
                package = build_replay_production_package(
                    run_id=replay_run.run_id,
                    content_brief=exact_brief,
                )
                production_plan = package["production_plan"]
                self.content_runs.start_producing(replay_run.run_id)
                jobs = self.service.asset_jobs.create_from_plan(replay_run.run_id, production_plan)
                self._record_trace(
                    replay_run.run_id,
                    revision_id=persisted_brief.revision_id,
                    stage="PRODUCTION",
                    task="replay_production",
                    tool=type(self.service.asset_executor).__name__,
                    action="execute_run",
                    result={"status": "started", "job_count": len(jobs), "source_revision_id": persisted_brief.revision_id},
                )
                jobs = self.service.asset_executor.execute_run(replay_run.run_id)
                completed = [job for job in jobs if job.status == "COMPLETED"]
                if len(completed) != len(jobs):
                    raise ValueError("replay production did not complete all asset jobs")
                assets = [self.service.asset_registry.register_completed_job(job) for job in completed]
                request_by_id = {
                    str(request.get("asset_request_id")): request
                    for request in production_plan.get("asset_requests", [])
                    if isinstance(request, dict)
                }
                flow_assets = [
                    {
                        "id": asset.asset_id,
                        "format": asset.asset_type,
                        "content_element_ids": list(request_by_id[asset.asset_request_id].get("content_element_ids") or []),
                        "claim_refs": list(asset.claim_refs),
                        "evidence_refs": list(asset.evidence_refs),
                    }
                    for asset in assets
                ]
                durable_context = self.service.knowledge.search(source_run.brief)
                research = {
                    "claims": [
                        {**claim, "id": claim.get("claim_id")}
                        for claim in durable_context.get("claims", [])
                    ],
                    "sources": [
                        {**source, "id": source.get("source_id")}
                        for source in durable_context.get("sources", [])
                    ],
                    "evidence": [
                        {**evidence, "id": evidence.get("evidence_id")}
                        for evidence in durable_context.get("evidence", [])
                    ],
                }
                if not research["claims"]:
                    raise ValueError("source run has no durable accepted claims for replay")
                information_flow = build_information_flow(
                    run_id=replay_run.run_id,
                    research=research,
                    package={
                        "story": {"id": package["script"]["script_id"]},
                        "content_brief": exact_brief,
                        "package": flow_assets,
                    },
                ).to_dict()
                replay_result = {
                    "run_id": replay_run.run_id,
                    "replay_of_run_id": source_run_id,
                    "replay_of_content_brief": {
                        "brief_id": brief_id,
                        "revision_id": persisted_brief.revision_id,
                    },
                    "content_brief": {
                        **{key: value for key, value in exact_brief.items() if key != "_revision_id"},
                        "revision_id": persisted_brief.revision_id,
                    },
                    "content_brief_revision_id": persisted_brief.revision_id,
                    **package,
                    "production": {
                        "status": "COMPLETED",
                        "job_ids": [job.job_id for job in jobs],
                        "jobs": [job.to_dict() for job in jobs],
                        "assets": [asset.to_dict() for asset in assets],
                    },
                    "information_flow": information_flow,
                    "replay": {
                        "changed_claim_ids": list(dict.fromkeys(changed)),
                        "changes": payload.get("changes") if isinstance(payload.get("changes"), dict) else {},
                    },
                }
                self.content_runs.save_production_result(replay_run.run_id, replay_result)
                output = ContentAssembler(
                    self.service.asset_registry,
                    os.environ.get("FACTORY_DATA_DIR", "./data"),
                ).assemble(
                    run_id=replay_run.run_id,
                    script=package["script"],
                    production_plan=production_plan,
                    assets=assets,
                )
                qc = QualityGate().evaluate(
                    run_id=replay_run.run_id,
                    script=package["script"],
                    production_plan=production_plan,
                    assets=assets,
                    output=output,
                    information_flow=information_flow,
                )
                self._record_trace(
                    replay_run.run_id,
                    revision_id=persisted_brief.revision_id,
                    stage="QC",
                    task="replay_quality_gate",
                    tool="QualityGate",
                    action="evaluate",
                    result={"status": qc["status"], "qc_id": qc["qc_id"], "source_revision_id": persisted_brief.revision_id},
                    decision="ACCEPT" if qc["passed"] else "FAIL",
                )
                final = {
                    **replay_result,
                    "production": {
                        **replay_result["production"],
                        "status": "READY_FOR_REVIEW" if qc["passed"] else "QC_FAILED",
                        "output": output,
                        "qc": qc,
                    },
                }
                replay_run = self.content_runs.save_result(replay_run.run_id, final)
                self.service.control.record(
                    source_run_id,
                    "replay.completed",
                    input_refs=(f"content_brief:{persisted_brief.revision_id}",),
                    output_refs=(replay_run.run_id, *[asset.asset_id for asset in assets]),
                    evidence={"qc_id": qc["qc_id"], "qc_status": qc["status"]},
                )
                self.service.control.record(
                    replay_run.run_id,
                    "replay.source",
                    input_refs=(source_run_id, f"content_brief:{persisted_brief.revision_id}"),
                    output_refs=tuple(asset.asset_id for asset in assets),
                    evidence={"replay_of_run_id": source_run_id, "content_brief_revision_id": persisted_brief.revision_id},
                )
                if not qc["passed"]:
                    self.content_runs.mark_failed(replay_run.run_id)
                self._json(200 if qc["passed"] else 422, {
                    "run": replay_run.to_dict(),
                    "qc": qc,
                    "replay": {
                        "source_run_id": source_run_id,
                        "replay_run_id": replay_run.run_id,
                        "content_brief_id": brief_id,
                        "content_brief_revision_id": persisted_brief.revision_id,
                        "changed_claim_ids": list(dict.fromkeys(changed)),
                    },
                })
                return

            if is_run_package_edit:
                run_id = self.path.removeprefix("/api/runs/").removesuffix("/package").strip("/")
                run = self.content_runs.get(run_id)
                if run is None:
                    self._json(404, {"error": "content run not found"})
                    return
                if run.status != "REVIEW":
                    raise ValueError("only REVIEW runs can edit the content package")
                payload = self._body()
                current = (run.result or {}).get("package")
                if not isinstance(current, dict):
                    platform = str(payload.get("platform") or platform_from_constraints(run.constraints)).strip().lower()
                    current = build_content_package(run_id=run_id, result=run.result or {}, platform=platform)
                updated_result, package = apply_package_edit(result=run.result or {}, package=current, patch=payload)
                updated = self.content_runs.save_result_preserving_status(run_id, updated_result)
                self._record_trace(run_id, stage="REVIEW", task="edit_content_package", tool="ContentPackage", action="edit", result={"status": "needs_recheck", "revision_id": package["revision"]["revision_id"]}, decision="RECHECK")
                self._json(200, {"run": updated.to_dict(), "package": package, "next": "rerun QC before approval"})
                return

            if is_run_publish:
                run_id = self.path.removeprefix("/api/runs/").removesuffix("/publish").strip("/")
                run = self.content_runs.get(run_id)
                if run is None:
                    self._json(404, {"error": "content run not found"})
                    return
                if run.status not in {"APPROVED", "EXPORTED"}:
                    raise ValueError("only APPROVED or EXPORTED runs can be published")
                payload = self._body()
                requested_publication_id = str(payload.get("publication_id") or "").strip()
                publications = self.service.control.list_publications(run_id)
                if requested_publication_id:
                    prepared = next((item for item in publications if item["publication_id"] == requested_publication_id), None)
                else:
                    prepared = next((item for item in publications if item["status"] == "PREPARED"), None)
                if prepared is None:
                    channel = str(payload.get("channel") or "local").strip()
                    if not channel:
                        raise ValueError("channel is required")
                    result = run.result or {}
                    production = result.get("production") if isinstance(result.get("production"), dict) else {}
                    assets = self.service.asset_registry.list_for_run(run_id)
                    artifact_ids = [asset.asset_id for asset in assets]
                    if not artifact_ids:
                        raise ValueError("run has no production artifacts")
                    content_ref = str(payload.get("content_ref") or (result.get("export") or {}).get("artifact") or (production.get("output") or {}).get("output_id") or run_id)
                    prepared = self.service.control.prepare_publication(
                        run_id,
                        channel,
                        content_ref,
                        {"run_id": run_id, "content_ref": content_ref, "artifact_ids": artifact_ids},
                    )
                publisher = None
                if str(prepared.get("channel") or "").lower() == "telegram":
                    publisher = (
                        FakeTelegramDistributionAdapter(str(prepared.get("destination") or "fake-chat"))
                        if os.environ.get("FACTORY_TELEGRAM_FAKE", "").strip() == "1"
                        else TelegramDistributionAdapter.from_env()
                    )
                published = self.service.control.publish(
                    prepared["publication_id"],
                    run_status=run.status,
                    url=os.environ.get("PUBLISH_URL", "").strip() or None,
                    token=os.environ.get("PUBLISH_AUTH_TOKEN"),
                    publisher=publisher,
                )
                result = self.content_runs.get(run_id).result or {}
                flow = result.get("information_flow")
                if isinstance(flow, dict):
                    artifact_ids = list((next((item for item in flow.get("publications", []) if item.get("publication_id") == prepared["publication_id"]), {}) or {}).get("artifact_ids") or [])
                    if not artifact_ids:
                        artifact_ids = [asset.asset_id for asset in self.service.asset_registry.list_for_run(run_id)]
                    result["information_flow"] = attach_publication(
                        flow,
                        publication_id=str(published["publication_id"]),
                        artifact_ids=artifact_ids,
                        channel=str(published["channel"]),
                        status=str(published["status"]),
                    )
                result["publication"] = published
                self.content_runs.mark_published(run_id, published, result=result)
                self._record_trace(
                    run_id,
                    stage="DISTRIBUTION",
                    task="publish_content",
                    tool="FactoryControlStore",
                    action="publish",
                    result={"status": published["status"], "publication_id": published["publication_id"], "channel": published["channel"]},
                    decision="ACCEPT",
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

            if self.path.startswith("/api/runs/") and self.path.endswith("/regenerate"):
                source_run_id = self.path.removeprefix("/api/runs/").removesuffix("/regenerate").strip("/")
                source_run = self.content_runs.get(source_run_id)
                if source_run is None:
                    self._json(404, {"error": "content run not found"})
                    return
                payload = self._body()
                instruction = str(payload.get("instruction", "")).strip()
                if not instruction:
                    raise ValueError("instruction is required")
                if len(instruction) > 4_000:
                    raise ValueError("instruction exceeds maximum length")
                constraints = tuple(source_run.constraints) + (f"revision instruction: {instruction}",)
                new_run = self.content_runs.create(
                    title=str(payload.get("title") or source_run.title),
                    brief=source_run.brief,
                    audience=source_run.audience,
                    goal=source_run.goal,
                    formats=source_run.formats,
                    constraints=constraints,
                )
                self.content_runs.start_planning(new_run.run_id)
                self.service.control.record(
                    new_run.run_id,
                    "regeneration.created",
                    actor="api",
                    input_refs=(source_run_id,),
                    output_refs=(new_run.run_id,),
                    evidence={"source_run_id": source_run_id, "instruction": instruction},
                )
                self._json(201, {
                    "run": new_run.to_dict(),
                    "regeneration": {
                        "source_run_id": source_run_id,
                        "instruction": instruction,
                    },
                    "next": "call /api/runs/{run_id}/factory",
                })
                return

            if is_run_factory:
                run_id = self.path.removeprefix("/api/runs/").removesuffix("/factory").strip("/")
                run = self.content_runs.get(run_id)
                if run is None:
                    self._json(404, {"error": "content run not found"})
                    return
                try:
                    if run.status in {"DRAFT", "RESEARCH_READY"}:
                        self.content_runs.start_planning(run_id)
                        run = self.content_runs.get(run_id)
                    self.service.control.record(run_id, "factory.started", status="RUNNING", actor="api")
                    self._record_trace(run_id, stage="RESEARCH", task="load_knowledge_context", tool="KnowledgeStore", action="search", result={"status": "completed"}, decision="CONTEXT_LOADED")
                    prior = self.service.knowledge.search(run.brief)
                    if not prior["claims"]:
                        prior = self.service.knowledge.accepted_for_run(run_id)
                    if not prior["claims"]:
                        if run.status in {"DRAFT", "FAILED", "PLANNING"}:
                            self.content_runs.start_execution(run_id)
                        research_result = ContentFactoryVerticalSlice(
                            knowledge_store=self.service.knowledge,
                            trace_event=lambda **event: self._record_trace(run_id, **event),
                        ).run(
                            run_id=run_id,
                            brief=run.brief,
                            formats=list(run.formats) or ["article", "social_post", "visual_card"],
                        )
                        research_dict = ContentFactoryVerticalSlice.to_dict(research_result)
                        ready = self.content_runs.save_research_result(run_id, research_dict)
                        self.service.control.record(
                            run_id,
                            "research.completed",
                            output_refs=tuple(research_dict.get("research", {}).get("knowledge_refs", {}).get("claims", {}).values()),
                            evidence=research_dict.get("quality", {}),
                        )
                        candidates = self.service.knowledge.candidates_for_run(run_id)
                        self._json(409, {
                            "error": "knowledge review required",
                            "run": ready.to_dict(),
                            "candidates": candidates,
                            "next": "promote accepted claims, then call /api/runs/{run_id}/factory again",
                        })
                        return
                    self._record_trace(run_id, stage="EDITORIAL", task="build_content_brief", tool="KnowledgeContentBuilder", action="build", result={"status": "started"})
                    try:
                        result = KnowledgeContentBuilder(self.workspace, self.service.knowledge).build(
                            run_id=run_id, topic=run.brief, audience=run.audience,
                            goal=run.goal, formats=list(run.formats), constraints=list(run.constraints),
                        )
                    except Exception as exc:
                        self._record_trace(run_id, stage="EDITORIAL", task="build_content_brief", tool="KnowledgeContentBuilder", action="build", result={"status": "failed", "error_type": type(exc).__name__}, decision="FAILED")
                        raise
                    self._record_trace(run_id, stage="EDITORIAL", task="build_content_brief", tool="KnowledgeContentBuilder", action="build", result={"status": "completed"}, decision="ACCEPT")
                    brief_revision = self.content_runs.save_content_brief(run_id, result["content_brief"])
                    result["content_brief"] = {
                        **result["content_brief"],
                        "revision_id": brief_revision.revision_id,
                    }
                    run = self.content_runs.save_result(
                        run_id,
                        {
                            **(run.result or {}),
                            "run_id": run_id,
                            "brief": run.brief,
                            **result,
                        },
                    )
                    self.service.control.record(
                        run_id,
                        "editorial.built",
                        output_refs=(f"content_brief:{brief_revision.revision_id}", "content_spec", "script", "production_plan"),
                    )
                    self.content_runs.start_producing(run_id)
                    persisted_brief = self.content_runs.get_content_brief(run_id)
                    if persisted_brief is None:
                        raise ValueError("persisted content brief not found before production")
                    result["content_brief"] = persisted_brief.payload | {"revision_id": persisted_brief.revision_id}
                    jobs = self.service.asset_jobs.create_from_plan(run_id, result["production_plan"])
                    run = self.content_runs.save_production_result(run_id, {
                        **(run.result or {}),
                        "production": {"status": "QUEUED", "job_ids": [j.job_id for j in jobs]},
                    })
                    self.service.control.record(run_id, "production.queued", output_refs=tuple(j.job_id for j in jobs))
                    self._record_trace(run_id, stage="PRODUCTION", task="execute_asset_jobs", tool="AssetExecutor", action="execute_run", result={"status": "started", "job_count": len(jobs)})
                    jobs = self.service.asset_executor.execute_run(run_id)
                    self._record_trace(run_id, stage="PRODUCTION", task="execute_asset_jobs", tool="AssetExecutor", action="execute_run", result={"status": "completed", "job_count": len(jobs)}, decision="ACCEPT")
                    run = self.content_runs.save_production_result(run_id, {
                        **(run.result or {}),
                        "production": {"status": "COMPLETED", "jobs": [j.to_dict() for j in jobs]},
                    })
                    self.service.control.record(run_id, "production.completed", output_refs=tuple(j.job_id for j in jobs))
                    assets = [self.service.asset_registry.register_completed_job(j).to_dict() for j in jobs]
                    output = ContentAssembler(self.service.asset_registry, os.environ.get("FACTORY_DATA_DIR", "./data")).assemble(
                        run_id=run_id, script=run.result.get("script") or {}, production_plan=run.result.get("production_plan") or {}
                    )
                    production_plan = run.result.get("production_plan") or {}
                    request_elements = {
                        str(request.get("script_unit_id")): list(request.get("content_element_ids") or [])
                        for request in production_plan.get("asset_requests", [])
                        if isinstance(request, dict) and request.get("script_unit_id")
                    }
                    lineage_assets = [
                        {
                            **asset,
                            "id": asset.get("asset_id"),
                            "format": asset.get("asset_type"),
                            "content_element_ids": request_elements.get(str(asset.get("script_unit_id")), []),
                        }
                        for asset in assets
                    ]
                    durable_context = self.service.knowledge.search(run.brief)
                    if not durable_context["claims"]:
                        durable_context = self.service.knowledge.accepted_for_run(run_id)
                    canonical_research = {
                        "claims": [
                            {
                                **claim,
                                "id": claim.get("claim_id"),
                            }
                            for claim in durable_context.get("claims", [])
                        ],
                        "sources": [
                            {
                                **source,
                                "id": source.get("source_id"),
                            }
                            for source in durable_context.get("sources", [])
                        ],
                        "evidence": [
                            {
                                **evidence,
                                "id": evidence.get("evidence_id"),
                            }
                            for evidence in durable_context.get("evidence", [])
                        ],
                    }
                    information_flow = build_information_flow(
                        run_id=run_id,
                        research=canonical_research,
                        package={
                            "story": {
                                "id": f"content-run:{run_id}:story",
                                "title": str((run.result.get("content_brief") or {}).get("title") or run.brief),
                                "angle": str((run.result.get("content_brief") or {}).get("angle") or ""),
                            },
                            "content_brief": run.result.get("content_brief"),
                            "package": lineage_assets,
                        },
                    ).to_dict()
                    run = self.content_runs.save_production_result(run_id, {
                        **(run.result or {}),
                        "information_flow": information_flow,
                        "production": {"status": "ASSEMBLED", "jobs": [j.to_dict() for j in jobs], "assets": assets, "output": output},
                    })
                    self.service.control.record(run_id, "assembly.completed", output_refs=(output["output_id"],))
                    self._record_trace(
                        run_id,
                        stage="QC",
                        task="quality_gate",
                        tool="QualityGate",
                        action="evaluate",
                        result={"status": "started"},
                    )
                    try:
                        qc = QualityGate().evaluate(
                            run_id=run_id,
                            script=run.result.get("script") or {},
                            production_plan=run.result.get("production_plan") or {},
                            assets=self.service.asset_registry.list_for_run(run_id),
                            output=output,
                            information_flow=run.result.get("information_flow"),
                        )
                    except Exception as exc:
                        self._record_trace(
                            run_id,
                            stage="QC",
                            task="quality_gate",
                            tool="QualityGate",
                            action="evaluate",
                            result={"status": "failed", "error_type": type(exc).__name__},
                            decision="FAILED",
                        )
                        raise
                    self._record_trace(
                        run_id,
                        stage="QC",
                        task="quality_gate",
                        tool="QualityGate",
                        action="evaluate",
                        result={
                            "status": qc["status"],
                            "passed": qc["passed"],
                            "check_count": len(qc.get("checks") or []),
                        },
                        decision="ACCEPT" if qc["passed"] else "REJECT",
                    )
                    final = {**(run.result or {}), "production": {**(run.result.get("production") or {}), "status": "READY_FOR_REVIEW" if qc["passed"] else "QC_FAILED", "qc": qc}}
                    final["package"] = build_content_package(
                        run_id=run_id,
                        result=final,
                        platform=platform_from_constraints(run.constraints),
                    )
                    final["package_revision_id"] = "r1"
                    final["package_edited"] = False
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
                    brief_revision = self.content_runs.save_content_brief(run_id, result["content_brief"])
                    updated = self.content_runs.save_result(run_id, {
                        "run_id": run_id,
                        "brief": run.brief,
                        **result,
                        "content_brief": {**result["content_brief"], "revision_id": brief_revision.revision_id},
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
                package = result.get("package")
                if isinstance(package, dict) and isinstance(package.get("qc"), dict) and package["qc"].get("status") == "NEEDS_RECHECK":
                    raise ValueError("edited content package requires QC recheck before approval")
                production = result.get("production")
                qc = production.get("qc") if isinstance(production, dict) else None
                if not isinstance(qc, dict) or qc.get("status") != "PASSED":
                    raise ValueError("only QC-passed runs can be approved")
                payload = self._body()
                decision_ref = str(payload.get("decision_ref", "")).strip()
                channel = str(payload.get("channel") or "local").strip()
                if not channel:
                    raise ValueError("channel is required")
                updated = self.content_runs.approve(run_id, decision_ref=decision_ref)
                assets = self.service.asset_registry.list_for_run(run_id)
                artifact_ids = [asset.asset_id for asset in assets]
                if not artifact_ids:
                    raise ValueError("approved run has no production artifacts")
                content_ref = str(
                    payload.get("content_ref")
                    or (result.get("export") or {}).get("artifact")
                    or (production.get("output") or {}).get("output_id")
                    or run_id
                )
                output = production.get("output") if isinstance(production.get("output"), dict) else {}
                destination = (
                    os.environ.get("TELEGRAM_CHAT_ID", "").strip()
                    if channel.lower() == "telegram"
                    else ""
                )
                if channel.lower() == "telegram" and not destination:
                    destination = "fake-chat" if os.environ.get("FACTORY_TELEGRAM_FAKE", "").strip() == "1" else ""
                if channel.lower() == "telegram" and not destination:
                    raise ValueError("TELEGRAM_CHAT_ID is required for Telegram publication")
                publication_payload = {
                    "run_id": run_id,
                    "content_ref": content_ref,
                    "content_brief_revision_id": result.get("content_brief_revision_id"),
                    "output_id": output.get("output_id"),
                    "artifact_ids": artifact_ids,
                    "destination": destination or None,
                    "output": output,
                    "media": list((result.get("package") or {}).get("media") or []),
                    "title": str((result.get("content_brief") or {}).get("title") or run.title),
                    "provenance": {
                        "run_id": run_id,
                        "content_brief_revision_id": result.get("content_brief_revision_id"),
                        "artifact_ids": artifact_ids,
                    },
                }
                publication = self.service.control.prepare_publication(
                    run_id, channel, content_ref, publication_payload, record_event=False,
                )
                self.service.control.record(
                    run_id,
                    "approval.completed",
                    status="APPROVED",
                    actor=decision_ref,
                    output_refs=(str((updated.result or {}).get("approval", {}).get("decision_ref") or ""),),
                )
                self.service.control.record(
                    run_id,
                    "publication.prepared",
                    output_refs=(str(publication["publication_id"]), channel),
                )
                flow = result.get("information_flow")
                if not isinstance(flow, dict):
                    raise ValueError("approved run is missing information flow")
                updated_flow = attach_publication(
                    flow,
                    publication_id=str(publication["publication_id"]),
                    artifact_ids=artifact_ids,
                    channel=channel,
                    status=str(publication["status"]),
                )
                current = self.content_runs.get(run_id)
                assert current is not None
                approved_result = {
                    **(current.result or {}),
                    "information_flow": updated_flow,
                    "publication": publication,
                }
                self.content_runs.save_result_preserving_status(run_id, approved_result)
                self._json(200, self.content_runs.get(run_id).to_dict())
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
                self.service.control.record(run_id, "export.completed", output_refs=(export.get("artifact", ""),), evidence=export)
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
                self.service.control.record(run_id, "assembly.completed", output_refs=(output.get("output_id", ""),))
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
                package = final_result.get("package")
                if isinstance(package, dict):
                    final_result["package"] = {
                        **package,
                        "qc": qc,
                        "approval": {},
                    }
                updated = self.content_runs.save_result(run_id, final_result) if qc["passed"] else self.content_runs.save_production_result(run_id, final_result)
                self.service.control.record(run_id, "qc.completed", status="COMPLETED" if qc["passed"] else "FAILED", output_refs=(qc.get("qc_id", ""),), evidence=qc)
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
        except IntegrationError as exc:
            status = 429 if exc.status_code == 429 else 502
            self._json(status, {"error": str(exc)})
        except Exception as exc:
            import logging
            logging.getLogger(__name__).exception("product API request failed", exc_info=exc)
            self._json(500, {"error": "internal server error"})


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
    telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    telegram_chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    factory_api_token = os.environ.get("FACTORY_API_TOKEN", "").strip()
    if telegram_token and telegram_chat_id and factory_api_token:
        ProductHandler.telegram_bot = TelegramFactoryBot(
            telegram=TelegramApi(telegram_token, telegram_chat_id),
            factory=FactoryHttpClient(f"http://127.0.0.1:{port}", factory_api_token),
            allowed_chat_id=telegram_chat_id,
        )
    else:
        ProductHandler.telegram_bot = None
    try:
        server.serve_forever()
    finally:
        server.server_close()
        service.close()


if __name__ == "__main__":
    main()
