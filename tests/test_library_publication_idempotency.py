from __future__ import annotations

import json
import threading
from http.server import ThreadingHTTPServer

from content_factory.content_run_planner import ContentRunPlanner
from content_factory.product_http import ProductHandler
from content_factory.service import FactoryService
from content_factory.workspace import ContentWorkspace
from tests.test_telegram_publication_smoke import _create_prepared_run, _request


def test_publish_existing_library_run_is_idempotent(tmp_path, monkeypatch):
    monkeypatch.setenv("FACTORY_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FACTORY_API_TOKEN", "telegram-publication-smoke-token")
    monkeypatch.setenv("FACTORY_TELEGRAM_FAKE", "1")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "fake-chat")

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
        run, _asset = _create_prepared_run(service, tmp_path, with_media=False)

        status, approved = _request(
            base_url,
            "POST",
            f"/api/runs/{run.run_id}/approve",
            {"decision_ref": "library-idempotency-test", "channel": "telegram"},
        )
        assert status == 200, approved
        publication = approved["result"]["publication"]

        status, first = _request(
            base_url,
            "POST",
            f"/api/runs/{run.run_id}/publish",
            {"publication_id": publication["publication_id"]},
        )
        assert status == 200, first
        assert first["status"] == "PUBLISHED"
        external_id = first["external_id"]

        status, second = _request(
            base_url,
            "POST",
            f"/api/runs/{run.run_id}/publish",
            {"publication_id": publication["publication_id"]},
        )
        assert status == 200, second
        assert second["status"] == "PUBLISHED"
        assert second["external_id"] == external_id
        assert second["idempotent"] is True

        final = service.content_runs.get(run.run_id)
        assert final is not None
        assert final.status == "PUBLISHED"
        publications = service.control.list_publications(run.run_id)
        assert len([item for item in publications if item["status"] == "PUBLISHED"]) == 1
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
        service.close()
