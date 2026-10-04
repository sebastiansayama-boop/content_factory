from __future__ import annotations

import json
import os
import sys
import tempfile
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

from content_factory.content_run_planner import ContentRunPlanner
from content_factory.product_http import ProductHandler
from content_factory.service import FactoryService
from content_factory.workspace import ContentWorkspace
import urllib.request
import urllib.error

def _request(base_url: str, method: str, path: str, payload: dict, token: str = "library-publish-token"):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        base_url + path,
        data=body,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return int(response.status), json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8")
        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            body = {"error": raw}
        return int(exc.code), body


ROOT = Path(__file__).resolve().parents[1]
LIBRARY_PATH = ROOT / "library" / "telegram" / "future-series.json"


def _prepare_run(service: FactoryService, episode: dict, workdir: Path, previous_run_id: str | None):
    run = service.content_runs.create(
        title=episode["title"],
        brief=episode["title"],
        audience="Telegram readers",
        goal="publish the next episode of the historical future series",
        formats=("social_post",),
        constraints=("language: Русский",),
    )
    service.content_runs.start_planning(run.run_id)

    artifact_path = workdir / f"{run.run_id}.txt"
    artifact_path.write_text(episode["text"], encoding="utf-8")
    request = {
        "asset_request_id": f"library-artifact-{run.run_id}",
        "script_unit_id": "telegram-text",
        "type": "text",
        "claim_refs": [claim["id"] for claim in episode["claims"]],
        "evidence_refs": [item["id"] for item in episode["evidence"]],
        "visual_intent": "text publication artifact",
        "acceptance_criteria": ["exists"],
    }
    jobs = service.asset_jobs.create_from_plan(run.run_id, {"asset_requests": [request]})
    job = jobs[0]
    service.asset_jobs.mark_running(job.job_id)
    service.asset_jobs.complete(
        job.job_id,
        {
            "asset_id": f"library-artifact-{run.run_id}",
            "provider": "library",
            "path": str(artifact_path),
            "metadata": {"origin": "telegram-library", "asset_type": "text"},
        },
    )
    asset = service.asset_registry.register_completed_job(service.asset_jobs.get(job.job_id))

    package = {
        "title": episode["title"],
        "text": episode["text"],
        "media": [],
        "claims": episode["claims"],
        "sources": episode["sources"],
        "evidence": episode["evidence"],
        "qc": {"status": "PASSED", "passed": True, "qc_id": f"qc-{run.run_id}"},
        "series": {
            "series_id": episode["story_state"]["series_id"],
            "title": episode["story_state"]["title"],
            "episode": episode["episode"],
            "previous_run_id": previous_run_id,
            "central_question": episode["story_state"]["central_question"],
            "unresolved": episode["story_state"]["unresolved"],
            "next_required_transition": episode["story_state"]["next_required_transition"],
            "story_state": episode["story_state"],
        },
    }
    result = {
        "run_id": run.run_id,
        "brief": run.brief,
        "content_brief": {
            "brief_id": f"brief-{run.run_id}",
            "revision_id": f"brief-{run.run_id}-r1",
            "title": episode["title"],
        },
        "production": {
            "status": "READY_FOR_REVIEW",
            "output": {"output_id": f"output-{run.run_id}"},
            "qc": {"status": "PASSED", "passed": True, "qc_id": f"qc-{run.run_id}"},
            "assets": [asset.to_dict()],
        },
        "package": package,
        "information_flow": {
            "artifacts": [{
                "artifact_id": asset.asset_id,
                "format": "text",
                "content_element_ids": [],
                "claim_ids": [claim["id"] for claim in episode["claims"]],
                "evidence_ids": [item["id"] for item in episode["evidence"]],
            }],
            "publications": [],
            "edges": [],
        },
    }
    return service.content_runs.save_result(run.run_id, result)


