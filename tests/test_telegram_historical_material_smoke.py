from __future__ import annotations

import json
import os
import threading
from http.server import ThreadingHTTPServer

import pytest

from tests.test_telegram_publication_smoke import _create_prepared_run, _request
from content_factory.content_run_planner import ContentRunPlanner
from content_factory.product_http import ProductHandler
from content_factory.service import FactoryService
from content_factory.workspace import ContentWorkspace
from content_factory.providers.gemini import FreeWebGeminiAdapter

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
        run, _asset = _create_prepared_run(service, tmp_path, with_media=False)
        result = dict(run.result or {})
        result["brief"] = "Малоизвестные факты из истории человечества"
        result["content_brief"] = {
            **result["content_brief"],
            "title": "Малоизвестные факты из истории человечества",
        }
        result["package"] = {
            **result["package"],
            "title": "Малоизвестные факты из истории человечества",
            "text": (
                "История полна фактов, которые редко попадают в учебники. "
                "Этот материал проверяет публикационный путь Content Factory на настоящей теме."
            ),
            "media": [],
        }
        service.content_runs.save_result(run.run_id, result)

        status, approved = _request(
            base_url,
            "POST",
            f"/api/runs/{run.run_id}/approve",
            {
                "decision_ref": "telegram-historical-material-approver",
                "actor_id": "telegram-historical-material-actor",
                "channel": "telegram",
            },
        )
        assert status == 200, approved
        publication = approved["result"]["publication"]
        assert publication["media"] == []

        status, published = _request(
            base_url,
            "POST",
            f"/api/runs/{run.run_id}/publish",
            {
                "publication_id": publication["publication_id"],
                "actor_id": "telegram-historical-material-actor",
            },
        )
        assert status == 200, published
        assert published["status"] == "PUBLISHED"
        assert published["channel"] == "telegram"
        assert published["response"]["telegram_ok"] is True
        assert published["response"]["media_count"] == 0
        assert published["response"]["text"].startswith("История полна фактов")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
        service.close()

def test_real_telegram_generated_historical_material_smoke(tmp_path, monkeypatch):
    if os.environ.get("RUN_TELEGRAM_E2E") != "1":
        pytest.skip("set RUN_TELEGRAM_E2E=1 for a real Telegram publication smoke")
    if not os.environ.get("TELEGRAM_BOT_TOKEN") or not os.environ.get("TELEGRAM_CHAT_ID"):
        pytest.fail("Telegram credentials are required")
    if not os.environ.get("GEMINI_API_KEY"):
        pytest.fail("GEMINI_API_KEY is required for generated Telegram smoke")

    monkeypatch.setenv("FACTORY_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FACTORY_API_TOKEN", "telegram-generated-publication-smoke-token")
    monkeypatch.delenv("FACTORY_TELEGRAM_FAKE", raising=False)

    research = FreeWebGeminiAdapter()
    topic = "Малоизвестные факты из истории человечества"
    research_prompt = f"""Research the topic and return ONLY JSON:
{{"topic":"string","summary":"string","claims":[{{"id":"claim-1","text":"atomic factual claim","source_ids":["source-1"],"evidence_ids":["evidence-1"]}}],"sources":[{{"id":"source-1","title":"string","url":"https://..."}}],"evidence":[{{"id":"evidence-1","source_id":"source-1","excerpt":"short supporting passage"}}]}}
Use several distinct historical examples from different periods or regions. Keep claims bounded and source-backed. Do not invent facts.
TOPIC:
{topic}
"""
    research_result = research.research(research_prompt)
    assert 200 <= research_result.status_code < 300
    research_payload = json.loads(research.text(research_result))
    claims = research_payload["claims"]
    evidence = research_payload["evidence"]
    assert len(claims) >= 3
    assert evidence

    knowledge = json.dumps({"claims": claims[:6], "evidence": evidence[:12]}, ensure_ascii=False)
    generation_prompt = f"""Write one finished Telegram publication in Russian.
Return ONLY JSON: {{"title":"string","content":"string"}}.
Length: 700-1200 characters.
One coherent publication, not a list.
Start with a concrete historical fact, scene, person, place, date, object, or action. Do not start with generic phrases such as "История полна", "Мало кто знает", "Вы знали?", "На протяжении веков".
Use only the supplied claims and evidence. Preserve uncertainty and scope. Do not invent facts.
Use natural contemporary Russian, varied sentence length, concrete details, and a non-generic ending.
Do not use the em dash character.
TOPIC:
{topic}
ACCEPTED KNOWLEDGE:
{knowledge}
"""
    generated = research.research(generation_prompt)
    assert 200 <= generated.status_code < 300
    generated_payload = json.loads(research.text(generated))
    generated_text = str(generated_payload["content"]).strip()
    assert 700 <= len(generated_text) <= 1200
    assert "—" not in generated_text
    assert not generated_text.startswith(("История полна", "Мало кто знает", "Вы знали?", "На протяжении веков"))

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
        run = service.content_runs.create(
            title=topic,
            brief=topic,
            audience="general",
            goal="verify generated Telegram publication",
            formats=("social_post",),
            constraints=("language: Русский",),
        )
        service.content_runs.start_planning(run.run_id)
        result = {
            "run_id": run.run_id,
            "brief": topic,
            "content_brief": {
                "brief_id": f"brief-{run.run_id}",
                "revision_id": f"brief-{run.run_id}-r1",
                "title": topic,
            },
            "production": {
                "status": "READY_FOR_REVIEW",
                "output": {"output_id": f"output-{run.run_id}"},
                "qc": {"status": "PASSED", "passed": True, "qc_id": f"qc-{run.run_id}"},
            },
            "package": {
                "title": str(generated_payload.get("title") or topic),
                "text": generated_text,
                "media": [],
                "claims": claims,
                "evidence": evidence,
                "qc": {"status": "PASSED"},
            },
            "information_flow": {"artifacts": [], "publications": [], "edges": []},
        }
        service.content_runs.save_result(run.run_id, result)

        status, approved = _request(
            base_url,
            "POST",
            f"/api/runs/{run.run_id}/approve",
            {"decision_ref": "telegram-generated-historical-approver", "channel": "telegram"},
        )
        assert status == 200, approved
        publication = approved["result"]["publication"]
        assert publication["status"] == "PREPARED"
        assert publication["media"] == []

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
        assert published["response"]["media_count"] == 0
        assert published["response"]["text"].strip() == generated_text

        final = service.content_runs.get(run.run_id)
        assert final is not None
        assert final.status == "PUBLISHED"
        print("\nGENERATED_TELEGRAM_TEXT:\n" + generated_text)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
        service.close()
