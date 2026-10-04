from __future__ import annotations

import os
import threading
from http.server import ThreadingHTTPServer

import pytest

from content_factory.content_run_planner import ContentRunPlanner
from content_factory.product_http import ProductHandler
from content_factory.service import FactoryService
from content_factory.workspace import ContentWorkspace
from tests.test_telegram_publication_smoke import _create_prepared_run, _request


pytestmark = pytest.mark.external


SERIES_ID = "telegram-series-future-001"
SERIES_TITLE = "Как люди прошлого представляли будущее"

EPISODE_6_TEXT = """В предыдущем эпизоде будущее стало чертежом: его начали описывать как города и системы, которые можно было спроектировать заранее. Но на этом история меняется. Машины не просто помогли строить запланированный мир. Они начали менять саму скорость и масштаб перемен.

Паровая машина постепенно превратилась из отдельного технического устройства в основу промышленной системы. Усовершенствования Джеймса Уатта в XVIII веке сделали ее значительно практичнее для разных видов работы. Затем железные дороги связали города и расстояния уже не так, как их знали прежде. В 1825 году открылась железная дорога Стоктон — Дарлингтон, на которой использовалась паровая тяга.

Это важно не только как история изобретений. Раньше воображаемый город можно было представить на бумаге, но сама жизнь менялась сравнительно медленно. Машины сделали изменение среды частью повседневности: производство, транспорт и расстояния стали зависеть от технических систем.

Поэтому будущее постепенно перестает быть только проектом. Оно становится процессом, который уже идет и способен менять планы быстрее, чем человек успевает их составить.

И здесь возникает следующий вопрос: когда стало понятно, что будущее нельзя надежно спроектировать заранее?"""

CLAIMS = [
    {
        "id": "claim-watt-steam",
        "text": "Усовершенствования Джеймса Уатта в XVIII веке сделали паровую машину значительно практичнее для промышленного применения.",
        "source_ids": ["source-watt"],
        "evidence_ids": ["evidence-watt"],
    },
    {
        "id": "claim-stockton-darlington",
        "text": "В 1825 году открылась железная дорога Стоктон — Дарлингтон, на которой использовалась паровая тяга.",
        "source_ids": ["source-stockton-darlington"],
        "evidence_ids": ["evidence-stockton-darlington"],
    },
    {
        "id": "claim-machines-change",
        "text": "Развитие паровой техники и железных дорог связало производство и транспорт с новыми техническими системами и изменило масштаб повседневных перемещений.",
        "source_ids": ["source-stockton-darlington", "source-watt"],
        "evidence_ids": ["evidence-watt", "evidence-stockton-darlington"],
    },
]

SOURCES = [
    {
        "id": "source-watt",
        "title": "Science Museum, James Watt",
        "url": "https://www.scienceandindustrymuseum.org.uk/objects-and-stories/james-watt",
    },
    {
        "id": "source-stockton-darlington",
        "title": "Science Museum, Stockton and Darlington Railway",
        "url": "https://www.scienceandindustrymuseum.org.uk/objects-and-stories/stockton-and-darlington-railway",
    },
]

EVIDENCE = [
    {
        "id": "evidence-watt",
        "source_id": "source-watt",
        "excerpt": "The Science Museum documents James Watt's improvements to the steam engine and their importance to industrial development.",
    },
    {
        "id": "evidence-stockton-darlington",
        "source_id": "source-stockton-darlington",
        "excerpt": "The Science Museum documents the opening of the Stockton and Darlington Railway in 1825 and its use of steam locomotives.",
    },
]

STORY_STATE = {
    "central_question": "Когда и почему будущее стало восприниматься как открытая возможность?",
    "established": [
        "Представления о будущем существовали задолго до современной фантастики.",
        "Древние традиции могли связывать время с повторяющимися природными и космическими ритмами.",
        "Пророчество связывало ожидание будущего с сакральным знанием и знаками.",
        "Воображаемые места и общества стали способом мысленно представить иной порядок жизни.",
        "Города начали описываться как проекты, которые можно было планировать и строить.",
        "Машины и технические системы начали ускорять и масштабировать изменения в повседневной жизни.",
    ],
    "unresolved": [
        "Когда стало понятно, что будущее нельзя надежно спроектировать заранее?"
    ],
    "next_required_transition": (
        "Показать момент, когда ускорение технических и социальных изменений "
        "сделало будущее все менее предсказуемым."
    ),
    "used_examples": [
        "Эбенизер Говард",
        "Тони Гарнье",
        "Ле Корбюзье",
        "Джеймс Уатт",
        "железная дорога Стоктон — Дарлингтон",
    ],
    "claims": [claim["id"] for claim in CLAIMS],
    "evidence": [item["id"] for item in EVIDENCE],
}


