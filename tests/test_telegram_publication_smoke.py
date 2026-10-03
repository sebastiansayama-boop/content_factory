from __future__ import annotations

import os
import threading
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer

import pytest
from PIL import Image

from content_factory.content_run_planner import ContentRunPlanner
from content_factory.product_http import ProductHandler
from content_factory.service import FactoryService
from content_factory.workspace import ContentWorkspace


pytestmark = pytest.mark.external


def _request(base_url: str, method: str, path: str, payload=None):
    from urllib.parse import urlsplit
    parts = urlsplit(base_url)
    connection = HTTPConnection(parts.hostname, parts.port, timeout=120)
    import json
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {
        "Authorization": "Bearer telegram-publication-smoke-token",
        "Content-Type": "application/json",
    }
    connection.request(method, path, body=body, headers=headers)
    response = connection.getresponse()
    raw = response.read()
    status = response.status
    connection.close()
    return status, json.loads(raw.decode("utf-8"))


def _create_prepared_run(service: FactoryService, tmp_path, *, with_media: bool):
    run = service.content_runs.create(
        title="Telegram publication smoke",
        brief="Prepared publication smoke test.",
        audience="general",
        goal="verify real Telegram publication",
        formats=("social_post",),
        constraints=("language: Русский",),
    )
    service.content_runs.start_planning(run.run_id)

    request = {
        "asset_request_id": "asset-request-smoke-1",
        "script_unit_id": "unit-1",
        "type": "visual",
        "claim_refs": [],
        "evidence_refs": [],
        "visual_intent": "publication smoke image",
        "acceptance_criteria": ["exists"],
    }
    jobs = service.asset_jobs.create_from_plan(
        run.run_id,
        {"asset_requests": [request]},
    )
    asset_path = tmp_path / f"{run.run_id}.jpg"
    Image.new("RGB", (64, 64), (120, 180, 220)).save(asset_path, format="JPEG")
    job = jobs[0]
    service.asset_jobs.mark_running(job.job_id)
    service.asset_jobs.complete(
        job.job_id,
        {
            "asset_id": f"asset-smoke-{run.run_id}",
            "provider": "test",
            "path": str(asset_path),
            "metadata": {"origin": "smoke", "asset_type": "image"},
        },
    )
    asset = service.asset_registry.register_completed_job(
        service.asset_jobs.get(job.job_id)
    )

    media = []
    if with_media:
        media.append(
            {
                "media_id": asset.asset_id,
                "type": "image",
                "uri": str(asset_path),
                "origin": "test",
                "source": {"id": "telegram-publication-smoke"},
                "license": "test",
            }
        )

    result = {
        "run_id": run.run_id,
        "brief": run.brief,
        "content_brief": {
            "brief_id": f"brief-{run.run_id}",
            "revision_id": f"brief-{run.run_id}-r1",
            "title": "Telegram publication smoke",
        },
        "production": {
            "status": "READY_FOR_REVIEW",
            "output": {"output_id": f"output-{run.run_id}"},
            "qc": {"status": "PASSED", "passed": True, "qc_id": f"qc-{run.run_id}"},
        },
        "package": {
            "title": "Telegram publication smoke",
            "text": "Реальный Telegram publication smoke test.",
            "media": media,
            "claims": [],
            "evidence": [],
            "qc": {"status": "PASSED"},
        },
        "information_flow": {
            "artifacts": [{"artifact_id": asset.asset_id, "format": "image", "content_element_ids": [], "claim_ids": [], "evidence_ids": []}],
            "publications": [],
            "edges": [],
        },
    }
    return service.content_runs.save_result(run.run_id, result), asset


