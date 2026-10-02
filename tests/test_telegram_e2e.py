import json
import os
import threading
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer

import pytest

from content_factory.content_run_planner import ContentRunPlanner
from content_factory.product_http import ProductHandler
from content_factory.service import FactoryService
from content_factory.workspace import ContentWorkspace


pytestmark = pytest.mark.external


def _request(base_url, method, path, payload=None, token="telegram-e2e-token"):
    from urllib.parse import urlsplit

    parts = urlsplit(base_url)
    connection = HTTPConnection(parts.hostname, parts.port, timeout=30)
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    connection.request(method, path, body=body, headers=headers)
    response = connection.getresponse()
    raw = response.read()
    connection.close()
    return response.status, json.loads(raw.decode("utf-8"))


@pytest.mark.skipif(
    os.environ.get("RUN_TELEGRAM_E2E") != "1",
    reason="set RUN_TELEGRAM_E2E=1 to publish one real integration-test message",
)
def test_real_telegram_distribution_e2e(tmp_path, monkeypatch):
    if not os.environ.get("TELEGRAM_BOT_TOKEN"):
        pytest.fail("TELEGRAM_BOT_TOKEN is required")
    if not os.environ.get("TELEGRAM_CHAT_ID"):
        pytest.fail("TELEGRAM_CHAT_ID is required")
    if not os.environ.get("GEMINI_API_KEY"):
        pytest.fail("GEMINI_API_KEY is required")

    monkeypatch.setenv("FACTORY_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FACTORY_PROVIDER", "gemini")
    monkeypatch.setenv("FACTORY_ASSET_PROVIDER", "openverse")
    monkeypatch.setenv("FACTORY_API_TOKEN", "telegram-e2e-token")
    monkeypatch.delenv("FACTORY_TELEGRAM_FAKE", raising=False)
    monkeypatch.delenv("PUBLISH_URL", raising=False)
    monkeypatch.delenv("PUBLISH_AUTH_TOKEN", raising=False)

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
        status, created = _request(
            base_url,
            "POST",
            "/api/runs",
            {
                "title": "Evidence-grounded Telegram integration test",
                "brief": "Why do unrelated animals sometimes evolve similar traits? Create one short evidence-grounded Telegram post.",
                "audience": "general audience",
                "goal": "verify Gemini content generation and real Telegram publication",
                "formats": ["social_post"],
                "constraints": ["short", "plain text", "language: Русский"],
            },
        )
        assert status == 201, created
        run = created.get("run", created)
        assert isinstance(run, dict), created
        run_id = run["run_id"]

        status, first_factory = _request(base_url, "POST", f"/api/runs/{run_id}/factory")
        assert status == 409, first_factory
        candidates = first_factory["candidates"]
        assert candidates, first_factory
        claim_id = candidates[0]["claim_id"]
        claim_text = str(candidates[0]["text"]).strip()
        assert claim_text

        status, promoted = _request(
            base_url,
            "POST",
            f"/api/knowledge/{claim_id}/promote",
            {"decision_ref": "telegram-e2e-human-test"},
        )
        assert status == 200, promoted
        assert promoted["status"] == "ACCEPTED"

        status, factory = _request(base_url, "POST", f"/api/runs/{run_id}/factory")
        assert status == 200, factory
        assert factory["qc"]["status"] == "PASSED"
        result = factory["run"]["result"]
        assert claim_id in result["content_spec"]["claim_refs"]
        media = list((result.get("package") or {}).get("media") or [])
        assert media, result.get("package")
        assert any(item.get("type") == "image" and item.get("origin") == "openverse" for item in media), media
        script_units = result["script"]["units"]
        assert any(claim_id in (unit.get("claim_refs") or []) for unit in script_units)

        status, approved = _request(
            base_url,
            "POST",
            f"/api/runs/{run_id}/approve",
            {
                "decision_ref": "telegram-e2e-human-test",
                "channel": "telegram",
            },
        )
        assert status == 200, approved
        assert approved["status"] == "APPROVED"

        publication = approved["result"]["publication"]
        assert publication["status"] == "PREPARED"
        assert publication["channel"] == "telegram"
        assert publication["destination"] == os.environ["TELEGRAM_CHAT_ID"]

        status, published = _request(
            base_url,
            "POST",
            f"/api/runs/{run_id}/publish",
            {"publication_id": publication["publication_id"]},
        )
        assert status == 200, published
        assert published["status"] == "PUBLISHED"
        assert published["channel"] == "telegram"
        assert published["external_id"]
        assert published["external_url"]
        assert published["published_at"]
        assert published["response"]["mode"] == "telegram"
        assert published["response"]["telegram_ok"] is True
        assert published["response"]["message_id"] == int(published["external_id"])
        assert published["response"]["media_count"] >= 1, published["response"]
        assert any(item.get("origin") == "openverse" for item in published["response"].get("media") or []), published["response"]
        published_text = str(published["response"]["text"])
        assert published_text.strip()
        assert "Development fixture claim" not in published_text
        assert any(ch in published_text for ch in "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"), published_text

        status, final = _request(base_url, "GET", f"/api/runs/{run_id}")
        assert status == 200, final
        assert final["status"] == "PUBLISHED"
        assert final["result"]["publication"]["publication_id"] == publication["publication_id"]
        assert final["result"]["information_flow"]["publications"][0]["status"] == "PUBLISHED"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
        service.close()
