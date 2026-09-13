from content_factory.artifacts import ArtifactStore
from content_factory.runtime import (
    AcceptanceDecision,
    Capability,
    ExecutionResult,
    FactoryRuntime,
    FactoryState,
    PublicationResult,
    VerificationResult,
    WorkItem,
)


class FakePublisher:
    def publish(self, work_item, execution):
        return PublicationResult(
            publication_id="pub-1",
            output_revision_id=execution.output_revision_id,
            target="fake://external/channel/1",
            externally_observable=True,
            evidence_refs=("external-observation-1",),
        )


def make_work_item():
    return WorkItem(
        work_item_id="wi-1",
        revision_id="spec-r1",
        objective="produce bounded content",
        requested_outcome="one externally delivered content item",
        inputs=("input-1",),
        knowledge_basis=("knowledge-r1",),
        required_capabilities=("write",),
        owner="editorial",
        acceptance_criteria=("meets specification",),
        release_requirements=("explicit publication authority",),
    )


def make_runtime(artifact_store=None):
    runtime = FactoryRuntime(publisher=FakePublisher(), artifact_store=artifact_store)

    def validate(item):
        assert item.requested_outcome

    def execute(item, execution_id):
        return ExecutionResult(
            execution_id=execution_id,
            capability_id="write",
            output_revision_id="asset-r1",
            payload="content",
            evidence_refs=("execution-1",),
        )

    runtime.register_capability(Capability("write", validate, execute))
    return runtime


def run_success(runtime):
    item = make_work_item()
    runtime.submit(item, actor="owner")
    publication = runtime.run(
        item,
        verification=lambda _, execution: VerificationResult(
            output_revision_id=execution.output_revision_id,
            passed=True,
            evidence_refs=("verification-1",),
        ),
        acceptance=lambda _, verified: AcceptanceDecision(
            output_revision_id=verified.output_revision_id,
            accepted=True,
            authority="approver",
        ),
        release_authority="publisher",
    )
    return item, publication


def test_end_to_end_v0_reaches_observed():
    runtime = make_runtime()
    item, publication = run_success(runtime)

    assert publication is not None
    assert runtime.states[item.work_item_id] == FactoryState.OBSERVED
    assert [event.state for event in runtime.provenance(item.work_item_id)] == [
        "RECEIVED",
        "ADMITTED",
        "PRODUCED",
        "VERIFIED",
        "ACCEPTED",
        "RELEASE_READY",
        "RELEASED",
        "DELIVERED",
        "OBSERVED",
    ]


def test_execution_does_not_publish_without_publisher():
    runtime = make_runtime()
    runtime.publisher = None
    item = make_work_item()
    runtime.submit(item)

    publication = runtime.run(
        item,
        verification=lambda _, execution: VerificationResult(execution.output_revision_id, True),
        acceptance=lambda _, verified: AcceptanceDecision(verified.output_revision_id, True, "approver"),
        release_authority="publisher",
    )

    assert publication is None
    assert runtime.states[item.work_item_id] == FactoryState.FAILED


def test_verification_is_revision_bound():
    runtime = make_runtime()
    item = make_work_item()
    runtime.submit(item)

    publication = runtime.run(
        item,
        verification=lambda _, execution: VerificationResult("wrong-revision", True),
        acceptance=lambda _, verified: AcceptanceDecision(verified.output_revision_id, True, "approver"),
        release_authority="publisher",
    )

    assert publication is None
    assert runtime.states[item.work_item_id] == FactoryState.FAILED


def test_acceptance_requires_authority():
    runtime = make_runtime()
    item = make_work_item()
    runtime.submit(item)

    publication = runtime.run(
        item,
        verification=lambda _, execution: VerificationResult(execution.output_revision_id, True),
        acceptance=lambda _, verified: AcceptanceDecision(verified.output_revision_id, True, ""),
        release_authority="publisher",
    )

    assert publication is None
    assert runtime.states[item.work_item_id] == FactoryState.FAILED


def test_runtime_materializes_durable_artifacts(tmp_path):
    runtime = make_runtime(ArtifactStore(tmp_path))
    item, publication = run_success(runtime)

    assert publication is not None
    expected = {
        "01_observation/wi-1.json",
        "03_working_context/wi-1.json",
        "05_decision/wi-1.json",
        "06_production/wi-1.json",
        "07_verification/wi-1.json",
        "08_effects_feedback/wi-1.json",
        "10_records/wi-1.json",
    }
    actual = {
        path.relative_to(tmp_path).as_posix()
        for path in tmp_path.rglob("*.json")
    }
    assert actual == expected

    record = (tmp_path / "10_records/wi-1.json").read_text(encoding="utf-8")
    assert '"state": "OBSERVED"' in record
    assert '"operation": "deliver"' in record
