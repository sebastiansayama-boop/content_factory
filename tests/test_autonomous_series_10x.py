from __future__ import annotations

import json
import os

import pytest

from content_factory.knowledge_content import KnowledgeContentBuilder
from content_factory.ollama_adapter import OllamaAdapter
from content_factory.service import FactoryService
from content_factory.text_capability import text_generation_capability
from content_factory.workspace import ContentWorkspace


pytestmark = pytest.mark.skipif(
    not os.environ.get("OLLAMA_MODEL"),
    reason="real Ollama provider configuration is required for this E2E",
)


def _knowledge():
    claims = [
        ("kc-time-1", "Люди издавна использовали повторяющиеся природные циклы для ориентации во времени.", "ke-time-1"),
        ("kc-time-2", "Солнечные часы связывают положение тени с ходом Солнца.", "ke-time-2"),
        ("kc-time-3", "Водяные часы позволяли измерять интервалы времени независимо от солнечного света.", "ke-time-3"),
        ("kc-time-4", "Механические часы сделали регулярный отсчёт интервалов частью городского ритма.", "ke-time-4"),
        ("kc-time-5", "Маятниковые часы Гюйгенса повысили точность механического измерения времени.", "ke-time-5"),
        ("kc-time-6", "Морские хронометры Харрисона помогли использовать точное время для определения долготы.", "ke-time-6"),
        ("kc-time-7", "Распространение железных дорог ускорило стандартизацию времени и появление часовых поясов.", "ke-time-7"),
        ("kc-time-8", "В 1967 году секунда была определена через частоту излучения атома цезия-133.", "ke-time-8"),
        ("kc-time-9", "Современные системы навигации и связи зависят от точной синхронизации времени.", "ke-time-9"),
        ("kc-time-10", "История измерения времени показывает переход от наблюдения природных циклов к измерению стабильных физических процессов.", "ke-time-10"),
    ]
    return {
        "topic": "Как человек научился измерять время",
        "summary": "История способов измерения времени от природных циклов до атомных часов.",
        "claims": [
            {"claim_id": cid, "text": text, "confidence": "high", "source_ids": ["src-time"], "evidence_ids": [eid], "scope": "История измерения времени."}
            for cid, text, eid in claims
        ],
        "evidence": [
            {"evidence_id": eid, "source_id": "src-time", "excerpt": text, "provenance": "controlled E2E knowledge"}
            for _, text, eid in claims
        ],
        "sources": [{"source_id": "src-time", "title": "Controlled E2E knowledge", "url": "https://example.invalid/time"}],
        "editorial_angles": ["Как менялся способ измерять время и зачем обществу требовалась всё большая точность."],
    }


@pytest.mark.external\ndef test_autonomous_series_accumulates_previous_results(tmp_path, monkeypatch):
    monkeypatch.setenv("FACTORY_DATA_DIR", str(tmp_path / "service-data"))
    service = FactoryService()
    try:
        ollama = OllamaAdapter()
        service._capability = text_generation_capability(
            capability_id="ollama.text.generate",
            provider=ollama,
            generate=ollama.generate,
            response_text=ollama.response_text,
        )
        workspace = ContentWorkspace(service)
        context = _knowledge()
        previous = None
        episodes = []

        for episode in range(1, 11):
            run = service.content_runs.create(
                title=f"Как человек научился измерять время — эпизод {episode}",
                brief="Как человек научился измерять время",
                audience="широкая аудитория Telegram",
                goal="создать последовательный исторический эпизод, который продолжает серию",
                formats=("telegram",),
                constraints=(
                    "style: Естественный",
                    "length: Средне",
                    "tone_strength: Средний",
                    "variation: Авто",
                    f"series_episode: {episode}",
                    "series_instruction: Каждый следующий эпизод должен учитывать предыдущий и развивать линию, не повторяя его.",
                ),
            )
            generated = KnowledgeContentBuilder(workspace, service.knowledge).build(
                run_id=run.run_id,
                topic="Как человек научился измерять время",
                audience="широкая аудитория Telegram",
                goal="последовательно рассказать историю измерения времени",
                formats=["telegram"],
                constraints=list(run.constraints),
                knowledge_context=context,
                previous_result=previous,
            )
            script = generated["script"]
            text = "\n\n".join(
                str(unit.get("text") or "").strip()
                for unit in script["units"]
                if isinstance(unit, dict) and str(unit.get("text") or "").strip()
            ).strip()
            assert text
            assert len(script["units"]) >= 4
            assert "—" not in text
            episodes.append({"episode": episode, "title": script["title"], "text": text})
            previous = generated

        assert len(episodes) == 10
        assert len({item["text"] for item in episodes}) == 10
        print("\nAUTONOMOUS SERIES RESULT")
        for item in episodes:
            print(f"\nEPISODE {item['episode']}: {item['title']}\n{item['text']}")
    finally:
        service.close()
