from content_factory.artifacts import ArtifactStore
from content_factory.knowledge import KnowledgeStore
from content_factory.knowledge_content import KnowledgeContentBuilder, _structure_steps
from content_factory.runtime import Capability, ExecutionResult
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


def test_knowledge_content_builder_creates_editorial_spec_script_and_plan(tmp_path):
    store = KnowledgeStore(tmp_path / "knowledge.sqlite3")
    store.capture(run_id="research-1", research=_research())
    claim_id = store._connection.execute(
        "SELECT claim_id FROM knowledge_claims"
    ).fetchone()["claim_id"]
    store.promote_claim(claim_id, decision_ref="DEC-EDITORIAL-001")

    outputs = [
        '{"ideas":[{"idea_id":"idea-1","title":"Spirit Houses","angle":"What offerings mean","audience":"general","purpose":"explain","formats":["short_video"]}]}',
        '{"brief_id":"brief-1","title":"Spirit Houses","objective":"Explain offerings","audience":"general","angle":"What offerings mean","selected_claim_refs":["'+claim_id+'"],"evidence_refs":["ke-PLACEHOLDER"],"editorial_points":[{"point_id":"point-1","text":"Explain what offerings mean","role":"development"}],"content_elements":[{"element_id":"element-1","kind":"narration","editorial_point_ids":["point-1"],"purpose":"explain","production_intent":"voice narration"}],"formats":["short_video"],"constraints":["no alcohol"]}',
        '{"spec_id":"spec-1","title":"Spirit Houses","objective":"Explain offerings","audience":"general","format":"short_video","tone":"clear","structure":["hook","explanation"],"constraints":["no alcohol"]}',
        '{"script_id":"script-1","title":"Spirit Houses","variation_mode":"scene","units":[{"unit_id":"unit-1","kind":"hook","text":"Why are offerings placed at spirit houses?","visual_intent":"show spirit house"},{"unit_id":"unit-2","kind":"beat","text":"Here is the context behind the practice.","visual_intent":"show context"},{"unit_id":"unit-3","kind":"narration","text":"The evidence supports the documented association.","visual_intent":"show evidence"},{"unit_id":"unit-4","kind":"cta","text":"The takeaway is to distinguish the practice from assumptions about it.","visual_intent":"show takeaway"}]}',
    ]
    evidence_id = store._connection.execute(
        "SELECT evidence_id FROM knowledge_evidence"
    ).fetchone()["evidence_id"]
    outputs = [item.replace("ke-PLACEHOLDER", evidence_id) for item in outputs]

    factory = FakeFactory(outputs, tmp_path)
    result = KnowledgeContentBuilder(ContentWorkspace(factory), store).build(
        run_id="run-1",
        topic="Thai spirit houses offerings",
        audience="general",
        goal="explain",
        formats=["short_video"],
        constraints=["no alcohol"],
    )

    assert result["editorial"]["selected_idea"]["idea_id"] == "idea-1"
    assert result["content_brief"]["brief_id"] == "brief-run-1"
    assert result["content_brief"]["selected_claim_refs"] == [claim_id]
    assert result["content_brief"]["editorial_points"][0]["claim_refs"] == [claim_id]
    assert result["content_brief"]["content_elements"][0]["editorial_point_ids"] == ["point-1"]
    assert result["content_spec"]["spec_id"] == "spec-1"
    assert result["script"]["script_id"] == "script-1"
    assert result["script"]["units"][0]["claim_refs"] == [claim_id]
    assert result["production_plan"]["asset_requests"][0]["script_unit_id"] == "unit-1"
    assert result["production_plan"]["asset_requests"][0]["content_element_ids"] == ["element-1"]
    assert len(store.usages_for_claim(claim_id)) == 2
    factory._store.close()
    store.close()


def test_knowledge_content_builder_rejects_unknown_provenance(tmp_path):
    store = KnowledgeStore(tmp_path / "knowledge.sqlite3")
    store.capture(run_id="research-1", research=_research())
    claim_id = store._connection.execute(
        "SELECT claim_id FROM knowledge_claims"
    ).fetchone()["claim_id"]
    store.promote_claim(claim_id, decision_ref="DEC-EDITORIAL-002")

    factory = FakeFactory([
        '{"ideas":[{"idea_id":"idea-1","title":"Bad","angle":"Bad","audience":"general","purpose":"bad","formats":["short_video"],"claim_refs":["kc-does-not-exist"],"evidence_refs":["ke-does-not-exist"]}]}'
    ], tmp_path)
    try:
        KnowledgeContentBuilder(ContentWorkspace(factory), store).build(
            run_id="run-2",
            topic="Thai spirit houses offerings",
            audience="general",
            goal="explain",
            formats=["short_video"],
            constraints=[],
        )
    except ValueError as exc:
        assert "unknown knowledge claim refs" in str(exc)
    else:
        raise AssertionError("unknown durable provenance must be rejected")
    factory._store.close()
    store.close()


