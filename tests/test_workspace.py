from content_factory.artifacts import ArtifactStore
from content_factory.runtime import Capability, ExecutionResult
from content_factory.runtime_store import RuntimeStore
from content_factory.workspace import ContentWorkspace, WorkspaceError, _json_from_text, _source_id


class FakeFactory:
    def __init__(self, output, tmp_path):
        self.output = output
        self._store = RuntimeStore(tmp_path / "runtime.sqlite3")
        self._artifacts = ArtifactStore(tmp_path / "artifacts")
        self._capability = Capability(
            capability_id="fake.text.generate",
            input_contract=lambda item: None,
            executor=self._execute,
        )

    def _execute(self, item, execution_id):
        return ExecutionResult(
            execution_id=execution_id,
            capability_id=self._capability.capability_id,
            output_revision_id=f"fake:{item.revision_id}",
            payload=self.output,
        )

    @staticmethod
    def _verify(_, execution):
        from content_factory.runtime import VerificationResult

        return VerificationResult(
            output_revision_id=execution.output_revision_id,
            passed=bool(str(execution.payload).strip()),
        )


def test_json_from_markdown_fence():
    assert _json_from_text('```json\n{"summary":"ok"}\n```') == {"summary": "ok"}


def test_analyze_builds_source_grounded_editorial_request(tmp_path):
    fake = FakeFactory(
        '{"summary":"A","themes":["one"],"stories":[{"id":"story-1","title":"T","angle":"A","why":"W","evidence":[{"id":"evidence-1","quote":"A substantive source","location":"source"}]}],"moments":[]}',
        tmp_path,
    )
    result = ContentWorkspace(fake).analyze(source="A substantive source", title="Interview")
    assert result["stories"][0]["id"] == "story-1"
    assert result["stories"][0]["source_id"] == _source_id("A substantive source")
    assert result["title"] == "Interview"
    fake._store.close()


def test_produce_requires_story_identity(tmp_path):
    fake = FakeFactory("{}", tmp_path)
    try:
        ContentWorkspace(fake).produce(source="source", story={})
    except WorkspaceError as exc:
        assert "story.id" in str(exc)
    else:
        raise AssertionError("missing story identity must fail")
    finally:
        fake._store.close()


def test_produce_returns_package_and_runtime_identity(tmp_path):
    source = "source"
    story = {
        "id": "story-1",
        "title": "T",
        "angle": "A",
        "source_id": _source_id(source),
        "evidence": [{"id": "evidence-1", "quote": "source", "location": "source"}],
    }
    fake = FakeFactory(
        '{"story":{"id":"story-1","title":"T","angle":"A"},"package":[{"id":"asset-1","format":"article","title":"T","content":"Body","source_refs":["evidence-1"]}]}',
        tmp_path,
    )
    result = ContentWorkspace(fake).produce(
        source=source,
        story=story,
        formats=["article"],
    )
    assert result["story_id"] == "story-1"
    assert result["package"][0]["format"] == "article"
    assert result["package"][0]["source_refs"] == ["evidence-1"]
    fake._store.close()
