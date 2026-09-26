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
    Falsification test for the current product contract.

    Given a selected story grounded in evidence-4 and a claim claim-1,
    production should expose the relationship needed to answer:
    "which assets are affected if claim-1 changes?"

    The current workspace contract only exposes source_refs, so this test
    is expected to fail until claim-level provenance is actually persisted.
    """
    fake = FakeFactory(
        '{"story":{"id":"story-1","title":"T","angle":"A"},'
        '"package":[{"id":"asset-1","format":"article","title":"T",'
        '"content":"Body","source_refs":["evidence-4"]}]}',
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
            "claims":[{"id":"claim-1","text":"Claim 1"}],
        },
        formats=["article"],
    )

    asset = result["package"][0]
    assert asset["claim_refs"] == ["claim-1"]
