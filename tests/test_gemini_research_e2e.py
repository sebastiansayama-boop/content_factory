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


def _request(base_url, method, path, payload=None, token="gemini-research-e2e-token"):
    from urllib.parse import urlsplit

    parts = urlsplit(base_url)
    connection = HTTPConnection(parts.hostname, parts.port, timeout=120)
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    connection.request(method, path, body=body, headers=headers)
    response = connection.getresponse()
    raw = response.read()
    connection.close()
    return response.status, json.loads(raw.decode("utf-8"))


@pytest.mark.skipif(
    os.environ.get("RUN_GEMINI_RESEARCH_E2E") != "1",
    reason="set RUN_GEMINI_RESEARCH_E2E=1 to run one real Gemini Google Search research call",
)
def test_real_gemini_research_e2e(tmp_path, monkeypatch):
    assert os.environ.get("GEMINI_API_KEY"), "GEMINI_API_KEY is required"
    monkeypatch.setenv("FACTORY_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FACTORY_PROVIDER", "gemini")
    monkeypatch.setenv("FACTORY_API_TOKEN", "gemini-research-e2e-token")
    monkeypatch.setenv("FACTORY_ACCEPTANCE_AUTHORITY", "e2e-acceptance")
    monkeypatch.setenv("FACTORY_RELEASE_AUTHORITY", "e2e-release")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
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
                    "Research how people in different historical eras imagined the future, from antiquity "
                    "through the nineteenth and twentieth centuries. Distinguish prophecy, cyclical views, "
                    "utopian projects, technological predictions, and uncertainty. Use documented historical "
                    "sources and do not invent claims."
                ),
                "audience": "general readers interested in history and ideas",
                "goal": "Build a research-grounded content package",
                "formats": ["short_video"],
                "constraints": ["documented sources", "explicit uncertainty", "no invented history"],
            },
        )
        assert status == 201, created
        run_id = created["run_id"]

        status, result = _request(base_url, "POST", f"/api/runs/{run_id}/factory")
        assert status == 409, result

        research = ((result.get("run") or {}).get("result") or {}).get("research") or {}
        sources = research.get("sources") or []
        claims = research.get("claims") or []
        serialized = json.dumps(result, ensure_ascii=False).lower()

        assert sources, result
        assert claims, result
        assert "local development fixture" not in serialized
        assert "example.invalid" not in serialized
        assert "development fixture" not in serialized

        print("GEMINI_RESEARCH_E2E_PASS")
        print("run_id:", run_id)
        print("topic:", research.get("topic"))
        print("summary:", research.get("summary"))
        print("claim_count:", len(claims))
        print("source_count:", len(sources))
        for source in sources:
            print("source:", source.get("title"), source.get("url"))
        for claim in claims:
            print("claim:", claim.get("text"))
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
        service.close()