def test_knowledge_content_builder_recovers_omitted_provenance_refs(tmp_path):
    store = KnowledgeStore(tmp_path / "knowledge.sqlite3")
    store.capture(run_id="research-omitted-refs", research=_research())
    claim_id = store._connection.execute(
        "SELECT claim_id FROM knowledge_claims"
    ).fetchone()["claim_id"]
    evidence_id = store._connection.execute(
        "SELECT evidence_id FROM knowledge_evidence"
    ).fetchone()["evidence_id"]
    store.promote_claim(claim_id, decision_ref="DEC-EDITORIAL-003")

    outputs = [
        '{"ideas":[{"idea_id":"idea-1","title":"Spirit Houses","angle":"What offerings mean","audience":"general","purpose":"explain","formats":["short_video"]}]}',
        '{"brief_id":"brief-1","title":"Spirit Houses","objective":"Explain offerings","audience":"general","angle":"What offerings mean","editorial_points":[{"point_id":"point-1","text":"Explain what offerings mean","role":"development"}],"content_elements":[{"element_id":"element-1","kind":"narration","editorial_point_ids":["point-1"],"purpose":"explain","production_intent":"voice narration"}],"formats":["short_video"],"constraints":["no alcohol"]}',
        '{"spec_id":"spec-1","title":"Spirit Houses","objective":"Explain offerings","audience":"general","format":"short_video","tone":"clear","structure":["hook","explanation"],"constraints":["no alcohol"],"style_bible":{}}',
        '{"script_id":"script-1","title":"Spirit Houses","variation_mode":"scene","units":[{"unit_id":"unit-1","kind":"hook","text":"Offerings are commonly associated with spirit houses.","visual_intent":"show spirit house"},{"unit_id":"unit-2","kind":"beat","text":"Here is the context behind the practice.","visual_intent":"show context"},{"unit_id":"unit-3","kind":"narration","text":"The evidence supports the documented association.","visual_intent":"show evidence"},{"unit_id":"unit-4","kind":"cta","text":"The takeaway is to distinguish the practice from assumptions about it.","visual_intent":"show takeaway"}]}',
    ]

    factory = FakeFactory(outputs, tmp_path)
    result = KnowledgeContentBuilder(ContentWorkspace(factory), store).build(
        run_id="run-omitted-refs",
        topic="Thai spirit houses offerings",
        audience="general",
        goal="explain",
        formats=["short_video"],
        constraints=["no alcohol"],
    )

    assert result["editorial"]["selected_idea"]["claim_refs"] == [claim_id]
    assert result["editorial"]["selected_idea"]["evidence_refs"] == [evidence_id]
    assert result["content_brief"]["selected_claim_refs"] == [claim_id]
    assert result["content_brief"]["evidence_refs"] == [evidence_id]
    assert result["content_brief"]["editorial_points"][0]["claim_refs"] == [claim_id]
    assert result["content_brief"]["editorial_points"][0]["evidence_refs"] == [evidence_id]
    assert result["content_brief"]["content_elements"][0]["claim_refs"] == [claim_id]
    assert result["content_brief"]["content_elements"][0]["evidence_refs"] == [evidence_id]
    assert result["content_spec"]["claim_refs"] == [claim_id]
    assert result["content_spec"]["evidence_refs"] == [evidence_id]
    assert result["script"]["units"][0]["claim_refs"] == [claim_id]
    assert result["script"]["units"][0]["evidence_refs"] == [evidence_id]
    factory._store.close()
    store.close()


