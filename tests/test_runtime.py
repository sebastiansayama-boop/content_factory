from content_factory.artifacts import ArtifactStore
from content_factory.runtime import (
    AcceptanceDecision,
    Capability,
    ExecutionResult,
    FactoryRuntime,
    FactoryState,
    PublicationResult,
    RuntimePolicy,
    VerificationResult,
    WorkItem,
)
from content_factory.runtime_store import RuntimeStore


class FakePublisher:
    def __init__(self):
        self.calls = []

    def publish(self, work_item, execution, publication_id=None):
        publication_id = publication_id or "pub-generated"
        self.calls.append(publication_id)
        return PublicationResult(
            publication_id=publication_id,
            output_revision_id=execution.output_revision_id,
            target="fake://external/channel/1",
            externally_observable=True,
            evidence_refs=("external-observation-1",),
        )


class SimulatedPublisher:
    def publish(self, work_item, execution, publication_id=None):
        return PublicationResult(
            publication_id=publication_id or "sim-1",
            output_revision_id=execution.output_revision_id,
            target="simulated://external/channel/1",
            externally_observable=False,
            evidence_refs=("simulation-1",),
        )


def make_work_item(work_item_id="wi-1", operation_id="op-1"):
    return WorkItem(
        work_item_id=work_item_id,
        operation_id=operation_id,
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


def make_runtime(artifact_store=None, publisher=None, runtime_store=None, *, retryable=False, idempotent=False, policy=None):
    runtime = FactoryRuntime(
        publisher=publisher or FakePublisher(),
        artifact_store=artifact_store,
        runtime_store=runtime_store,
        policy=policy,
    )

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

    runtime.register_capability(
        Capability("write", validate, execute, retryable=retryable, idempotent=idempotent)
    )
    return runtime


def run_success(runtime, item=None):
    item = item or make_work_item()
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
    assert runtime.operation_ids[item.work_item_id] == "op-1"
    assert [event.state for event in runtime.provenance(item.work_item_id)] == [
        "RECEIVED", "ADMITTED", "PRODUCED", "VERIFIED", "ACCEPTED",
        "RELEASE_READY", "RELEASED", "DELIVERED", "OBSERVED",
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


def test_runtime_materializes_operation_and_attempts(tmp_path):
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
    actual = {path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*.json")}
    assert actual == expected

    context = (tmp_path / "03_working_context/wi-1.json").read_text(encoding="utf-8")
    assert '"operation_id": "op-1"' in context

    record = (tmp_path / "10_records/wi-1.json").read_text(encoding="utf-8")
    assert '"state": "OBSERVED"' in record
    assert '"operation": "deliver"' in record
    assert '"attempts"' in record


def test_simulated_publication_does_not_create_observation(tmp_path):
    runtime = make_runtime(ArtifactStore(tmp_path), publisher=SimulatedPublisher())
    item, publication = run_success(runtime)

    assert publication is not None
    assert runtime.states[item.work_item_id] == FactoryState.DELIVERED
    assert not (tmp_path / "01_observation/wi-1.json").exists()


def test_runtime_state_and_full_execution_projection_survive_restart(tmp_path):
    database = tmp_path / "runtime.sqlite3"
    item = make_work_item("wi-restart", "op-restart")

    with RuntimeStore(database) as store:
        first = make_runtime(runtime_store=store)
        publication = run_success(first, item)[1]
        assert publication is not None

    with RuntimeStore(database) as store:
        recovered = make_runtime(runtime_store=store)
        assert recovered.states[item.work_item_id] == FactoryState.OBSERVED
        assert recovered.operation_ids[item.work_item_id] == "op-restart"
        assert recovered.executions[item.work_item_id].execution_id
        assert recovered.verifications[item.work_item_id].passed is True
        assert recovered.acceptances[item.work_item_id].accepted is True
        assert recovered.publications[item.work_item_id].publication_id == publication.publication_id
        assert recovered.attempts[item.work_item_id][0]["status"] == "SUCCEEDED"


def test_duplicate_operation_identity_is_rejected():
    runtime = make_runtime()
    item = make_work_item("wi-identity", "op-identity")
    runtime.submit(item)

    conflicting = make_work_item("wi-identity", "op-other")
    try:
        runtime.submit(conflicting)
    except ValueError as exc:
        assert "already exists" in str(exc)
    else:
        raise AssertionError("duplicate work item was accepted")


def test_idempotent_retry_uses_distinct_execution_ids():
    calls = []

    def execute(item, execution_id):
        calls.append(execution_id)
        if len(calls) == 1:
            raise RuntimeError("transient")
        return ExecutionResult(execution_id, "write", "asset-r2", "content", ())

    runtime = FactoryRuntime(policy=RuntimePolicy(max_execution_attempts=2))
    runtime.register_capability(Capability("write", lambda _: None, execute, retryable=True, idempotent=True))
    item = make_work_item("wi-retry", "op-retry")
    runtime.submit(item)
    runtime.run(
        item,
        verification=lambda _, execution: VerificationResult(execution.output_revision_id, True),
        acceptance=lambda _, verified: AcceptanceDecision(verified.output_revision_id, True, "approver"),
        release_authority="publisher",
    )

    assert len(calls) == 2
    assert calls[0] != calls[1]
    assert [attempt["status"] for attempt in runtime.attempts[item.work_item_id]] == ["FAILED", "SUCCEEDED"]


def test_non_idempotent_unknown_blocks_automatic_reexecution(tmp_path):
    database = tmp_path / "runtime.sqlite3"
    item = make_work_item("wi-unknown", "op-unknown")

    with RuntimeStore(database) as store:
        runtime = make_runtime(runtime_store=store)
        runtime.submit(item)
        runtime._transition(item, FactoryState.ADMITTED, "admit", "factory")
        store.start_attempt(
            attempt_id="attempt-1",
            work_item_id=item.work_item_id,
            operation_id=item.operation_id,
            execution_id="exec-1",
            attempt_no=1,
            started_at="2026-09-14T00:00:00+00:00",
        )

    with RuntimeStore(database) as store:
        recovered = make_runtime(runtime_store=store)
        assert recovered.states[item.work_item_id] == FactoryState.UNKNOWN
        try:
            recovered.run(
                item,
                verification=lambda _, execution: VerificationResult(execution.output_revision_id, True),
                acceptance=lambda _, verified: AcceptanceDecision(verified.output_revision_id, True, "approver"),
                release_authority="publisher",
            )
        except Exception:
            pass
        else:
            raise AssertionError("UNKNOWN execution was automatically re-run")


def test_cancel_is_durable(tmp_path):
    database = tmp_path / "runtime.sqlite3"
    item = make_work_item("wi-cancel", "op-cancel")

    with RuntimeStore(database) as store:
        runtime = make_runtime(runtime_store=store)
        runtime.submit(item)
        runtime.cancel(item, actor="operator", reason="operator requested stop")
        assert runtime.states[item.work_item_id] == FactoryState.CANCELLED

    with RuntimeStore(database) as store:
        recovered = FactoryRuntime(runtime_store=store)
        assert recovered.states[item.work_item_id] == FactoryState.CANCELLED