def main() -> int:
    data = json.loads(LIBRARY_PATH.read_text(encoding="utf-8"))
    episodes = {int(item["episode"]): item for item in data["episodes"]}
    if 6 not in episodes or 7 not in episodes or 8 not in episodes or 9 not in episodes:
        raise RuntimeError("library must contain Episodes 6 and 7")

    for item in episodes.values():
        item["story_state"]["series_id"] = data["series_id"]
        item["story_state"]["title"] = data["title"]

    if not os.environ.get("TELEGRAM_BOT_TOKEN") or not os.environ.get("TELEGRAM_CHAT_ID"):
        raise RuntimeError("Telegram credentials are required")
    if os.environ.get("FACTORY_TELEGRAM_FAKE") == "1":
        raise RuntimeError("real Telegram publication required; FACTORY_TELEGRAM_FAKE must be unset")

    with tempfile.TemporaryDirectory(prefix="content-factory-library-") as temp:
        data_dir = Path(temp) / "data"
        data_dir.mkdir()
        os.environ["FACTORY_DATA_DIR"] = str(data_dir)
        os.environ["FACTORY_API_TOKEN"] = "library-publish-token"

        service = FactoryService()
        ProductHandler.service = service
        ProductHandler.workspace = ContentWorkspace(service)
        ProductHandler.content_runs = service.content_runs
        ProductHandler.content_run_planner = ContentRunPlanner(ProductHandler.workspace)
        ProductHandler._rate_limited = staticmethod(lambda *args, **kwargs: False)

        server = ThreadingHTTPServer(("127.0.0.1", 0), ProductHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base_url = f"http://127.0.0.1:{server.server_port}"

        try:
            ep6 = _prepare_run(service, episodes[6], data_dir, None)
            service.content_runs.approve(ep6.run_id, decision_ref="library-episode-6-import")
            service.content_runs.mark_published(
                ep6.run_id,
                {"status": "PUBLISHED", "channel": "telegram", "external_id": "102"},
            )

            ep7 = _prepare_run(service, episodes[7], data_dir, ep6.run_id)
            status, approved = _request(
                base_url,
                "POST",
                f"/api/runs/{ep7.run_id}/approve",
                {"decision_ref": "library-episode-7-approval", "channel": "telegram"},
            )
            if status != 200:
                raise RuntimeError(f"approval failed: {approved}")

            publication = approved["result"]["publication"]
            status, published = _request(
                base_url,
                "POST",
                f"/api/runs/{ep7.run_id}/publish",
                {"publication_id": publication["publication_id"], "actor_id": "library-publisher"},
            )
            if status != 200:
                raise RuntimeError(f"Telegram publication failed: {published}")
            if published.get("status") != "PUBLISHED" or not published.get("external_id"):
                raise RuntimeError(f"Telegram publication not confirmed: {published}")

            final = service.content_runs.get(ep7.run_id)
            if final is None or final.status != "PUBLISHED":
                raise RuntimeError("ContentRun did not reach PUBLISHED")

            status, replay = _request(
                base_url,
                "POST",
                f"/api/runs/{ep7.run_id}/publish",
                {"publication_id": publication["publication_id"], "actor_id": "library-publisher"},
            )
            if status != 200 or replay.get("idempotent") is not True:
                raise RuntimeError(f"idempotency check failed: {replay}")
            if replay.get("external_id") != published.get("external_id"):
                raise RuntimeError("idempotency returned a different external_id")

            ep8 = _prepare_run(service, episodes[8], data_dir, ep7.run_id)
            status, approved8 = _request(
                base_url,
                "POST",
                f"/api/runs/{ep8.run_id}/approve",
                {"decision_ref": "library-episode-8-approval", "channel": "telegram"},
            )
            if status != 200:
                raise RuntimeError(f"Episode 8 approval failed: {approved8}")

            publication8 = approved8["result"]["publication"]
            status, published8 = _request(
                base_url,
                "POST",
                f"/api/runs/{ep8.run_id}/publish",
                {"publication_id": publication8["publication_id"], "actor_id": "library-publisher"},
            )
            if status != 200 or published8.get("status") != "PUBLISHED" or not published8.get("external_id"):
                raise RuntimeError(f"Episode 8 Telegram publication failed: {published8}")

            final8 = service.content_runs.get(ep8.run_id)
            if final8 is None or final8.status != "PUBLISHED":
                raise RuntimeError("Episode 8 ContentRun did not reach PUBLISHED")

            status, replay8 = _request(
                base_url,
                "POST",
                f"/api/runs/{ep8.run_id}/publish",
                {"publication_id": publication8["publication_id"], "actor_id": "library-publisher"},
            )
            if status != 200 or replay8.get("idempotent") is not True:
                raise RuntimeError(f"Episode 8 idempotency check failed: {replay8}")
            if replay8.get("external_id") != published8.get("external_id"):
                raise RuntimeError("Episode 8 idempotency returned a different external_id")

            print(f"TELEGRAM_EPISODE_8_RUN_ID={ep8.run_id}")
            print(f"TELEGRAM_EPISODE_8_MESSAGE_ID={published8['external_id']}")
            print("TELEGRAM_EPISODE_8_STATUS=PUBLISHED")
            print("TELEGRAM_EPISODE_8_IDEMPOTENCY=PASS")
            ep9 = _prepare_run(service, episodes[9], data_dir, ep8.run_id)
            status, approved9 = _request(
                base_url,
                "POST",
                f"/api/runs/{ep9.run_id}/approve",
                {"decision_ref": "library-episode-9-approval", "channel": "telegram"},
            )
            if status != 200:
                raise RuntimeError(f"Episode 9 approval failed: {approved9}")

            publication9 = approved9["result"]["publication"]
            status, published9 = _request(
                base_url,
                "POST",
                f"/api/runs/{ep9.run_id}/publish",
                {"publication_id": publication9["publication_id"], "actor_id": "library-publisher"},
            )
            if status != 200 or published9.get("status") != "PUBLISHED" or not published9.get("external_id"):
                raise RuntimeError(f"Episode 9 Telegram publication failed: {published9}")

            final9 = service.content_runs.get(ep9.run_id)
            if final9 is None or final9.status != "PUBLISHED":
                raise RuntimeError("Episode 9 ContentRun did not reach PUBLISHED")

            status, replay9 = _request(
                base_url,
                "POST",
                f"/api/runs/{ep9.run_id}/publish",
                {"publication_id": publication9["publication_id"], "actor_id": "library-publisher"},
            )
            if status != 200 or replay9.get("idempotent") is not True:
                raise RuntimeError(f"Episode 9 idempotency check failed: {replay9}")
            if replay9.get("external_id") != published9.get("external_id"):
                raise RuntimeError("Episode 9 idempotency returned a different external_id")

            print(f"TELEGRAM_EPISODE_9_RUN_ID={ep9.run_id}")
            print(f"TELEGRAM_EPISODE_9_MESSAGE_ID={published9['external_id']}")
            print("TELEGRAM_EPISODE_9_STATUS=PUBLISHED")
            print("TELEGRAM_EPISODE_9_IDEMPOTENCY=PASS")

            print(f"TELEGRAM_EPISODE_7_RUN_ID={ep7.run_id}")
            print(f"TELEGRAM_EPISODE_7_MESSAGE_ID={published['external_id']}")
            print("TELEGRAM_EPISODE_7_STATUS=PUBLISHED")
            print("TELEGRAM_EPISODE_7_IDEMPOTENCY=PASS")
            return 0
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)
            service.close()


if __name__ == "__main__":
    sys.exit(main())