def test_knowledge_content_builder_enforces_requested_format(tmp_path):
    store = KnowledgeStore(tmp_path / "knowledge.sqlite3")
    store.capture(run_id="research-format", research=_research())
    claim_id = store._connection.execute(
        "SELECT claim_id FROM knowledge_claims"
    ).fetchone()["claim_id"]
    evidence_id = store._connection.execute(
        "SELECT evidence_id FROM knowledge_evidence"
    ).fetchone()["evidence_id"]
    store.promote_claim(claim_id, decision_ref="DEC-FORMAT-001")

    outputs = [
        '{"ideas":[{"idea_id":"idea-1","title":"Spirit Houses","angle":"What offerings mean","audience":"general","purpose":"explain","formats":["short_video"],"claim_refs":["'+claim_id+'"],"evidence_refs":["'+evidence_id+'"]}]}',
        '{"brief_id":"brief-1","title":"Spirit Houses","objective":"Explain offerings","audience":"general","angle":"What offerings mean","editorial_points":[{"point_id":"point-1","text":"Explain what offerings mean","role":"development","claim_refs":["'+claim_id+'"],"evidence_refs":["'+evidence_id+'"]}],"content_elements":[{"element_id":"element-1","kind":"narration","editorial_point_ids":["point-1"],"purpose":"explain","production_intent":"article paragraph","claim_refs":["'+claim_id+'"],"evidence_refs":["'+evidence_id+'"]}],"formats":["short_video"],"constraints":["none"]}',
        '{"spec_id":"spec-1","title":"Spirit Houses","objective":"Explain offerings","audience":"general","format":"short_video","tone":"clear","structure":["hook","explanation"],"constraints":["none"],"claim_refs":["'+claim_id+'"],"evidence_refs":["'+evidence_id+'"]}',
        '{"script_id":"script-1","title":"Spirit Houses","variation_mode":"scene","units":[{"unit_id":"unit-1","kind":"hook","text":"Why are offerings placed at spirit houses?","visual_intent":"show spirit house","claim_refs":["'+claim_id+'"],"evidence_refs":["'+evidence_id+'"]},{"unit_id":"unit-2","kind":"beat","text":"Here is the context behind the practice.","visual_intent":"show context","claim_refs":["'+claim_id+'"],"evidence_refs":["'+evidence_id+'"]},{"unit_id":"unit-3","kind":"narration","text":"The evidence supports the documented association.","visual_intent":"show evidence","claim_refs":["'+claim_id+'"],"evidence_refs":["'+evidence_id+'"]},{"unit_id":"unit-4","kind":"cta","text":"The takeaway is to distinguish the practice from assumptions about it.","visual_intent":"show takeaway","claim_refs":["'+claim_id+'"],"evidence_refs":["'+evidence_id+'"]}]}',
    ]
    factory = FakeFactory(outputs, tmp_path)
    result = KnowledgeContentBuilder(ContentWorkspace(factory), store).build(
        run_id="run-format",
        topic="Thai spirit houses offerings",
        audience="general",
        goal="explain",
        formats=["article"],
        constraints=["none"],
    )

    assert result["content_brief"]["formats"] == ["article"]
    assert result["content_spec"]["format"] == "article"
    assert result["production_plan"]["format"] == "article"
    factory._store.close()
    store.close()


def test_knowledge_content_builder_rejects_high_certainty_epistemic_overclaim(tmp_path):
    store = KnowledgeStore(tmp_path / "knowledge.sqlite3")
    store.capture(run_id="research-epistemic", research=_research())
    claim_id = store._connection.execute(
        "SELECT claim_id FROM knowledge_claims"
    ).fetchone()["claim_id"]
    evidence_id = store._connection.execute(
        "SELECT evidence_id FROM knowledge_evidence"
    ).fetchone()["evidence_id"]
    store.promote_claim(claim_id, decision_ref="DEC-EPISTEMIC-001")

    outputs = [
        '{"ideas":[{"idea_id":"idea-1","title":"Spirit Houses","angle":"What offerings mean","audience":"general","purpose":"explain","formats":["article"],"claim_refs":["'+claim_id+'"],"evidence_refs":["'+evidence_id+'"]}]}',
        '{"brief_id":"brief-1","title":"Spirit Houses","objective":"Explain offerings","audience":"general","angle":"What offerings mean","editorial_points":[{"point_id":"point-1","text":"Explain the documented association","role":"development","claim_refs":["'+claim_id+'"],"evidence_refs":["'+evidence_id+'"]}],"content_elements":[{"element_id":"element-1","kind":"narration","editorial_point_ids":["point-1"],"purpose":"explain","production_intent":"article paragraph","claim_refs":["'+claim_id+'"],"evidence_refs":["'+evidence_id+'"]}],"formats":["article"],"constraints":["none"]}',
        '{"spec_id":"spec-1","title":"Spirit Houses","objective":"Explain offerings","audience":"general","format":"article","tone":"clear","structure":["hook","context","development","conclusion"],"constraints":["none"],"claim_refs":["'+claim_id+'"],"evidence_refs":["'+evidence_id+'"]}',
        '{"script_id":"script-1","title":"Spirit Houses","variation_mode":"scene","units":[{"unit_id":"unit-1","kind":"hook","text":"The evidence shows a documented association.","visual_intent":"show spirit house","claim_refs":["'+claim_id+'"],"evidence_refs":["'+evidence_id+'"]},{"unit_id":"unit-2","kind":"beat","text":"The practice has a specific cultural context.","visual_intent":"show context","claim_refs":["'+claim_id+'"],"evidence_refs":["'+evidence_id+'"]},{"unit_id":"unit-3","kind":"narration","text":"The evidence supports this documented association.","visual_intent":"show evidence","claim_refs":["'+claim_id+'"],"evidence_refs":["'+evidence_id+'"]},{"unit_id":"unit-4","kind":"cta","text":"This proves that the practice has one universal meaning.","visual_intent":"show takeaway","claim_refs":["'+claim_id+'"],"evidence_refs":["'+evidence_id+'"]}]}',
    ]
    factory = FakeFactory(outputs, tmp_path)
    try:
        KnowledgeContentBuilder(ContentWorkspace(factory), store).build(
            run_id="run-epistemic",
            topic="Thai spirit houses offerings",
            audience="general",
            goal="explain",
            formats=["article"],
            constraints=[],
        )
    except Exception as exc:
        assert "exceeds accepted epistemic scope" in str(exc)
    else:
        raise AssertionError("high-certainty epistemic overclaim must be rejected")
    factory._store.close()
    store.close()



