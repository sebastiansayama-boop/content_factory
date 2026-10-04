import json

from content_factory.artifacts import ArtifactStore
from content_factory.knowledge import KnowledgeStore
from content_factory.knowledge_content import KnowledgeContentBuilder
from content_factory.runtime import Capability, ExecutionResult, VerificationResult
from content_factory.runtime_store import RuntimeStore
from content_factory.workspace import ContentWorkspace


class FakeFactory:
    def __init__(self, outputs, tmp_path):
        self._store = RuntimeStore(tmp_path / "runtime.sqlite3")
        self._artifacts = ArtifactStore(tmp_path / "artifacts")
        self._capability = Capability(
            capability_id="fake.text.generate",
            input_contract=lambda item: None,
            executor=self._executor(outputs),
        )

    @staticmethod
    def _verify(_, execution):
        return VerificationResult(
            output_revision_id=execution.output_revision_id,
            passed=True,
        )

    @staticmethod
    def _executor(outputs):
        state = {"index": 0}

        def execute(item, execution_id):
            output = outputs[state["index"]]
            state["index"] += 1
            return ExecutionResult(
                execution_id=execution_id,
                capability_id="fake.text.generate",
                output_revision_id=f"fake:{item.revision_id}",
                payload=output,
            )

        return execute


def _knowledge():
    return {
        "claims": [
            {
                "id": "claim-1",
                "text": "Ancient calendars organized civic and ritual time.",
                "confidence": "high",
                "source_ids": ["source-1"],
                "evidence_ids": ["evidence-1"],
            },
            {
                "id": "claim-2",
                "text": "Historical texts used cycles and signs to describe future events.",
                "confidence": "medium",
                "source_ids": ["source-2"],
                "evidence_ids": ["evidence-2"],
            },
        ],
        "sources": [
            {"id": "source-1", "title": "Calendar source", "url": "https://example.com/calendar"},
            {"id": "source-2", "title": "Future source", "url": "https://example.com/future"},
        ],
        "evidence": [
            {"id": "evidence-1", "source_id": "source-1", "excerpt": "Calendar evidence", "provenance": "test"},
            {"id": "evidence-2", "source_id": "source-2", "excerpt": "Future evidence", "provenance": "test"},
        ],
        "editorial_angles": [],
    }


def _script(text, claim_id, evidence_id):
    return json.dumps({
        "script_id": "script-1",
        "title": "Разный материал",
        "variation_mode": "contrast",
        "units": [
            {"unit_id": "unit-1", "kind": "hook", "text": text, "visual_intent": "", "claim_refs": [claim_id], "evidence_refs": [evidence_id]},
            {"unit_id": "unit-2", "kind": "context", "text": "Контекст уточняет исходное наблюдение.", "visual_intent": "", "claim_refs": [claim_id], "evidence_refs": [evidence_id]},
            {"unit_id": "unit-3", "kind": "development", "text": "Документированная деталь показывает другой аспект материала.", "visual_intent": "", "claim_refs": [claim_id], "evidence_refs": [evidence_id]},
            {"unit_id": "unit-4", "kind": "conclusion", "text": "Вывод остается ограниченным принятой evidence.", "visual_intent": "", "claim_refs": [claim_id], "evidence_refs": [evidence_id]},
        ],
    })


def test_builder_regenerates_when_publication_is_too_similar(tmp_path):
    store = KnowledgeStore(tmp_path / "knowledge.sqlite3")
    store.capture(run_id="research-diversity", research=_knowledge())
    rows = store._connection.execute("SELECT claim_id FROM knowledge_claims ORDER BY claim_id").fetchall()
    links = store._connection.execute("SELECT claim_id, evidence_id FROM knowledge_claim_evidence ORDER BY claim_id, evidence_id").fetchall()
    claim_1 = rows[0]["claim_id"]
    claim_2 = rows[1]["claim_id"]
    evidence_1 = next(row["evidence_id"] for row in links if row["claim_id"] == claim_1)
    evidence_2 = next(row["evidence_id"] for row in links if row["claim_id"] == claim_2)
    store.promote_claim(claim_1, decision_ref="D1")
    store.promote_claim(claim_2, decision_ref="D2")

    repeated = "Календарь организовывал гражданское и ритуальное время. Этот порядок задавал структуру праздников и повседневной жизни."
    distinct = "В старых текстах будущее могло описываться через циклы и знаки. Такой способ связывал ожидание события с уже известной системой отсчета."

    outputs = [
        json.dumps({"ideas": [
            {"idea_id": "idea-1", "title": "Calendar", "angle": "time", "audience": "general", "purpose": "explain", "formats": ["article"], "claim_refs": [claim_1], "evidence_refs": [evidence_1]},
            {"idea_id": "idea-2", "title": "Future", "angle": "cycles", "audience": "general", "purpose": "compare", "formats": ["article"], "claim_refs": [claim_2], "evidence_refs": [evidence_2]},
            {"idea_id": "idea-3", "title": "Both", "angle": "contrast", "audience": "general", "purpose": "compare", "formats": ["article"], "claim_refs": [claim_1, claim_2], "evidence_refs": [evidence_1, evidence_2]},
        ]}),
        json.dumps({"brief_id": "brief-1", "title": "Future", "objective": "compare", "audience": "general", "angle": "cycles", "selected_claim_refs": [claim_2], "evidence_refs": [evidence_2], "editorial_points": [{"point_id": "point-1", "text": "Cycles", "role": "development", "claim_refs": [claim_2], "evidence_refs": [evidence_2]}], "content_elements": [{"element_id": "element-1", "kind": "narration", "editorial_point_ids": ["point-1"], "purpose": "explain", "production_intent": "text", "claim_refs": [claim_2], "evidence_refs": [evidence_2]}], "formats": ["article"], "constraints": ["none"]}),
        json.dumps({"spec_id": "spec-1", "title": "Future", "objective": "compare", "audience": "general", "format": "article", "tone": "clear", "structure": ["hook", "context", "development", "conclusion"], "constraints": ["none"], "claim_refs": [claim_2], "evidence_refs": [evidence_2], "style_bible": {}}),
        _script(repeated, claim_2, evidence_2),
        _script(distinct, claim_2, evidence_2),
    ]

    factory = FakeFactory(outputs, tmp_path)
    previous = {
        "script": {
            "units": [
                {"unit_id": "old-1", "text": repeated, "claim_refs": [claim_1]},
                {"unit_id": "old-2", "text": "Предыдущий контекст.", "claim_refs": [claim_1]},
            ]
        }
    }
    result = KnowledgeContentBuilder(ContentWorkspace(factory), store).build(
        run_id="run-diversity",
        topic="future",
        audience="general",
        goal="compare",
        formats=["article"],
        constraints=["variation: auto"],
        previous_result=previous,
    )

    publication = "\n\n".join(unit["text"] for unit in result["script"]["units"])
    assert result["content_brief"]["selected_claim_refs"] == [claim_2]
    assert publication != "\n\n".join(unit["text"] for unit in previous["script"]["units"])
    assert distinct in publication

    factory._store.close()
    store.close()
