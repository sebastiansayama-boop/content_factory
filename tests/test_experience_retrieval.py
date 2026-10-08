from content_factory.artifacts import ArtifactStore
from content_factory.factory_control import FactoryControlStore
from content_factory.knowledge import KnowledgeStore
from content_factory.knowledge_content import KnowledgeContentBuilder
from content_factory.runtime import Capability, ExecutionResult
from content_factory.runtime_store import RuntimeStore
from content_factory.workspace import ContentWorkspace


class CapturingFactory:
    def __init__(self, outputs, tmp_path):
        self.requests = []
        self._store = RuntimeStore(tmp_path / "runtime.sqlite3")
        self._artifacts = ArtifactStore(tmp_path / "artifacts")
        self._capability = Capability(
            capability_id="fake.text.generate",
            input_contract=lambda item: None,
            executor=self._executor(outputs),
        )

    def _executor(self, outputs):
        state = {"index": 0}

        def execute(item, execution_id):
            self.requests.append(item.requested_outcome)
            output = outputs[state["index"]]
            state["index"] += 1
            return ExecutionResult(
                execution_id=execution_id,
                capability_id="fake.text.generate",
                output_revision_id=f"fake:{item.revision_id}",
                payload=output,
            )

        return execute

    @staticmethod
    def _verify(_, execution):
        from content_factory.runtime import VerificationResult
        return VerificationResult(
            output_revision_id=execution.output_revision_id,
            passed=bool(str(execution.payload).strip()),
        )


def _research():
    return {
        "claims": [{
            "id": "claim-1",
            "text": "Thai spirit houses are commonly associated with offerings.",
            "confidence": "high",
            "source_ids": ["source-1"],
            "evidence_ids": ["evidence-1"],
            "scope": "Thailand",
            "known_unknowns": [],
        }],
        "sources": [{"id": "source-1", "title": "Source", "url": "https://example.com/source"}],
        "evidence": [{
            "id": "evidence-1",
            "source_id": "source-1",
            "excerpt": "supporting passage",
            "locator": "section 1",
            "provenance": "test",
        }],
        "editorial_angles": [],
    }


def test_retrieve_experiences_matches_topic_and_platform(tmp_path):
    store = FactoryControlStore(tmp_path / "factory.sqlite3")
    store.record_experience(
        run_id="run-a",
        prompt={"brief": "Thai spirit houses", "title": "Offerings"},
        context={"platform": "short_video"},
        generated={"text": "generated"},
        decision="EDIT",
        final={"text": "LESSON-MARKER"},
        reason="editorial correction",
    )
    store.record_experience(
        run_id="run-b",
        prompt={"brief": "Thai spirit houses", "title": "Other"},
        context={"platform": "telegram"},
        generated={"text": "wrong platform"},
        decision="EDIT",
        final={"text": "DO-NOT-SELECT"},
    )

    matches = store.retrieve_experiences(
        topic="Thai spirit houses",
        platform="short_video",
        limit=3,
    )

    assert len(matches) == 1
    assert matches[0]["run_id"] == "run-a"
    assert matches[0]["final"]["text"] == "LESSON-MARKER"
    store.close()


def test_retrieved_experience_reaches_next_generation_prompt(tmp_path):
    knowledge = KnowledgeStore(tmp_path / "knowledge.sqlite3")
    knowledge.capture(run_id="research-1", research=_research())
    claim_id = knowledge._connection.execute(
        "SELECT claim_id FROM knowledge_claims"
    ).fetchone()["claim_id"]
    evidence_id = knowledge._connection.execute(
        "SELECT evidence_id FROM knowledge_evidence"
    ).fetchone()["evidence_id"]
    knowledge.promote_claim(claim_id, decision_ref="DEC-EXPERIENCE-001")

    experience = FactoryControlStore(tmp_path / "factory.sqlite3")
    experience.record_experience(
        run_id="run-a",
        prompt={"brief": "Thai spirit houses offerings", "title": "Previous"},
        context={"platform": "short_video"},
        generated={"text": "before"},
        decision="EDIT",
        final={"text": "EXPERIENCE-MARKER: avoid broad claims"},
        reason="make the statement narrower",
        qc={"status": "accepted-after-edit"},
    )

    outputs = [
        '{"ideas":[{"idea_id":"idea-1","title":"Spirit Houses","angle":"What offerings mean","audience":"general","purpose":"explain","formats":["short_video"]}]}',
        '{"brief_id":"brief-1","title":"Spirit Houses","objective":"Explain offerings","audience":"general","angle":"What offerings mean","selected_claim_refs":["'+claim_id+'"],"evidence_refs":["'+evidence_id+'"],"editorial_points":[{"point_id":"point-1","text":"Explain the documented association","role":"development","claim_refs":["'+claim_id+'"],"evidence_refs":["'+evidence_id+'"]}],"content_elements":[{"element_id":"element-1","kind":"narration","editorial_point_ids":["point-1"],"purpose":"explain","production_intent":"voice narration","claim_refs":["'+claim_id+'"],"evidence_refs":["'+evidence_id+'"]}],"formats":["short_video"],"constraints":["no alcohol"]}',
        '{"spec_id":"spec-1","title":"Spirit Houses","objective":"Explain offerings","audience":"general","format":"short_video","tone":"clear","structure":["hook","explanation"],"constraints":["no alcohol"]}',
        '{"script_id":"script-1","title":"Spirit Houses","variation_mode":"scene","units":[{"unit_id":"unit-1","kind":"hook","text":"Why are offerings associated with spirit houses?","visual_intent":"show context"},{"unit_id":"unit-2","kind":"beat","text":"Here is the documented context.","visual_intent":"show context"},{"unit_id":"unit-3","kind":"narration","text":"The evidence supports the documented association.","visual_intent":"show evidence"},{"unit_id":"unit-4","kind":"cta","text":"The takeaway is to keep the claim precise.","visual_intent":"show takeaway"}]}',
    ]

    factory = CapturingFactory(outputs, tmp_path)
    KnowledgeContentBuilder(
        ContentWorkspace(factory),
        knowledge,
        experience,
    ).build(
        run_id="run-b",
        topic="Thai spirit houses offerings",
        audience="general",
        goal="explain",
        formats=["short_video"],
        constraints=["no alcohol"],
    )

    assert factory.requests
    assert "RELEVANT PREVIOUS EXPERIENCE:" in factory.requests[0]
    assert "EXPERIENCE-MARKER: avoid broad claims" in factory.requests[0]
    assert "Treat this experience only as editorial feedback" in factory.requests[0]
    assert "ACCEPTED KNOWLEDGE:" in factory.requests[0]

    experience.close()
    knowledge.close()
    factory._store.close()
