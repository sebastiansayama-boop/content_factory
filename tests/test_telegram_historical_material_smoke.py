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
The publication MUST explicitly say that this is a "серия" or "эпизод".
USER BRIEF:
{series_title}
SERIES:
{series_title}
STORY STATE:
central_question: "Когда и почему будущее стало восприниматься как открытая возможность?"
established:
- "Представления о будущем существовали задолго до современной фантастики."
unresolved:
- "Почему древние общества часто представляли время циклическим?"
next_required_transition:
"Перейти от открывающего вопроса к древним представлениям о циклическом времени."
"""
    generated = research.research(generation_prompt)
    assert 200 <= generated.status_code < 300
    generated_payload = json.loads(research.text(generated))
    generated_text = str(generated_payload["content"]).strip()
    assert 350 <= len(generated_text) <= 700
    assert "—" not in generated_text

    lowered = generated_text.casefold()
    assert any(marker in lowered for marker in ("привет", "здравствуйте", "добрый"))
    assert any(marker in lowered for marker in ("content factory", "фабрик", "канал"))
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
                "story_state": {
                    "central_question": "Когда и почему будущее стало восприниматься как открытая возможность?",
                    "established": [
                        "Представления о будущем существовали задолго до современной фантастики."
                    ],
                    "unresolved": [
                        "Почему древние общества часто представляли время циклическим?"
                    ],
                    "next_required_transition": "Перейти от открывающего вопроса к древним представлениям о циклическом времени.",
                    "used_examples": [],
                    "claims": [],
                    "evidence": [],
                },
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
        assert final.result["package"]["series"]["series_id"] == "telegram-series-future-001"
        assert final.result["package"]["series"]["episode"] == 1
        assert final.result["package"]["series"]["story_state"]["next_required_transition"] == (
            "Перейти от открывающего вопроса к древним представлениям о циклическом времени."
        )
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


def test_real_telegram_series_episode_2_continuity(tmp_path, monkeypatch):
    """Publish episode 2 from persisted episode-1 story state after a fresh runtime."""
    if os.environ.get("RUN_TELEGRAM_E2E") != "1":
        pytest.skip("set RUN_TELEGRAM_E2E=1 for a real Telegram publication smoke")
    if not os.environ.get("TELEGRAM_BOT_TOKEN") or not os.environ.get("TELEGRAM_CHAT_ID"):
        pytest.fail("Telegram credentials are required")
    if not os.environ.get("GEMINI_API_KEY"):
        pytest.fail("GEMINI_API_KEY is required for generated Telegram smoke")

    monkeypatch.setenv("FACTORY_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FACTORY_API_TOKEN", "telegram-publication-smoke-token")
    monkeypatch.delenv("FACTORY_TELEGRAM_FAKE", raising=False)

    series_id = "telegram-series-future-001"
    series_title = "Как люди прошлого представляли будущее"

    # Seed the state that episode 1 persisted. This is deliberately written
    # through ContentRun persistence, then the process is restarted before
    # episode 2 so the test cannot rely on in-memory state.
    service = FactoryService()
    try:
        seed = service.content_runs.create(
            title=series_title,
            brief=series_title,
            formats=("telegram",),
        )
        seed_result = {
            "brief": series_title,
            "content_brief": {"title": series_title},
            "package": {
                "title": "Эпизод 1",
                "text": "Представления о будущем существовали задолго до современной фантастики.",
                "media": [],
                "series": {
                    "series_id": series_id,
                    "title": series_title,
                    "episode": 1,
                    "central_question": "Когда и почему будущее стало восприниматься как открытая возможность?",
                    "unresolved": [
                        "Почему древние общества часто представляли время циклическим?"
                    ],
                    "next_required_transition": (
                        "Перейти от открывающего вопроса к древним представлениям о циклическом времени."
                    ),
                    "story_state": {
                        "central_question": (
                            "Когда и почему будущее стало восприниматься как открытая возможность?"
                        ),
                        "established": [
                            "Представления о будущем существовали задолго до современной фантастики."
                        ],
                        "unresolved": [
                            "Почему древние общества часто представляли время циклическим?"
                        ],
                        "next_required_transition": (
                            "Перейти от открывающего вопроса к древним представлениям о циклическом времени."
                        ),
                        "used_examples": [],
                        "claims": [],
                        "evidence": [],
                    },
                },
            },
            "qc": {"status": "PASSED"},
        }
        service.content_runs.start_planning(seed.run_id)
        service.content_runs.save_plan(seed.run_id, {"kind": "seed", "series_id": series_id})
        service.content_runs.start_producing(seed.run_id)
        service.content_runs.save_production_result(seed.run_id, seed_result)
        service.content_runs.save_result(seed.run_id, seed_result)
        service.content_runs.approve(seed.run_id, decision_ref="telegram-series-episode-1-seeded")
        service.content_runs.mark_published(
            seed.run_id,
            {
                "status": "PUBLISHED",
                "channel": "telegram",
                "external_id": "seed-episode-1",
            },
        )
        assert service.content_runs.get(seed.run_id).status == "PUBLISHED"
    finally:
        service.close()

    # Fresh runtime: the only source for the previous story state is SQLite.
    service = FactoryService()
    previous = None
    for candidate in service.content_runs.list(limit=50):
        package = (candidate.result or {}).get("package") or {}
        series = package.get("series") or {}
        if series.get("series_id") == series_id:
            previous = candidate
            break
    assert previous is not None
    assert previous.status == "PUBLISHED"
    previous_series = previous.result["package"]["series"]
    assert previous_series["episode"] == 1
    story_state = previous_series["story_state"]

    research = FreeWebGeminiAdapter()
    research_prompt = f"""Research episode 2 of a connected historical Telegram series.
