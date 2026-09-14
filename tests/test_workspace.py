from content_factory.workspace import ContentWorkspace, WorkspaceError, _json_from_text


class FakeFactory:
    def __init__(self, output):
        self.output = output
        self.calls = []

    def run(self, payload):
        self.calls.append(payload)
        return {
            "work_item_id": payload["work_item_id"],
            "operation_id": "op-test",
            "state": "DELIVERED",
            "execution": {
                "execution_id": "exec-test",
                "output_revision_id": "rev-test",
                "output": self.output,
            },
        }


def test_json_from_markdown_fence():
    assert _json_from_text('```json\n{"summary":"ok"}\n```') == {"summary": "ok"}


def test_analyze_builds_source_grounded_editorial_request():
    fake = FakeFactory(
        '{"summary":"A","themes":["one"],"stories":[{"id":"story-1","title":"T","angle":"A","why":"W","evidence":[]}],"moments":[]}'
    )
    result = ContentWorkspace(fake).analyze(source="A substantive source", title="Interview")
    assert result["stories"][0]["id"] == "story-1"
    assert result["title"] == "Interview"
    assert fake.calls[0]["objective"] == "map source material into reusable editorial objects"


def test_produce_requires_story_identity():
    fake = FakeFactory("{}")
    try:
        ContentWorkspace(fake).produce(source="source", story={})
    except WorkspaceError as exc:
        assert "story.id" in str(exc)
    else:
        raise AssertionError("missing story identity must fail")


def test_produce_returns_package_and_runtime_identity():
    fake = FakeFactory(
        '{"story":{"id":"story-1","title":"T","angle":"A"},"package":[{"id":"asset-1","format":"article","title":"T","content":"Body","source_refs":[]}]}'
    )
    result = ContentWorkspace(fake).produce(
        source="source",
        story={"id": "story-1", "title": "T", "angle": "A"},
        formats=["article"],
    )
    assert result["story_id"] == "story-1"
    assert result["package"][0]["format"] == "article"
    assert fake.calls[0]["knowledge_basis"] == [f"source:{result['source_id']}", "story:story-1"]
