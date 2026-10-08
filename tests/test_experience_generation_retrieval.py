from content_factory.artifacts import ArtifactStore
from content_factory.factory_control import FactoryControlStore
from content_factory.knowledge import KnowledgeStore
from content_factory.knowledge_content import KnowledgeContentBuilder
from content_factory.runtime import Capability, ExecutionResult
from content_factory.runtime_store import RuntimeStore
from content_factory.workspace import ContentWorkspace


class CapturingFactory:
    def __init__(self, outputs, tmp_path):
        self._store = RuntimeStore(tmp_path / "runtime.sqlite3")
        self._artifacts = ArtifactStore(tmp_path / "artifacts")
        self.control = FactoryControlStore(tmp_path / "control.sqlite3")
        self.prompts = []
        self._capability = Capability(
            capability_id="fake.text.generate",
            input_contract=lambda item: None,
            executor=self._executor(outputs),
        )

    def _executor(self, outputs):
        state = {"index": 0}

        def execute(item, execution_id):
            self.prompts.append(item.requested_outcome)
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


def test_persistent_accept_experience_is_not_retrieved_by_next_generation(tmp_path):
    knowledge = KnowledgeStore(tmp_path / "knowledge.sqlite3")
    research = {
        "claims": [{
            "id": "claim-1",
            "text": "A documented historical claim.",
            "confidence": "high",
            "source_ids": ["source-1"],
            "evidence_ids": ["evidence-1"],
            "scope": "test",
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
    knowledge.capture(run_id="research-1", research=research)
    claim_id = knowledge._connection.execute(
        "SELECT claim_id FROM knowledge_claims"
    ).fetchone()["claim_id"]
    evidence_id = knowledge._connection.execute(
        "SELECT evidence_id FROM knowledge_evidence"
    ).fetchone()["evidence_id"]
    knowledge.promote_claim(claim_id, decision_ref="DEC-EXPERIENCE-001")

    factory = CapturingFactory([
        '{"ideas":[{"idea_id":"idea-1","title":"Test","angle":"Documented claim","audience":"general","purpose":"explain","formats":["article"]}]}',
        '{"brief_id":"brief-1","title":"Test","objective":"Explain","audience":"general","angle":"Documented claim","selected_claim_refs":["'+claim_id+'"],"evidence_refs":["'+evidence_id+'"],"editorial_points":[{"point_id":"point-1","text":"Explain the claim","role":"development","claim_refs":["'+claim_id+'"],"evidence_refs":["'+evidence_id+'"]}],"content_elements":[{"element_id":"element-1","kind":"narration","editorial_point_ids":["point-1"],"purpose":"explain","production_intent":"article paragraph","claim_refs":["'+claim_id+'"],"evidence_refs":["'+evidence_id+'"]}],"formats":["article"],"constraints":["test constraint"]}',
        '{"spec_id":"spec-1","title":"Test","objective":"Explain","audience":"general","format":"article","tone":"clear","structure":["hook","development"],"constraints":["test constraint"],"claim_refs":["'+claim_id+'"],"evidence_refs":["'+evidence_id+'"]}',
        '{"script_id":"script-1","title":"Test","variation_mode":"scene","units":[{"unit_id":"unit-1","kind":"hook","text":"Documented claim.","visual_intent":"show context","claim_refs":["'+claim_id+'"],"evidence_refs":["'+evidence_id+'"]},{"unit_id":"unit-2","kind":"narration","text":"The evidence supports the claim.","visual_intent":"show evidence","claim_refs":["'+claim_id+'"],"evidence_refs":["'+evidence_id+'"]},{"unit_id":"unit-3","kind":"conclusion","text":"The takeaway is documented context.","visual_intent":"show takeaway","claim_refs":["'+claim_id+'"],"evidence_refs":["'+evidence_id+'"]}]}',
    ], tmp_path)

    marker = "UNIQUE_ACCEPT_EXPERIENCE_MARKER_20261008"
    record = factory.control.record_experience(
        run_id="previous-run",
        prompt={"brief": marker},
        context={"marker": marker},
        generated={"text": marker},
        decision="ACCEPT",
        final={"text": marker},
        qc={"status": "PASSED"},
        provenance={"run_id": "previous-run", "source": "experiment"},
    )
    assert factory.control.list_experiences() == [record]

    KnowledgeContentBuilder(ContentWorkspace(factory), knowledge).build(
        run_id="next-run",
        topic="Documented historical claim",
        audience="general",
        goal="explain",
        formats=["article"],
        constraints=["test constraint"],
    )

    assert factory.prompts
    assert all(marker not in prompt for prompt in factory.prompts)

    factory.control.close()
    factory._store.close()
    knowledge.close()