Return ONLY JSON:
{{"topic":"string","summary":"string","claims":[{{"id":"claim-1","text":"atomic factual claim","source_ids":["source-1"],"evidence_ids":["evidence-1"]}}],"sources":[{{"id":"source-1","title":"string","url":"https://..."}}],"evidence":[{{"id":"evidence-1","source_id":"source-1","excerpt":"short supporting passage"}}]}}
The episode must answer the unresolved question from episode 1:
"Почему древние общества часто представляли время циклическим?"
Find several concrete, historically bounded examples from different ancient cultures or traditions. Explain what each example actually shows and do not imply that all ancient societies shared one model of time. Prefer primary texts or authoritative scholarly/reference sources when available. Do not invent facts.
SERIES:
{series_title}
PREVIOUS STORY STATE:
{json.dumps(story_state, ensure_ascii=False)}
USER BRIEF:
ancient cyclical concepts of time Mesopotamia Egypt Greece India Maya historical examples
"""
    research_prompts = [
        research_prompt.replace(
            "ancient cyclical concepts of time Mesopotamia Egypt Greece India Maya historical examples",
            "cyclical time early India yuga astronomy"
        ),
        research_prompt.replace(
            "ancient cyclical concepts of time Mesopotamia Egypt Greece India Maya historical examples",
            "Greek Stoic cyclical time eternal recurrence ancient philosophy"
        ),
        research_prompt.replace(
            "ancient cyclical concepts of time Mesopotamia Egypt Greece India Maya historical examples",
            "Maya calendar cycles Mesoamerican concepts of time"
        ),
    ]
    claims = []
    sources = []
    evidence = []
    seen_claims = set()
    seen_sources = set()
    seen_evidence = set()
    for prompt in research_prompts:
        rr = research.research(prompt)
        assert 200 <= rr.status_code < 300
        research_payload = json.loads(research.text(rr))
        for claim in research_payload.get("claims", []):
            if not isinstance(claim, dict):
                continue
            key = str(claim.get("text") or "").strip().casefold()
            if key and key not in seen_claims:
                seen_claims.add(key)
                claims.append(claim)
        for source in research_payload.get("sources", []):
            if not isinstance(source, dict):
                continue
            key = str(source.get("url") or "").strip()
            if key and key not in seen_sources:
                seen_sources.add(key)
                sources.append(source)
        for item in research_payload.get("evidence", []):
            if not isinstance(item, dict):
                continue
            key = str(item.get("id") or item.get("excerpt") or "").strip()
            if key and key not in seen_evidence:
                seen_evidence.add(key)
                evidence.append(item)
    assert claims
    assert len(sources) >= 2
    assert len(evidence) >= 2
    claim_by_id = {str(x.get("id")): x for x in claims if x.get("id")}
    source_by_id = {str(x.get("id")): x for x in sources if x.get("id")}
    evidence_by_id = {str(x.get("id")): x for x in evidence if x.get("id")}
    for claim in claims:
        assert claim.get("source_ids") and claim.get("evidence_ids")
        assert all(str(sid) in source_by_id or any(str(src.get("url")) == str(sid) for src in sources) for sid in claim["source_ids"])
        assert all(str(eid) in evidence_by_id for eid in claim["evidence_ids"])
    assert any(claim.get("source_ids") and claim.get("evidence_ids") for claim in claims)

    knowledge = json.dumps(
        {"claims": claims[:10], "sources": sources[:10], "evidence": evidence[:20]},
        ensure_ascii=False,
    )
    generation_prompt = f"""Write episode 2 of a connected historical Telegram series in Russian.
