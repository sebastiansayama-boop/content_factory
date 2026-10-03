from __future__ import annotations

import os
import threading
from http.server import ThreadingHTTPServer

import pytest

from tests.test_telegram_publication_smoke import _create_prepared_run, _request
from content_factory.content_run_planner import ContentRunPlanner
from content_factory.product_http import ProductHandler
from content_factory.service import FactoryService
from content_factory.workspace import ContentWorkspace

pytestmark = pytest.mark.external

def test_real_telegram_historical_material_smoke(tmp_path, monkeypatch):
    if os.environ.get("RUN_TELEGRAM_E2E") != "1":
        pytest.skip("set RUN_TELEGRAM_E2E=1 for a real Telegram publication smoke")
    if not os.environ.get("TELEGRAM_BOT_TOKEN") or not os.environ.get("TELEGRAM_CHAT_ID"):
        pytest.fail("Telegram credentials are required")

    monkeypatch.setenv("FACTORY_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FACTORY_API_TOKEN", "telegram-" + "publication-smoke-token")
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
        run, _asset = _create_prepared_run(service, tmp_path, with_media=True)
        result = dict(run.result or {})
        result["brief"] = "Малоизвестные факты из истории человечества"
        result["content_brief"] = {**result["content_brief"], "title": "Малоизвестные факты из истории человечества"}
        result["package"] = {
            **result["package"],
            "title": "Малоизвестные факты из истории человечества",
            "text": "История полна фактов, которые редко попадают в учебники. Этот материал проверяет публикационный путь Content Factory на настоящей теме.",
        }
        service.content_runs.save_result(run.run_id, result)

        status, approved = _request(base_url, "POST", f"/api/runs/{run.run_id}/approve", {
            "decision_ref": "telegram-historical-material-approver",
            "actor_id": "telegram-historical-material-actor",
            "channel": "telegram",
        })
        assert status == 200, approved
        publication = approved["result"]["publication"]

        status, published = _request(base_url, "POST", f"/api/runs/{run.run_id}/publish", {
            "publication_id": publication["publication_id"],
            "actor_id": "telegram-historical-material-actor",
        })
        assert status == 200, published
        assert published["status"] == "PUBLISHED"
        assert published["channel"] == "telegram"
        assert published["response"]["telegram_ok"] is True
        assert published["response"]["text"].startswith("История полна фактов")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
        service.close()
