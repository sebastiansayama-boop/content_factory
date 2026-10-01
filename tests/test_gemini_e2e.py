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


def _request(base_url, method, path, payload=None, token="gemini-e2e-token"):
    from urllib.parse import urlsplit

    parts = urlsplit(base_url)
    connection = HTTPConnection(parts.hostname, parts.port, timeout=90)
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
    os.environ.get("RUN_GEMINI_E2E") != "1",
    reason="set RUN_GEMINI_E2E=1 to run one real Gemini Content Factory generation",
)
def test_real_gemini_content_factory_e2e(tmp_path, monkeypatch):
    if not os.environ.get("GEMINI_API_KEY"):
        pytest.fail("GEMINI_API_KEY is required")

    monkeypatch.setenv("FACTORY_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FACTORY_PROVIDER", "gemini")
    monkeypatch.setenv("FACTORY_API_TOKEN", "gemini-e2e-token")
    monkeypatch.setenv("FACTORY_ACCEPTANCE_AUTHORITY", "e2e-acceptance")
    monkeypatch.setenv("FACTORY_RELEASE_AUTHORITY", "e2e-release")
    monkeypatch.delenv("FACTORY_TELEGRAM_FAKE", raising=False)
    monkeypatch.delenv("PUBLISH_URL", raising=False)
    monkeypatch.delenv("PUBLISH_AUTH_TOKEN", raising=False)

    service = FactoryService()
    ProductHandler.service = service
    ProductHandler.workspace = ContentWorkspace(service)
    ProductHandler.content_runs = service.content_runs
    ProductHandler.content_run_planner = ContentRunPlanner(ProductHandler.workspace)
    monkeypatch.setattr(ProductHandler, "_rate_limited", lambda *args, **kwargs: False)
    monkeypatch.setattr(ProductHandler, "_auth_failure_limited", lambda *args, **kwargs: False)

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
                "title": "How people imagined the future",
                "brief": (
                    "Create a fact-based short-form content piece about how people in different eras "
                    "imagined the future, distinguishing documented historical evidence from uncertainty. "
                    "Use the supplied research pipeline and do not invent historical claims."
                ),
                "audience": "general readers interested in history and ideas",
                "goal": "Create a publishable short-form content asset",
                "formats": ["short_video"],
                "constraints": ["clear structure", "no unsupported claims"],
            },
        )
        assert status == 201, created
        run_id = created["run_id"]

        status, first_factory = _request(
            base_url,
            "POST",
            f"/api/runs/{run_id}/factory",
        )

        assert status == 409, first_factory
        candidates = first_factory.get("candidates") or []
        assert candidates, first_factory

        claim_id = candidates[0]["claim_id"]
        status, promoted = _request(
            base_url,
            "POST",
            f"/api/knowledge/{claim_id}/promote",
            {"decision_ref": "gemini-e2e-human-test"},
        )
        assert status == 200, promoted
        assert promoted["status"] == "ACCEPTED"

        status, factory = _request(
            base_url,
            "POST",
            f"/api/runs/{run_id}/factory",
        )
        assert status == 200, factory

        run = factory["run"]
        result = run.get("result") or {}
        script = result.get("script") or {}
        units = script.get("units") or []
        production = result.get("production") or {}
        qc = production.get("qc") or {}

        assert run["status"] == "REVIEW", run
        assert units and any(str(unit.get("text", "")).strip() for unit in units), script
        assert production["status"] == "READY_FOR_REVIEW", production
        assert qc["passed"] is True, qc

        print("GEMINI_E2E_PASS")
        print("run_id:", run_id)
        print("script_units:", len(units))
        print("qc_status:", qc.get("status"))
        print("script:")
        for unit in units:
            text = str(unit.get("text", "")).strip()
            if text:
                print(text)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
        service.close()