@pytest.mark.skipif(
    os.environ.get("RUN_TELEGRAM_E2E") != "1",
    reason="set RUN_TELEGRAM_E2E=1 for a real Telegram publication smoke",
)
def test_real_telegram_publication_text_smoke(tmp_path, monkeypatch):
    if not os.environ.get("TELEGRAM_BOT_TOKEN"):
        pytest.fail("TELEGRAM_BOT_TOKEN is required")
    if not os.environ.get("TELEGRAM_CHAT_ID"):
        pytest.fail("TELEGRAM_CHAT_ID is required")

    monkeypatch.setenv("FACTORY_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FACTORY_API_TOKEN", "telegram-publication-smoke-token")
    monkeypatch.delenv("FACTORY_TELEGRAM_FAKE", raising=False)

    service = FactoryService()
    ProductHandler.service = service
    ProductHandler.workspace = ContentWorkspace(service)
    ProductHandler.content_runs = service.content_runs
    ProductHandler.content_run_planner = ContentRunPlanner(ProductHandler.workspace)
    monkeypatch.setattr(ProductHandler, "_rate_limited", lambda *args, **kwargs: False)

    server = ThreadingHTTPServer(("127.0.0.1", 0), ProductHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_port}"

    try:
        run, asset = _create_prepared_run(service, tmp_path, with_media=False)

        status, approved = _request(
            base_url,
            "POST",
            f"/api/runs/{run.run_id}/approve",
            {"decision_ref": "telegram-publication-smoke-text", "channel": "telegram"},
        )
        assert status == 200, approved
        publication = approved["result"]["publication"]
        assert publication["status"] == "PREPARED"
        assert publication["destination"] == os.environ["TELEGRAM_CHAT_ID"]

        status, published = _request(
            base_url,
            "POST",
            f"/api/runs/{run.run_id}/publish",
            {"publication_id": publication["publication_id"]},
        )
        assert status == 200, published
        assert published["status"] == "PUBLISHED"
        assert published["channel"] == "telegram"
        assert published["external_id"]
        assert published["external_url"]
        assert published["response"]["telegram_ok"] is True
        assert published["response"]["media_count"] == 0
        assert published["response"]["text"].strip() == "Telegram publication smoke"

        final = service.content_runs.get(run.run_id)
        assert final is not None
        assert final.status == "PUBLISHED"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
        service.close()


@pytest.mark.skipif(
    os.environ.get("RUN_TELEGRAM_E2E") != "1",
    reason="set RUN_TELEGRAM_E2E=1 for a real Telegram publication smoke",
)
def test_real_telegram_publication_media_smoke(tmp_path, monkeypatch):
    if not os.environ.get("TELEGRAM_BOT_TOKEN"):
        pytest.fail("TELEGRAM_BOT_TOKEN is required")
    if not os.environ.get("TELEGRAM_CHAT_ID"):
        pytest.fail("TELEGRAM_CHAT_ID is required")

    monkeypatch.setenv("FACTORY_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FACTORY_API_TOKEN", "telegram-publication-smoke-token")
    monkeypatch.delenv("FACTORY_TELEGRAM_FAKE", raising=False)

    service = FactoryService()
    ProductHandler.service = service
    ProductHandler.workspace = ContentWorkspace(service)
    ProductHandler.content_runs = service.content_runs
    ProductHandler.content_run_planner = ContentRunPlanner(ProductHandler.workspace)
    monkeypatch.setattr(ProductHandler, "_rate_limited", lambda *args, **kwargs: False)

    server = ThreadingHTTPServer(("127.0.0.1", 0), ProductHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_port}"

    try:
        run, asset = _create_prepared_run(service, tmp_path, with_media=True)

        status, approved = _request(
            base_url,
            "POST",
            f"/api/runs/{run.run_id}/approve",
            {"decision_ref": "telegram-publication-smoke-media", "channel": "telegram"},
        )
        assert status == 200, approved
        publication = approved["result"]["publication"]
        assert publication["status"] == "PREPARED"

        status, published = _request(
            base_url,
            "POST",
            f"/api/runs/{run.run_id}/publish",
            {"publication_id": publication["publication_id"]},
        )
        assert status == 200, published
        assert published["status"] == "PUBLISHED"
        assert published["channel"] == "telegram"
        assert published["response"]["telegram_ok"] is True
        assert published["response"]["media_count"] == 1
        assert published["response"]["media"][0]["media_id"] == asset.asset_id
        assert published["response"]["media"][0]["origin"] == "test"

        final = service.content_runs.get(run.run_id)
        assert final is not None
        assert final.status == "PUBLISHED"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
        service.close()