def test_structure_steps_normalizes_structured_model_output():
    assert _structure_steps([
        {
            "step": "Introduction",
            "purpose": "set context",
            "claim_refs": ["kc-1"],
            "evidence_refs": ["ke-1"],
        },
        "Development",
        {
            "step": "Conclusion",
            "purpose": "summarize",
        },
    ]) == ["Introduction", "Development", "Conclusion"]


def test_knowledge_content_builder_retries_unknown_spec_ids(tmp_path):
    import json

    store = KnowledgeStore(tmp_path / "knowledge.sqlite3")
    store.capture(run_id="research-provenance-retry", research=_research())
    claim = store._connection.execute("SELECT claim_id FROM knowledge_claims").fetchone()["claim_id"]
    evidence = store._connection.execute("SELECT evidence_id FROM knowledge_evidence").fetchone()["evidence_id"]
    store.promote_claim(claim, decision_ref="DEC-PROVENANCE-RETRY")

    idea = {
        "ideas": [{
            "idea_id": "idea-1", "title": "Spirit houses", "angle": "Offerings",
            "audience": "general", "purpose": "explain", "formats": ["article"],
            "claim_refs": [claim], "evidence_refs": [evidence],
        }],
    }
    brief = {
        "title": "Spirit houses", "objective": "Explain offerings", "angle": "Offerings",
        "selected_claim_refs": [claim], "evidence_refs": [evidence],
        "editorial_points": [{
            "point_id": "point-1", "text": "Offerings", "role": "development",
            "claim_refs": [claim], "evidence_refs": [evidence],
        }],
        "content_elements": [{
            "element_id": "element-1", "kind": "narration",
            "editorial_point_ids": ["point-1"], "purpose": "Explain",
            "production_intent": "article paragraph",
            "claim_refs": [claim], "evidence_refs": [evidence],
        }],
    }
    spec = {
        "spec_id": "spec-1", "title": "Spirit houses",
        "objective": "Explain offerings", "audience": "general",
        "format": "article", "tone": "clear",
        "structure": ["hook", "context", "development", "conclusion"],
        "constraints": ["use accepted evidence"], "style_bible": {},
        "claim_refs": [claim], "evidence_refs": [evidence],
    }
    invalid_spec = {**spec, "claim_refs": ["kc-9876543210"]}
    script = {
        "script_id": "script-1", "title": "Spirit houses", "variation_mode": "scene",
        "units": [
            {"unit_id": f"unit-{i}", "kind": "narration", "text": "Explain supported claim",
             "visual_intent": "show supporting evidence",
             "claim_refs": [claim], "evidence_refs": [evidence]}
            for i in range(1, 5)
        ],
    }
    factory = FakeFactory(
        [json.dumps(value) for value in (idea, brief, invalid_spec, spec, script)],
        tmp_path,
    )
    result = KnowledgeContentBuilder(ContentWorkspace(factory), store).build(
        run_id="run-provenance-retry",
        topic="Thai spirit houses offerings",
        audience="general",
        goal="explain",
        formats=["article"],
        constraints=[],
    )
    assert result["content_spec"]["claim_refs"] == [claim]
    assert result["content_spec"]["evidence_refs"] == [evidence]

    factory._store.close()
    store.close()