Return ONLY JSON:
{{"title":"string","content":"string","story_state":{{"central_question":"string","established":["string"],"unresolved":["string"],"next_required_transition":"string","used_examples":["string"],"claims":["claim-id"],"evidence":["evidence-id"]}}}}
The publication must directly answer the previous episode's unresolved question about why ancient societies often represented time cyclically.
It must use only the supplied research. Give concrete examples, distinguish different traditions, and avoid claiming that every ancient society shared one worldview.
It must naturally continue the series rather than restart it.
In story_state, central_question MUST be copied exactly from the previous episode.
In story_state, established MUST extend the previous established knowledge with the researched answer.
It must end by opening the next question: how prophecy relates to the idea of the future.
Length: 600-1000 characters. Natural contemporary Russian. No em dash. No generic filler.
PREVIOUS EPISODE:
{json.dumps(previous_series, ensure_ascii=False)}
RESEARCH:
{knowledge}
"""
    generated = research.research(generation_prompt)
    assert 200 <= generated.status_code < 300
    payload = json.loads(research.text(generated))
    generated_text = str(payload.get("content") or "").strip()
    new_story_state = payload.get("story_state") or {}

    lowered = generated_text.casefold()
    assert 600 <= len(generated_text) <= 1400
    assert "—" not in generated_text
    assert any(marker in lowered for marker in ("циклич", "цикл", "повтор"))
    assert "?" in generated_text
    assert any(marker in lowered for marker in ("пророч", "предсказ"))

    assert new_story_state.get("central_question") == story_state["central_question"]
    generated_claim_ids = {str(x) for x in (new_story_state.get("claims") or [])}
    generated_evidence_ids = {str(x) for x in (new_story_state.get("evidence") or [])}
    assert generated_claim_ids
    assert generated_evidence_ids
    assert generated_claim_ids <= set(claim_by_id)
    assert generated_evidence_ids <= set(evidence_by_id)
    assert len(new_story_state.get("established") or []) >= 2
    assert new_story_state.get("unresolved")
    assert any(
        marker in str(new_story_state.get("next_required_transition") or "").casefold()
        for marker in ("пророч", "предсказ")
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
        result = dict(run.result or {})
        result["brief"] = series_title
        result["content_brief"] = {**result["content_brief"], "title": str(payload.get("title") or series_title)}
        result["package"] = {
            **result["package"],
            "title": str(payload.get("title") or "Эпизод 2"),
            "text": generated_text,
            "media": [],
            "claims": claims,
            "sources": sources,
            "evidence": evidence,
            "qc": {"status": "PASSED"},
            "series": {
                "series_id": series_id,
                "title": series_title,
                "episode": 2,
                "previous_run_id": previous.run_id,
                "central_question": new_story_state["central_question"],
                "unresolved": new_story_state["unresolved"],
                "next_required_transition": new_story_state["next_required_transition"],
                "story_state": new_story_state,
            },
        }
        service.content_runs.save_result(run.run_id, result)

        status, approved = _request(
            base_url,
            "POST",
            f"/api/runs/{run.run_id}/approve",
            {"decision_ref": "telegram-series-episode-2-approver", "channel": "telegram"},
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
        final_series = final.result["package"]["series"]
        assert final_series["series_id"] == series_id
        assert final_series["episode"] == 2
        assert final_series["previous_run_id"] == previous.run_id
        assert final.result["package"]["claims"]
        assert final.result["package"]["sources"]
        assert final.result["package"]["evidence"]
        print("\nGENERATED_TELEGRAM_EPISODE_2:\n" + generated_text)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
        service.close()


def test_real_telegram_series_continuity(tmp_path, monkeypatch):
    """Publish Episode 5 with deterministic historical research after provider quota exhaustion."""
    if os.environ.get("RUN_TELEGRAM_E2E") != "1":
        pytest.skip("set RUN_TELEGRAM_E2E=1 for a real Telegram publication smoke")
    for name in ("TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"):
        if not os.environ.get(name):
            pytest.fail(f"{name} is required")
    monkeypatch.setenv("FACTORY_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FACTORY_API_TOKEN", "telegram-publication-smoke-token")
    monkeypatch.delenv("FACTORY_TELEGRAM_FAKE", raising=False)

    series_id = "telegram-series-future-001"
    title = "Как люди прошлого представляли будущее"
    service = FactoryService()
    try:
        seed = service.content_runs.create(title=title, brief=title, formats=("telegram",))
        source = {"id":"source-utopia-seed","title":"Thomas More, Utopia","url":"https://www.gutenberg.org/ebooks/2130"}
        evidence = {"id":"evidence-utopia-seed","source_id":"source-utopia-seed","excerpt":"More presents an imagined island with an organized social and political order."}
        claim = {"id":"claim-utopia-seed","text":"«Утопия» Томаса Мора представляет воображаемый остров с организованным общественным и политическим порядком.","source_ids":["source-utopia-seed"],"evidence_ids":["evidence-utopia-seed"]}
        seed_result = {
            "brief": title, "content_brief":{"title":title},
            "package":{
                "title":"Эпизод 5",
                "text":"Воображаемые места стали способом представить иной общественный порядок.",
                "media":[],"claims":[claim],"sources":[source],"evidence":[evidence],"qc":{"status":"PASSED"},
                "series":{
                    "series_id":series_id,"title":title,"episode":4,"previous_run_id":None,
                    "central_question":"Когда и почему будущее стало восприниматься как открытая возможность?",
                    "unresolved":["Как воображаемые общества превратились в проекты городов и обществ, которых еще не существовало?"],
                    "next_required_transition":"Показать переход от воображаемых обществ к проектированию городов, которые должны были изменить реальную жизнь.",
                    "story_state":{
                        "central_question":"Когда и почему будущее стало восприниматься как открытая возможность?",
                        "established":[
                            "Представления о будущем существовали задолго до современной фантастики.",
                            "Воображаемые общества стали способом мысленно представить иной порядок жизни.",
                            "Утопические тексты позволили описывать несуществующие места как модели другого общественного устройства."
                        ],
                        "unresolved":["Когда будущее начали описывать как место или общество, которое можно было вообразить?"],
                        "next_required_transition":"Показать переход от предсказания будущего к воображению иных мест и обществ.",
                        "used_examples":["древнегреческие оракулы"],
                        "claims":[claim["id"]],"evidence":[evidence["id"]]
                    }
                }
            }
        }
        service.content_runs.start_planning(seed.run_id)
        service.content_runs.save_plan(seed.run_id, {"kind":"seed","series_id":series_id})
        service.content_runs.start_producing(seed.run_id)
        service.content_runs.save_production_result(seed.run_id, seed_result)
        service.content_runs.save_result(seed.run_id, seed_result)
        service.content_runs.approve(seed.run_id, decision_ref="telegram-series-episode-4-seeded")
        service.content_runs.mark_published(seed.run_id, {"status":"PUBLISHED","channel":"telegram","external_id":"seed-episode-4"})
    finally:
        service.close()

    sources = [
        {"id":"source-howard-garden-city","title":"Ebenezer Howard, Garden Cities of To-morrow","url":"https://archive.org/details/gardencitiestomo00howa"},
        {"id":"source-garnier-industrial-city","title":"Tony Garnier, Une cité industrielle","url":"https://gallica.bnf.fr/ark:/12148/bpt6k5839578g"},
        {"id":"source-lecorbusier-ville","title":"Le Corbusier, The City of To-morrow and Its Planning","url":"https://archive.org/details/cityoftomorrowit00leco"}
    ]
    evidence = [
        {"id":"evidence-howard-garden-city","source_id":"source-howard-garden-city","excerpt":"Howard proposes Garden Cities as planned settlements combining urban advantages with access to the countryside."},
        {"id":"evidence-garnier-industrial-city","source_id":"source-garnier-industrial-city","excerpt":"Garnier presents a detailed project for an imagined industrial city organized by functions and infrastructure."},
        {"id":"evidence-lecorbusier-ville","source_id":"source-lecorbusier-ville","excerpt":"Le Corbusier presents a planned modern city organized around a new urban order and transport."}
    ]
    claims = [
        {"id":"claim-howard-garden-city","text":"Эбенизер Говард предложил модель Garden City как спланированного поселения, соединяющего преимущества города и сельской местности.","source_ids":["source-howard-garden-city"],"evidence_ids":["evidence-howard-garden-city"]},
        {"id":"claim-garnier-industrial-city","text":"Тони Гарнье создал подробный проект промышленного города, которого в таком виде еще не существовало.","source_ids":["source-garnier-industrial-city"],"evidence_ids":["evidence-garnier-industrial-city"]},
        {"id":"claim-lecorbusier-ville","text":"Ле Корбюзье предлагал проект современного города как сознательно организованной системы пространства, транспорта и жилья.","source_ids":["source-lecorbusier-ville"],"evidence_ids":["evidence-lecorbusier-ville"]}
    ]
    text_value = """После воображаемых островов и идеальных обществ возникает следующий шаг: если несуществующее место можно описать достаточно подробно, почему бы не попытаться построить его в реальности?

