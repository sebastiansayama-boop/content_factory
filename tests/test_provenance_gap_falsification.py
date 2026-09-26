from content_factory.artifacts import ArtifactStore
from content_factory.runtime import Capability, ExecutionResult
from content_factory.runtime_store import RuntimeStore
from content_factory.workspace import ContentWorkspace


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


def test_produce_exposes_claim_level_provenance_for_downstream_asset(tmp_path):
    """
    Regression test for the claim-level provenance contract.

    Given a selected story grounded in evidence-4 and claim-1 explicitly
    supported by evidence-4, production must expose the relationship needed
    to answer: "which assets are affected if claim-1 changes?"
    """
    fake = FakeFactory(
        '{"story":{"id":"story-1","title":"T","angle":"A"},'
        '"package":[{"id":"asset-1","format":"article","title":"T",'
        '"content":"Body","source_refs":["evidence-4"],"claim_refs":["claim-1"]}]}',
        tmp_path,
    )

    result = ContentWorkspace(fake).produce(
        source="Evidence-4 supports claim-1.",
        story={
            "id":"story-1",
            "title":"T",
            "angle":"A",
            "evidence":[
                {
                    "id":"evidence-4",
                    "quote":"Evidence supporting claim-1",
                    "location":"source",
                }
            ],
            "claims":[
                {
                    "id":"claim-1",
                    "text":"Claim 1",
                    "evidence_refs":["evidence-4"],
                }
            ],
        },
        formats=["article"],
    )

    asset = result["package"][0]
    assert asset["claim_refs"] == ["claim-1"]


def test_produce_derives_claim_refs_from_asset_evidence(tmp_path):
    fake = FakeFactory(
        '{"story":{"id":"story-1","title":"T","angle":"A"},'
        '"package":[{"id":"asset-1","format":"article","title":"T",'
        '"content":"Body","source_refs":["evidence-4"]}]}',
        tmp_path,
    )

    result = ContentWorkspace(fake).produce(
        source="Evidence-4 supports claim-1.",
        story={
            "id": "story-1",
            "title": "T",
            "angle": "A",
            "evidence": [
                {
                    "id": "evidence-4",
                    "quote": "Evidence supporting claim-1",
                    "location": "source",
                }
            ],
            "claims": [
                {
                    "id": "claim-1",
                    "text": "Claim 1",
                    "evidence_refs": ["evidence-4"],
                }
            ],
        },
        formats=["article"],
    )

    assert result["package"][0]["claim_refs"] == ["claim-1"]


def test_produce_rejects_claim_not_supported_by_asset_evidence(tmp_path):
    fake = FakeFactory(
        '{"story":{"id":"story-1","title":"T","angle":"A"},'
        '"package":[{"id":"asset-1","format":"article","title":"T",'
        '"content":"Body","source_refs":["evidence-4"],"claim_refs":["claim-1"]}]}',
        tmp_path,
    )

    try:
        ContentWorkspace(fake).produce(
            source="Evidence-4 supports another claim.",
            story={
                "id": "story-1",
                "title": "T",
                "angle": "A",
                "evidence": [
                    {"id": "evidence-4", "quote": "Other evidence", "location": "source"},
                    {"id": "evidence-5", "quote": "Claim evidence", "location": "source"},
                ],
                "claims": [
                    {
                        "id": "claim-1",
                        "text": "Claim 1",
                        "evidence_refs": ["evidence-5"],
                    }
                ],
            },
            formats=["article"],
        )
    except Exception as exc:
        assert "not supported by asset source_refs" in str(exc)
    else:
        raise AssertionError("unsupported claim provenance must fail closed")
