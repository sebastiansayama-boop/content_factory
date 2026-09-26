from content_factory.integrations import ExternalCallResult
from content_factory.research import OpenAIWebResearchAdapter
from content_factory.vertical_slice import ContentFactoryVerticalSlice, quality_check


class FakeResearchAdapter:
    def __init__(self) -> None:
        self.calls = 0

    def research(self, prompt: str) -> ExternalCallResult:
        self.calls += 1
        if self.calls == 1:
            text = '{"topic":"Convergent evolution","summary":"Similar pressures can produce similar traits.","claims":[{"id":"claim-1","text":"Similar environmental pressures can produce similar traits.","confidence":"high","source_ids":["source-1"]}],"sources":[{"id":"source-1","title":"Example source","url":"https://example.com/source"}],"editorial_angles":["similar problems can produce similar biological solutions"]}'
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