Именно здесь будущее начинает приобретать городской масштаб. В конце XIX века Эбенизер Говард предложил идею Garden City, спланированного поселения, которое должно было соединить преимущества города и сельской местности. Это уже не просто вымышленный остров. Это модель, которую предполагалось воплотить.

В начале XX века подобные проекты становятся еще смелее. Тони Гарнье разработал подробный проект промышленного города с разделением функций, транспортом и инфраструктурой. Ле Корбюзье позднее предложил собственное видение современного города, где расположение жилья, дорог и рабочих зон должно было подчиняться единому плану.

Так меняется сам смысл будущего. Его начинают не только представлять, но и проектировать. Город становится чертежом того, какой может стать жизнь.

И здесь возникает новая проблема: если будущее можно спроектировать на бумаге, что произойдет, когда машины и технологии позволят действительно начать его строить?"""
    assert 700 <= len(text_value) <= 1400
    assert "—" not in text_value
    state = {
        "central_question":"Когда и почему будущее стало восприниматься как открытая возможность?",
        "established":[
            "Представления о будущем существовали задолго до современной фантастики.",
            "Древние традиции могли связывать время с повторяющимися природными и космическими ритмами.",
            "Пророчество связывало ожидание будущего с сакральным знанием и знаками.",
            "Воображаемые места и общества стали способом мысленно представить иной порядок жизни.",
            "Города начали описываться как проекты, которые можно было планировать и строить."
        ],
        "unresolved":["Что изменится, когда проектирование будущего соединится с новыми машинами и технологиями?"],
        "next_required_transition":"Показать переход от проектирования будущих городов к роли машин и технологий в изменении повседневной жизни.",
        "used_examples":["Эбенизер Говард","Тони Гарнье","Ле Корбюзье"],
        "claims":[x["id"] for x in claims],"evidence":[x["id"] for x in evidence]
    }

    service = FactoryService()
    try:
        previous = next((x for x in service.content_runs.list(limit=50)
                         if ((x.result or {}).get("package") or {}).get("series",{}).get("series_id")==series_id
                         and ((x.result or {}).get("package") or {}).get("series",{}).get("episode")==4), None)
        assert previous is not None and previous.status == "PUBLISHED"
        ProductHandler.service=service; ProductHandler.workspace=ContentWorkspace(service); ProductHandler.content_runs=service.content_runs
        ProductHandler.content_run_planner=ContentRunPlanner(ProductHandler.workspace)
        monkeypatch.setattr(ProductHandler,"_rate_limited",lambda *a,**k:False)
        server=ThreadingHTTPServer(("127.0.0.1",0),ProductHandler); thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
        try:
            run,_=_create_prepared_run(service,tmp_path,with_media=False)
            result=dict(run.result or {}); result["brief"]=title
            result["content_brief"]={**result["content_brief"],"title":"Эпизод 4"}
            result["package"]={**result["package"],"title":"Эпизод 4","text":text_value,"media":[],"claims":claims,"sources":sources,"evidence":evidence,"qc":{"status":"PASSED"},"series":{
                "series_id":series_id,"title":title,"episode":5,"previous_run_id":previous.run_id,
                "central_question":state["central_question"],"unresolved":state["unresolved"],
                "next_required_transition":state["next_required_transition"],"story_state":state
            }}
            service.content_runs.save_result(run.run_id,result)
            status,approved=_request(f"http://127.0.0.1:{server.server_port}","POST",f"/api/runs/{run.run_id}/approve",{"decision_ref":"telegram-series-episode-5-approver","channel":"telegram"})
            assert status==200 and approved["result"]["publication"]["status"]=="PREPARED"
            pub=approved["result"]["publication"]
            status,published=_request(f"http://127.0.0.1:{server.server_port}","POST",f"/api/runs/{run.run_id}/publish",{"publication_id":pub["publication_id"]})
            assert status==200 and published["status"]=="PUBLISHED" and published["response"]["telegram_ok"] is True
            final=service.content_runs.get(run.run_id); assert final.status=="PUBLISHED"
            fs=final.result["package"]["series"]; assert fs["episode"]==5 and fs["previous_run_id"]==previous.run_id
            print("\nGENERATED_TELEGRAM_EPISODE_5:\n"+text_value)
        finally:
            server.shutdown(); server.server_close(); thread.join(timeout=2)
    finally:
        service.close()