def _seed_episode_5(service: FactoryService) -> object:
    seed = service.content_runs.create(
        title=SERIES_TITLE,
        brief=SERIES_TITLE,
        formats=("telegram",),
    )
    result = {
        "brief": SERIES_TITLE,
        "content_brief": {"title": SERIES_TITLE},
        "package": {
            "title": "Эпизод 5",
            "text": (
                "После воображаемых обществ возникла возможность проектировать "
                "города, которых еще не существовало."
            ),
            "media": [],
            "claims": [],
            "sources": [],
            "evidence": [],
            "qc": {"status": "PASSED"},
            "series": {
                "series_id": SERIES_ID,
                "title": SERIES_TITLE,
                "episode": 5,
                "previous_run_id": None,
                "central_question": STORY_STATE["central_question"],
                "unresolved": [
                    "Что изменится, когда проектирование будущего соединится с новыми машинами и технологиями?"
                ],
                "next_required_transition": (
                    "Показать переход от проектирования будущих городов "
                    "к роли машин и технологий в изменении повседневной жизни."
                ),
                "story_state": {
                    **{k: v for k, v in STORY_STATE.items() if k not in {"established", "unresolved", "next_required_transition", "used_examples", "claims", "evidence"}},
                    "established": STORY_STATE["established"][:5],
                    "unresolved": [
                        "Что изменится, когда проектирование будущего соединится с новыми машинами и технологиями?"
                    ],
                    "next_required_transition": (
                        "Показать переход от проектирования будущих городов "
                        "к роли машин и технологий в изменении повседневной жизни."
                    ),
                    "used_examples": STORY_STATE["used_examples"][:3],
                    "claims": [],
                    "evidence": [],
                },
            },
        },
    }
    service.content_runs.start_planning(seed.run_id)
    service.content_runs.save_plan(seed.run_id, {"kind": "seed", "series_id": SERIES_ID})
    service.content_runs.start_producing(seed.run_id)
    service.content_runs.save_production_result(seed.run_id, result)
    service.content_runs.save_result(seed.run_id, result)
    service.content_runs.approve(seed.run_id, decision_ref="telegram-series-episode-5-seeded")
    service.content_runs.mark_published(
        seed.run_id,
        {
            "status": "PUBLISHED",
            "channel": "telegram",
            "external_id": "seed-episode-5",
        },
    )
    return seed


def test_real_telegram_episode_6_publication(tmp_path, monkeypatch):
    if os.environ.get("RUN_TELEGRAM_E2E") != "1":
        pytest.skip("set RUN_TELEGRAM_E2E=1 for a real Telegram publication smoke")
    for name in ("TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"):
        if not os.environ.get(name):
            pytest.fail(f"{name} is required")

    monkeypatch.setenv("FACTORY_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FACTORY_API_TOKEN", "telegram-publication-smoke-token")
    monkeypatch.delenv("FACTORY_TELEGRAM_FAKE", raising=False)

    service = FactoryService()
    previous = _seed_episode_5(service)

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
        result["brief"] = SERIES_TITLE
        result["content_brief"] = {
            **result["content_brief"],
            "title": "Эпизод 6",
        }
        result["package"] = {
            **result["package"],
            "title": "Эпизод 6",
            "text": EPISODE_6_TEXT,
            "media": [],
            "claims": CLAIMS,
            "sources": SOURCES,
            "evidence": EVIDENCE,
            "qc": {"status": "PASSED"},
            "series": {
                "series_id": SERIES_ID,
                "title": SERIES_TITLE,
                "episode": 6,
                "previous_run_id": previous.run_id,
                "central_question": STORY_STATE["central_question"],
                "unresolved": STORY_STATE["unresolved"],
                "next_required_transition": STORY_STATE["next_required_transition"],
                "story_state": STORY_STATE,
            },
        }
        service.content_runs.save_result(run.run_id, result)

        status, approved = _request(
            base_url,
            "POST",
            f"/api/runs/{run.run_id}/approve",
            {"decision_ref": "telegram-series-episode-6-approver", "channel": "telegram"},
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
        assert published["response"]["text"].strip() == EPISODE_6_TEXT

        final = service.content_runs.get(run.run_id)
        assert final is not None
        assert final.status == "PUBLISHED"
        final_series = final.result["package"]["series"]
        assert final_series["series_id"] == SERIES_ID
        assert final_series["episode"] == 6
        assert final_series["previous_run_id"] == previous.run_id
        assert final.result["package"]["claims"] == CLAIMS
        assert final.result["package"]["sources"] == SOURCES
        assert final.result["package"]["evidence"] == EVIDENCE
        print("\nTELEGRAM_EPISODE_6:\n" + EPISODE_6_TEXT)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
        service.close()
