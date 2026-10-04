from __future__ import annotations

import json
import os
import threading
from http.server import ThreadingHTTPServer

import pytest

from content_factory.publication_diversity import max_publication_similarity
from tests.test_telegram_publication_smoke import _create_prepared_run, _request
from content_factory.content_run_planner import ContentRunPlanner
from content_factory.product_http import ProductHandler
from content_factory.service import FactoryService
from content_factory.workspace import ContentWorkspace
from content_factory.free_research import FreeWebGeminiAdapter

pytestmark = pytest.mark.external


def test_real_telegram_historical_material_smoke(tmp_path, monkeypatch):
    if os.environ.get("RUN_TELEGRAM_E2E") != "1":
        pytest.skip("set RUN_TELEGRAM_E2E=1 for a real Telegram publication smoke")
    if not os.environ.get("TELEGRAM_BOT_TOKEN") or not os.environ.get("TELEGRAM_CHAT_ID"):
        pytest.fail("Telegram credentials are required")

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
    monkeypatch.setenv("FACTORY_API_TOKEN", "telegram-publication-smoke-token")
    monkeypatch.delenv("FACTORY_TELEGRAM_FAKE", raising=False)

    research = FreeWebGeminiAdapter()
    series_title = "Как люди прошлого представляли будущее"
    generation_prompt = f"""Write the FIRST publication of a serialized Telegram channel in Russian.
Return ONLY JSON: {{"title":"string","content":"string"}}.
This is episode 1 of a 10-part series.
The first publication must:
- greet the reader;
- introduce the narrator/channel as Content Factory;
- briefly explain that this is the beginning of a connected historical series;
- introduce the central question: when and why did people begin to see the future as an open possibility rather than something predetermined;
- end with a clear unresolved question that naturally leads to episode 2;
- NOT answer the historical question yet.
Length: 350-700 characters.
Natural contemporary Russian. Concrete and concise. No generic filler. Do not use the em dash character.
Do not invent historical facts in this introductory episode.
USER BRIEF:
{series_title}
SERIES:
{series_title}
"""
    generated = research.research(generation_prompt)
    assert 200 <= generated.status_code < 300
    generated_payload = json.loads(research.text(generated))
    generated_text = str(generated_payload["content"]).strip()
    assert 350 <= len(generated_text) <= 700
    assert "—" not in generated_text

    lowered = generated_text.casefold()
    assert any(marker in lowered for marker in ("привет", "здравствуйте", "добрый"))
    assert "content factory" in lowered
    assert any(marker in lowered for marker in ("серия", "эпизод", "часть"))
    assert "будущ" in lowered
    assert any(marker in lowered for marker in ("открыт", "возможност", "предопредел"))
    assert "?" in generated_text

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
        result["brief"] = series_title
        result["content_brief"] = {
            **result["content_brief"],
            "title": series_title,
        }
        result["package"] = {
            **result["package"],
            "title": str(generated_payload.get("title") or series_title),
            "text": generated_text,
            "media": [],
            "series": {
                "series_id": "telegram-series-future-001",
                "title": series_title,
                "episode": 1,
                "central_question": "Когда и почему будущее стало восприниматься как открытая возможность?",
                "unresolved": ["Почему древние общества часто представляли время циклическим?"],
                "next_required_transition": "Перейти от открывающего вопроса к древним представлениям о циклическом времени.",
            },
            "qc": {"status": "PASSED"},
        }
        service.content_runs.save_result(run.run_id, result)

        status, approved = _request(
            base_url,
            "POST",
            f"/api/runs/{run.run_id}/approve",
            {"decision_ref": "telegram-series-episode-1-approver", "channel": "telegram"},
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
        assert final.result["series"]["series_id"] == "telegram-series-future-001"
        assert final.result["series"]["episode"] == 1
        print("\nGENERATED_TELEGRAM_TEXT:\n" + generated_text)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
        service.close()


@pytest.mark.external
def test_real_telegram_five_matrix_publications(tmp_path, monkeypatch):
    if os.environ.get("RUN_TELEGRAM_E2E") != "1":
        pytest.skip("set RUN_TELEGRAM_E2E=1 for a real Telegram matrix publication test")
    if not os.environ.get("TELEGRAM_BOT_TOKEN") or not os.environ.get("TELEGRAM_CHAT_ID"):
        pytest.fail("Telegram credentials are required")
    if not os.environ.get("GEMINI_API_KEY"):
        pytest.fail("GEMINI_API_KEY is required for matrix publication test")

    from content_factory.publication_text_matrix import TEXT_VARIATION_MATRIX, format_text_variation_matrix
    from content_factory.publication_text_rules import resolve_publication_text_rules, validate_publication_text

    monkeypatch.setenv("FACTORY_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FACTORY_API_TOKEN", "telegram-publication-smoke-token")
    monkeypatch.delenv("FACTORY_TELEGRAM_FAKE", raising=False)

    research = FreeWebGeminiAdapter()
    topic = "Как люди прошлого представляли будущее до появления современной научной фантастики"
    research_prompt = f"""Research the topic and return ONLY JSON:
{{"topic":"string","summary":"string","claims":[{{"id":"claim-1","text":"atomic factual claim","source_ids":["source-1"],"evidence_ids":["evidence-1"]}}],"sources":[{{"id":"source-1","title":"string","url":"https://..."}}],"evidence":[{{"id":"evidence-1","source_id":"source-1","excerpt":"short supporting passage"}}]}}
Use several distinct historical examples from different periods or regions. Keep every claim bounded and source-backed. Do not invent facts.
USER BRIEF:
{topic}
"""
    research_prompts = [
        research_prompt,
        f"""Research one concrete historical example for this topic and return ONLY JSON in the same schema.
Focus on a pre-modern or early-modern example with a specific person, text, object, place, or dated event. Keep claims atomic and source-backed. Do not invent facts.
USER BRIEF:
{topic}""",
        f"""Research one different concrete historical example for this topic and return ONLY JSON in the same schema.
Focus on a different period or region and provide a specific source-backed detail that can support a distinct editorial angle. Do not invent facts.
USER BRIEF:
{topic}""",
    ]
    claims = []
    evidence = []
    seen_claims = set()
    for prompt in research_prompts:
        rr = research.research(prompt)
        assert 200 <= rr.status_code < 300
        rp = json.loads(research.text(rr))
        for claim in rp.get("claims", []):
            key = str(claim.get("text") or "").strip().casefold()
            if key and key not in seen_claims:
                seen_claims.add(key)
                claims.append(claim)
        evidence.extend(rp.get("evidence", []))
    assert len(claims) >= 2
    assert evidence
    knowledge = json.dumps({"claims": claims[:8], "evidence": evidence[:16]}, ensure_ascii=False)

    rules = resolve_publication_text_rules(["language: Русский", "style: natural", "length: short", "tone_strength: medium", "variation: auto"])
    matrix = format_text_variation_matrix()
    generated = []
    used_modes = set()
    valid_modes = {item.id for item in TEXT_VARIATION_MATRIX}
    for index in range(5):
        prompt = f"""Write one finished Telegram publication in Russian.
Return ONLY JSON: {{"title":"string","content":"string","variation_mode":"scene|person|contrast|question|object|sequence|myth_fact|zoom_out"}}.
This is publication {index + 1} of 5 for the SAME topic and SAME accepted knowledge.
Variation is AUTO: choose exactly one dominant writing mode from the supplied matrix based on the strongest factual shape of the accepted knowledge.
The mode label is internal and must not appear in the publication.
Do not force a mode if the evidence does not support it. Prefer an unused supported mode. Previously used modes: {", ".join(sorted(used_modes)) or "none"}. Choose a mode not in that set unless no unused supported mode remains.
Length: 550-850 characters. One coherent publication, not a list.
Use only supplied claims/evidence. Preserve uncertainty and scope. No invented facts.
Natural contemporary Russian. No em dash. No generic openings or filler.
TEXT VARIATION MATRIX:
{matrix}
TOPIC:
{topic}
ACCEPTED KNOWLEDGE:
{knowledge}
"""
        gr = research.research(prompt)
        assert 200 <= gr.status_code < 300
        gp = json.loads(research.text(gr))
        text_value = str(gp["content"]).strip()
        variation_mode = str(gp.get("variation_mode") or "").strip().casefold()
        assert variation_mode in valid_modes
        used_modes.add(variation_mode)
        validate_publication_text(text_value, rules)
        assert "—" not in text_value
        generated.append((str(gp.get("title") or topic).strip(), text_value, variation_mode))
    assert len({text_value for _, text_value in generated}) == 5
    assert len(used_modes) >= 3

    # Surface the failure mode we saw in real Telegram output: different
    # variation labels are not sufficient if the factual/narrative core repeats.
    pair_scores = []
    for left_index in range(len(generated)):
        for right_index in range(left_index + 1, len(generated)):
            score = max_publication_similarity(
                generated[left_index][1],
                [generated[right_index][1]],
            )
            pair_scores.append((left_index + 1, right_index + 1, score))
    max_pair = max(pair_scores, key=lambda item: item[2])
    assert max_pair[2] < 0.35, (
        "publication diversity failed: "
        f"pair {max_pair[0]} vs {max_pair[1]} similarity={max_pair[2]:.3f}"
    )

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
        for index, (title, text_value, variation_mode) in enumerate(generated, start=1):
            run, _asset = _create_prepared_run(service, tmp_path, with_media=False)
            result = dict(run.result or {})
            result["brief"] = topic
            result["content_brief"] = {**result["content_brief"], "title": title}
            result["package"] = {**result["package"], "title": title, "text": text_value, "media": [], "claims": claims, "evidence": evidence, "qc": {"status": "PASSED"}}
            service.content_runs.save_result(run.run_id, result)
            status, approved = _request(base_url, "POST", f"/api/runs/{run.run_id}/approve", {"decision_ref": f"telegram-matrix-{index}-approver", "channel": "telegram"})
            assert status == 200, approved
            publication = approved["result"]["publication"]
            assert publication["status"] == "PREPARED"
            assert publication["media"] == []
            status, published = _request(base_url, "POST", f"/api/runs/{run.run_id}/publish", {"publication_id": publication["publication_id"]})
            assert status == 200, published
            assert published["status"] == "PUBLISHED"
            assert published["channel"] == "telegram"
            assert published["response"]["telegram_ok"] is True
            assert published["response"]["media_count"] == 0
            assert published["response"]["text"].strip() == text_value
            print(f"\nMATRIX_TELEGRAM_PUBLICATION_{index}: mode={variation_mode}\n{title}\n{text_value}")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
        service.close()
