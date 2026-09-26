from content_factory.artifacts import ArtifactStore
from content_factory.runtime import Capability, ExecutionResult
from content_factory.runtime_store import RuntimeStore
from content_factory.workspace import ContentWorkspace, WorkspaceError, _json_from_text


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
        '{"summary":"A","themes":["one"],"stories":[{"id":"story-1","title":"T","angle":"A","why":"W","evidence":[]}],"moments":[]}',
        tmp_path,
    )
    # Use the production verification contract supplied by the service shape.
    fake._verify = fake._verify
    result = ContentWorkspace(fake).analyze(source="A substantive source", title="Interview")
    assert result["stories"][0]["id"] == "story-1"
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
    fake = FakeFactory(
        '{"story":{"id":"story-1","title":"T","angle":"A"},"package":[{"id":"asset-1","format":"article","title":"T","content":"Body","source_refs":[]}]}'
        , tmp_path,
    )
    result = ContentWorkspace(fake).produce(
        source="source",
        story={
            "id": "story-1",
            "title": "T",
            "angle": "A",
            "evidence": [
                {"id": "evidence-1", "quote": "Source evidence", "location": "source"}
            ],
            "claims": [
                {
                    "id": "claim-1",
                    "text": "A factual claim",
                    "evidence_refs": ["evidence-1"],
                }
            ],
        },
        formats=["article"],
    )
    assert result["story_id"] == "story-1"
    assert result["package"][0]["format"] == "article"
    fake._store.close()


def test_regenerate_executes_only_claim_affected_asset(tmp_path):
    fake = FakeFactory(
        '{"id":"asset-1","format":"article","title":"Revised","content":"Updated body","source_refs":["evidence-1"],"claim_refs":["claim-1"]}',
        tmp_path,
    )
    workspace = ContentWorkspace(fake)
    story = {
        "id": "story-1",
        "title": "T",
        "angle": "A",
        "evidence": [
            {"id": "evidence-1", "quote": "Evidence one", "location": "source"},
            {"id": "evidence-2", "quote": "Evidence two", "location": "source"},
        ],
        "claims": [
            {"id": "claim-1", "text": "Changed claim", "evidence_refs": ["evidence-1"]},
            {"id": "claim-2", "text": "Unchanged claim", "evidence_refs": ["evidence-2"]},
        ],
    }
    package = {
        "package": [
            {
                "id": "asset-1",
                "format": "article",
                "title": "Original",
                "content": "Original body",
                "source_refs": ["evidence-1"],
                "claim_refs": ["claim-1"],
            },
            {
                "id": "asset-2",
                "format": "social_post",
                "title": "Keep",
                "content": "Keep body",
                "source_refs": ["evidence-2"],
                "claim_refs": ["claim-2"],
            },
        ]
    }

    result = workspace.regenerate(
        source="source",
        story=story,
        package=package,
        changed_claim_ids=["claim-1"],
    )

    assert result["package"][0]["content"] == "Updated body"
    assert result["package"][1]["content"] == "Keep body"
    assert result["regeneration"]["regenerated_asset_ids"] == ["asset-1"]
    assert result["regeneration"]["retained_asset_ids"] == ["asset-2"]
    fake._store.close()
