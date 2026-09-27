from content_factory.integrations import ExternalCallResult
from content_factory.knowledge import KnowledgeStore
from content_factory.research import OpenAIWebResearchAdapter
from content_factory.vertical_slice import ContentFactoryVerticalSlice, quality_check


class PromptRecordingFakeResearchAdapter:
    def __init__(self):
        self.calls = 0
        self.prompts = []

    def research(self, prompt: str) -> ExternalCallResult:
        self.calls += 1
        self.prompts.append(prompt)
        if self.calls == 1:
            text = '{"topic":"Convergent evolution","summary":"Similar pressures can produce similar traits.","claims":[{"id":"claim-1","text":"Similar environmental pressures can produce similar traits.","confidence":"high","source_ids":["source-1"],"evidence_ids":["evidence-1"],"scope":"bounded evolutionary examples","known_unknowns":["This does not establish a universal law."]}],"sources":[{"id":"source-1","title":"Example source","url":"https://example.com/source"}],"evidence":[{"id":"evidence-1","source_id":"source-1","excerpt":"Similar environmental pressures can produce similar traits.","locator":"example passage","provenance":"example-source"}],"editorial_angles":["similar problems can produce similar biological solutions"]}'
        else:
            text = '{"title":"Generated asset","content":"A grounded draft.","claim_refs":["claim-1"],"source_refs":["source-1"]}'
        return ExternalCallResult(
            integration_id="fake.research",
            status_code=200,
            response_id=f"resp-{self.calls}",
            payload={"output":[{"type":"message","content":[{"type":"output_text","text":text}]}]},
        )

    @staticmethod
    def text(result: ExternalCallResult) -> str:
        return OpenAIWebResearchAdapter.text(result)

    @staticmethod
    def sources(result: ExternalCallResult) -> list[dict[str, str]]:
        return []


class FakeResearchAdapter:
    def __init__(self) -> None:
        self.calls = 0

    def research(self, prompt: str) -> ExternalCallResult:
        self.calls += 1
        if self.calls == 1:
            text = '{"topic":"Convergent evolution","summary":"Similar pressures can produce similar traits.","claims":[{"id":"claim-1","text":"Similar environmental pressures can produce similar traits.","confidence":"high","source_ids":["source-1"],"evidence_ids":["evidence-1"],"scope":"bounded evolutionary examples","known_unknowns":["This does not establish a universal law."]}],"sources":[{"id":"source-1","title":"Example source","url":"https://example.com/source"}],"evidence":[{"id":"evidence-1","source_id":"source-1","excerpt":"Similar environmental pressures can produce similar traits.","locator":"example passage","provenance":"example-source"}],"editorial_angles":["similar problems can produce similar biological solutions"]}'
        else:
            text = '{"title":"Generated asset","content":"A grounded draft.","claim_refs":["claim-1"],"source_refs":["source-1"]}'
        return ExternalCallResult(
            integration_id="fake.research",
            status_code=200,
            response_id=f"resp-{self.calls}",
            payload={"output":[{"type":"message","content":[{"type":"output_text","text":text}]}]},
        )

    @staticmethod
    def text(result: ExternalCallResult) -> str:
        return OpenAIWebResearchAdapter.text(result)

    @staticmethod
    def sources(result: ExternalCallResult) -> list[dict[str, str]]:
        return []


def test_vertical_slice_produces_research_text_visual_and_qc():
    result = ContentFactoryVerticalSlice(FakeResearchAdapter()).run(
        run_id="run-test-1",
        brief="Explain why unrelated animals can evolve similar traits.",
    )
    assert result.quality["status"] == "PASS"
    assert result.quality["asset_count"] == 3
    assert result.research["claims"][0]["source_ids"] == ["source-1"]
    assert {a["format"] for a in result.package["package"]} == {"article", "social_post", "visual_card"}


def test_quality_check_rejects_unknown_claim_reference():
    result = quality_check(
        {"package":[{"id":"asset-1","content":"draft","claim_refs":["missing"],"source_refs":[]}]},
        {"claims":[{"id":"claim-1"}],"sources":[{"id":"source-1"}]},
    )
    assert result["status"] == "FAIL"
    assert "unknown claim" in result["errors"][0]

def test_vertical_slice_captures_and_reuses_knowledge(tmp_path):
    store = KnowledgeStore(tmp_path / "knowledge.sqlite3")
    first = ContentFactoryVerticalSlice(FakeResearchAdapter(), store).run(
        run_id="run-knowledge-1",
        brief="Explain why unrelated animals can evolve similar traits.",
    )
    assert first.research["knowledge"]["captured"] is True
    assert store.counts()["claims"] == 1

    refs = first.research["knowledge_refs"]
    assert refs["claims"]["claim-1"].startswith("kc-")
    assert refs["sources"]["source-1"].startswith("ks-")
    assert refs["evidence"]["evidence-1"].startswith("ke-")
    assert refs["claims"]["claim-1"] != "claim-1"
    assert refs["sources"]["source-1"] != "source-1"
    assert refs["evidence"]["evidence-1"] != "evidence-1"

    second_adapter = PromptRecordingFakeResearchAdapter()
    second = ContentFactoryVerticalSlice(second_adapter, store).run(
        run_id="run-knowledge-2",
        brief="Explain why unrelated animals can evolve similar traits.",
        formats=["article"],
    )
    assert second.research["knowledge"]["reusable_context_counts"]["claims"] == 1
    assert "Prior reusable knowledge" in second_adapter.prompts[0]
    assert '"claims"' in second_adapter.prompts[0]
    store.close()
