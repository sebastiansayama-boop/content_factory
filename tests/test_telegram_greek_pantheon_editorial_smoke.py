from __future__ import annotations

import json
import os
import threading

import pytest
from http.server import ThreadingHTTPServer

from content_factory.free_research import FreeWebGeminiAdapter
from content_factory.research import parse_research_json
from content_factory.knowledge import KnowledgeStore
from content_factory.knowledge_content import KnowledgeContentBuilder
from content_factory.ollama_adapter import OllamaAdapter
from content_factory.providers import LLMProvider
from content_factory.text_capability import text_generation_capability
from content_factory.product_http import ProductHandler
from content_factory.content_run_planner import ContentRunPlanner
from content_factory.service import FactoryService
from content_factory.workspace import ContentWorkspace
from tests.test_telegram_publication_smoke import _create_prepared_run, _request

pytestmark = pytest.mark.external


def _knowledge_from_research(payload: dict) -> dict:
    claims = []
    for raw in payload.get("claims", []):
        claim_id = str(raw.get("id") or "").strip()
        if not claim_id:
            continue
        evidence_ids = [
            f"ke-greek-{str(item).removeprefix('evidence-')}"
            for item in raw.get("evidence_ids", [])
            if isinstance(item, str)
        ]
        claims.append({
            "claim_id": f"kc-greek-{claim_id.removeprefix('claim-')}",
            "text": str(raw.get("text") or "").strip(),
            "evidence_ids": evidence_ids,
            "source_ids": [str(item) for item in raw.get("source_ids", []) if isinstance(item, str)],
            "scope": str(raw.get("scope") or "").strip(),
        })

    evidence = []
    for raw in payload.get("evidence", []):
        evidence_id = str(raw.get("id") or "").strip()
        source_id = str(raw.get("source_id") or "").strip()
        if not evidence_id or not source_id:
            continue
        evidence.append({
            "evidence_id": f"ke-greek-{evidence_id.removeprefix('evidence-')}",
            "source_id": source_id,
            "excerpt": str(raw.get("excerpt") or "").strip(),
        })

    sources = [
        {
            "source_id": str(raw.get("id") or "").strip(),
            "title": str(raw.get("title") or "").strip(),
            "url": str(raw.get("url") or "").strip(),
        }
        for raw in payload.get("sources", [])
        if isinstance(raw, dict) and raw.get("id") and raw.get("url")
    ]
    return {"claims": claims, "evidence": evidence, "sources": sources}


def test_real_telegram_greek_pantheon_editorial_smoke(tmp_path, monkeypatch):
    if os.environ.get("RUN_TELEGRAM_E2E") != "1":
        pytest.skip("set RUN_TELEGRAM_E2E=1 for a real Telegram publication smoke")
    for name in ("TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID", "GEMINI_API_KEY"):
        if not os.environ.get(name):
            pytest.fail(f"{name} is required")

    monkeypatch.setenv("FACTORY_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FACTORY_API_TOKEN", "telegram-greek-editorial-smoke-token")
    monkeypatch.delenv("FACTORY_TELEGRAM_FAKE", raising=False)

    research = FreeWebGeminiAdapter()
    prompt = """Research episode 1 of a Russian Telegram series titled "Пантеон богов в Древней Греции".
Return ONLY JSON with topic, summary, claims, sources and evidence.
Claims must be atomic, source-backed and scoped. Focus only on the basic map of the Greek pantheon:
Zeus, Hera, Poseidon, Hades, and the distinction between the Olympian gods and Hades.
Use reputable public sources and do not invent facts.
The material must support a 900-1800 character Russian publication.
USER BRIEF:
Ancient Greek pantheon: Zeus, Hera, Poseidon, Hades, and the basic structure of the Greek gods.
"""
    response = research.research(prompt)
    assert 200 <= response.status_code < 300
    payload = parse_research_json(research.text(response))
    context = _knowledge_from_research(payload)
    assert len(context["claims"]) >= 3
    assert context["evidence"]
    assert context["sources"]

    service = FactoryService()
    ollama = OllamaAdapter()
    assert isinstance(ollama, LLMProvider)
    service._capability = text_generation_capability(
        capability_id="ollama.text.generate",
        provider=ollama,
        generate=ollama.generate,
        response_text=ollama.response_text,
    )
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
        generated = KnowledgeContentBuilder(
            ProductHandler.workspace,
            service.knowledge,
        ).build(
            run_id=run.run_id,
            topic="Пантеон богов в Древней Греции",
            audience="широкая аудитория Telegram",
            goal="дать читателю карту пантеона, а не перечень имён",
            formats=["telegram"],
            constraints=[
                "style: Естественный",
                "length: Средне",
                "tone_strength: Средний",
                "variation: Авто",
            ],
            knowledge_context=context,
        )
        script = generated["script"]
        publication_text = "\n\n".join(
            str(unit["text"]).strip()
            for unit in script["units"]
            if isinstance(unit, dict) and str(unit.get("text") or "").strip()
        ).strip()
        assert 900 <= len(publication_text) <= 1800
        assert "—" not in publication_text
        assert script["variation_mode"] != "auto"
        assert len(script["units"]) >= 4

        result = dict(run.result or {})
        result["brief"] = "Пантеон богов в Древней Греции"
        result["content_brief"] = {
            **result["content_brief"],
            "title": script["title"],
        }
        result["package"] = {
            **result["package"],
            "title": script["title"],
            "text": publication_text,
            "media": [],
            "series": {
                "series_id": "telegram-series-greek-pantheon-004",
                "title": "Пантеон богов в Древней Греции",
                "episode": 1,
                "central_question": "Как устроен мир древнегреческих богов и почему каждый из них занял именно своё место?",
                "next_required_transition": "От общей карты перейти к Зевсу как центру олимпийского порядка.",
                "story_state": {
                    "central_question": "Как устроен мир древнегреческих богов и почему каждый из них занял именно своё место?",
                    "established": ["Эпизод 1 вводит карту основных фигур пантеона."],
                    "unresolved": ["Как Зевс стал центром олимпийского порядка?"],
                    "next_required_transition": "От общей карты перейти к Зевсу как центру олимпийского порядка.",
                    "used_examples": [],
                    "claims": [item["claim_id"] for item in context["claims"]],
                    "evidence": [item["evidence_id"] for item in context["evidence"]],
                },
            },
            "qc": {"status": "PASSED"},
        }
        service.content_runs.save_result(run.run_id, result)

        status, approved = _request(
            base_url,
            "POST",
            f"/api/runs/{run.run_id}/approve",
            {"decision_ref": "greek-pantheon-episode-1-approver", "channel": "telegram"},
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
        assert published["response"]["text"].strip() == publication_text

        print("\nGREEK_PANTHEON_EPISODE_1:\n" + publication_text)
        print("\nVARIATION_MODE:", script["variation_mode"])
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
        service.close()
