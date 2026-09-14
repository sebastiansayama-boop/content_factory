from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Protocol
from uuid import uuid4

from .artifacts import ArtifactStore
from .runtime_store import RuntimeStore


class RuntimeErrorBase(Exception):
    """Base error for deterministic factory failures."""


class InvalidTransition(RuntimeErrorBase):
    pass


class AuthorityDenied(RuntimeErrorBase):
    pass


class CapabilityNotFound(RuntimeErrorBase):
    pass


class ExecutionUnknown(RuntimeErrorBase):
    pass


class FactoryState(str, Enum):
    RECEIVED = "RECEIVED"
    ADMITTED = "ADMITTED"
    PRODUCED = "PRODUCED"
    VERIFIED = "VERIFIED"
    ACCEPTED = "ACCEPTED"
    RELEASE_READY = "RELEASE_READY"
    RELEASED = "RELEASED"
    DELIVERED = "DELIVERED"
    OBSERVED = "OBSERVED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True)
class WorkItem:
    work_item_id: str
    revision_id: str
    objective: str
    requested_outcome: str
    inputs: tuple[str, ...]
    knowledge_basis: tuple[str, ...]
    required_capabilities: tuple[str, ...]
    owner: str
    acceptance_criteria: tuple[str, ...]
    release_requirements: tuple[str, ...]
    constraints: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    success_signals: tuple[str, ...] = ()
    operation_id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(frozen=True)
class Capability:
    capability_id: str
    input_contract: Callable[[WorkItem], None]
    executor: Callable[[WorkItem, str], "ExecutionResult"]
    quality_requirements: tuple[str, ...] = ()
    authority_requirements: tuple[str, ...] = ()
    retryable: bool = False
    idempotent: bool = False


@dataclass(frozen=True)
class RuntimePolicy:
    max_execution_attempts: int = 1


@dataclass(frozen=True)
class ExecutionResult:
    execution_id: str
    capability_id: str
    output_revision_id: str
    payload: Any
    evidence_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class VerificationResult:
    output_revision_id: str
    passed: bool
    evidence_refs: tuple[str, ...] = ()
    reason: str = ""


@dataclass(frozen=True)
class AcceptanceDecision:
    output_revision_id: str
    accepted: bool
    authority: str
    reason: str = ""


@dataclass(frozen=True)
class PublicationResult:
    publication_id: str
    output_revision_id: str
    target: str
    externally_observable: bool
    evidence_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class Event:
    event_id: str
    timestamp: str
    work_item_id: str
    revision_id: str
    state: str
    operation: str
    actor: str
    data: dict[str, Any] = field(default_factory=dict)


class Publisher(Protocol):
    def publish(
        self,
        work_item: WorkItem,
        execution: ExecutionResult,
        publication_id: str | None = None,
    ) -> PublicationResult:
        ...


class FactoryRuntime:
    """Durable control kernel for one bounded work item.

    RuntimeStore is the recovery source for control state, execution/decision
    projections, attempts, and the append-only event journal. ArtifactStore is
    a separate evidence projection. External publication is an explicit
    idempotency boundary: a stable publication_id is reserved before delivery.
    """

    _allowed = {
        FactoryState.RECEIVED: {FactoryState.ADMITTED, FactoryState.FAILED, FactoryState.CANCELLED},
        FactoryState.ADMITTED: {FactoryState.PRODUCED, FactoryState.FAILED, FactoryState.UNKNOWN, FactoryState.CANCELLED},
        FactoryState.PRODUCED: {FactoryState.VERIFIED, FactoryState.FAILED, FactoryState.CANCELLED},
        FactoryState.VERIFIED: {FactoryState.ACCEPTED, FactoryState.FAILED, FactoryState.CANCELLED},
        FactoryState.ACCEPTED: {FactoryState.RELEASE_READY, FactoryState.FAILED, FactoryState.CANCELLED},
        FactoryState.RELEASE_READY: {FactoryState.RELEASED, FactoryState.FAILED, FactoryState.CANCELLED},
        FactoryState.RELEASED: {FactoryState.DELIVERED, FactoryState.FAILED},
        FactoryState.DELIVERED: {FactoryState.OBSERVED, FactoryState.FAILED},
        FactoryState.OBSERVED: set(),
        FactoryState.FAILED: set(),
        FactoryState.UNKNOWN: set(),
        FactoryState.CANCELLED: set(),
    }

    def __init__(
        self,
        publisher: Publisher | None = None,
        artifact_store: ArtifactStore | None = None,
        runtime_store: RuntimeStore | None = None,
        policy: RuntimePolicy | None = None,
    ) -> None:
        self.publisher = publisher
        self.artifact_store = artifact_store
        self.runtime_store = runtime_store
        self.policy = policy or RuntimePolicy()
        if self.policy.max_execution_attempts < 1:
            raise ValueError("max_execution_attempts must be >= 1")
        self.capabilities: dict[str, Capability] = {}
        self.states: dict[str, FactoryState] = {}
        self.operation_ids: dict[str, str] = {}
        self.events: list[Event] = []
        self.executions: dict[str, ExecutionResult] = {}
        self.verifications: dict[str, VerificationResult] = {}
        self.acceptances: dict[str, AcceptanceDecision] = {}
        self.publications: dict[str, PublicationResult] = {}
        self.attempts: dict[str, list[dict[str, Any]]] = {}
        self._recover()

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _jsonable(value: Any) -> Any:
        try:
            json.dumps(value)
        except TypeError as exc:
            raise ValueError(f"runtime payload is not JSON-serializable: {exc}") from exc
        return value

    def _recover(self) -> None:
        if self.runtime_store is None:
            return
        restarted_at = self._now()
        self.runtime_store.mark_running_attempts_unknown(restarted_at)
        for item in self.runtime_store.load_work_items():
            self.states[item.work_item_id] = FactoryState(item.state)
            self.operation_ids[item.work_item_id] = item.operation_id
        self.events = [Event(**event) for event in self.runtime_store.load_events()]
        for work_item_id in list(self.states):
            attempts = self.runtime_store.load_attempts(work_item_id)
            self.attempts[work_item_id] = attempts
            execution = self.runtime_store.load_record(work_item_id, "execution")
            if execution:
                self.executions[work_item_id] = ExecutionResult(**execution)
            verification = self.runtime_store.load_record(work_item_id, "verification")
            if verification:
                self.verifications[work_item_id] = VerificationResult(**verification)
            acceptance = self.runtime_store.load_record(work_item_id, "acceptance")
            if acceptance:
                self.acceptances[work_item_id] = AcceptanceDecision(**acceptance)
            publication = self.runtime_store.load_record(work_item_id, "publication")
            if publication:
                self.publications[work_item_id] = PublicationResult(**publication)
            if self.states[work_item_id] == FactoryState.ADMITTED and any(
                attempt["status"] == "UNKNOWN" for attempt in attempts
            ) and work_item_id not in self.executions:
                persisted = next(item for item in self.runtime_store.load_work_items() if item.work_item_id == work_item_id)
                event = Event(
                    event_id=str(uuid4()),
                    timestamp=restarted_at,
                    work_item_id=work_item_id,
                    revision_id=persisted.revision_id,
                    state=FactoryState.UNKNOWN.value,
                    operation="recover_unknown",
                    actor="recovery",
                    data={"operation_id": persisted.operation_id},
                )
                self.runtime_store.transition(
                    work_item_id=work_item_id,
                    operation_id=persisted.operation_id,
                    revision_id=persisted.revision_id,
                    state=FactoryState.UNKNOWN.value,
                    updated_at=restarted_at,
                    event=event.__dict__,
                )
                self.states[work_item_id] = FactoryState.UNKNOWN
                self.events.append(event)

    def register_capability(self, capability: Capability) -> None:
        if capability.capability_id in self.capabilities:
            raise ValueError(f"capability already registered: {capability.capability_id}")
        self.capabilities[capability.capability_id] = capability

    def submit(self, work_item: WorkItem, actor: str = "factory") -> None:
        if work_item.work_item_id in self.states:
            raise ValueError(f"work item already exists: {work_item.work_item_id}")
        if not work_item.required_capabilities:
            raise ValueError("work item requires at least one capability")
        event = self._new_event(work_item, FactoryState.RECEIVED, "submit", actor, operation_id=work_item.operation_id)
        if self.runtime_store is not None:
            self.runtime_store.create_work_item(
                work_item_id=work_item.work_item_id,
                operation_id=work_item.operation_id,
                revision_id=work_item.revision_id,
                state=FactoryState.RECEIVED.value,
                updated_at=event.timestamp,
                event=event.__dict__,
            )
        self.operation_ids[work_item.work_item_id] = work_item.operation_id
        self.states[work_item.work_item_id] = FactoryState.RECEIVED
        self.events.append(event)
        self._materialize(work_item)

    def run(
        self,
        work_item: WorkItem,
        *,
        verification: Callable[[WorkItem, ExecutionResult], VerificationResult],
        acceptance: Callable[[WorkItem, VerificationResult], AcceptanceDecision],
        release_authority: str | None = None,
        actor: str = "factory",
    ) -> PublicationResult | None:
        self._require_known_operation(work_item)
        state = self.states.get(work_item.work_item_id)
        if state is None:
            raise InvalidTransition("work item has not been submitted")
        if state in {FactoryState.OBSERVED, FactoryState.CANCELLED, FactoryState.FAILED, FactoryState.UNKNOWN}:
            if state == FactoryState.OBSERVED:
                return self.publications.get(work_item.work_item_id)
            raise InvalidTransition(f"cannot run from terminal state {state.value}")

        if state == FactoryState.RECEIVED:
            self._transition(work_item, FactoryState.ADMITTED, "admit", actor)

        capability_id = work_item.required_capabilities[0]
        capability = self.capabilities.get(capability_id)
        if capability is None:
            return self._fail(work_item, f"capability not registered: {capability_id}")

        try:
            if work_item.work_item_id not in self.executions:
                if not capability.idempotent and self._has_unknown_attempt(work_item.work_item_id):
                    raise ExecutionUnknown("prior execution attempt is UNKNOWN; explicit recovery resolution required")
                execution = self._execute_with_attempts(work_item, capability)
                if execution is None:
                    return None
                self.executions[work_item.work_item_id] = execution
                self._save_execution(work_item, execution)
                self._transition(
                    work_item,
                    FactoryState.PRODUCED,
                    "execute",
                    actor,
                    execution_id=execution.execution_id,
                    operation_id=work_item.operation_id,
                )

            if work_item.work_item_id not in self.verifications:
                verified = verification(work_item, self.executions[work_item.work_item_id])
                execution = self.executions[work_item.work_item_id]
                if verified.output_revision_id != execution.output_revision_id:
                    raise ValueError("verification must bind to exact output revision")
                self.verifications[work_item.work_item_id] = verified
                self._save_verification(work_item, verified)
                if not verified.passed:
                    return self._fail(work_item, "verification failed")
                self._transition(work_item, FactoryState.VERIFIED, "verify", actor)

            if work_item.work_item_id not in self.acceptances:
                decision = acceptance(work_item, self.verifications[work_item.work_item_id])
                execution = self.executions[work_item.work_item_id]
                if decision.output_revision_id != execution.output_revision_id:
                    raise ValueError("acceptance must bind to exact output revision")
                self.acceptances[work_item.work_item_id] = decision
                self._save_acceptance(work_item, decision)
                if not decision.accepted or not decision.authority:
                    return self._fail(work_item, "acceptance denied or missing authority")
                self._transition(work_item, FactoryState.ACCEPTED, "accept", decision.authority)

            if release_authority is None:
                raise AuthorityDenied("release authority is required")
            if self.states[work_item.work_item_id] == FactoryState.ACCEPTED:
                self._transition(work_item, FactoryState.RELEASE_READY, "release_ready", release_authority)
                self._transition(work_item, FactoryState.RELEASED, "release", release_authority)

            if work_item.work_item_id not in self.publications:
                if self.publisher is None:
                    raise AuthorityDenied("no publisher configured; external effect is not implicit")
                reservation = self.runtime_store.reserve_publication_id(work_item.work_item_id, str(uuid4())) if self.runtime_store else str(uuid4())
                publication = self.publisher.publish(work_item, self.executions[work_item.work_item_id], reservation)
                if publication.publication_id != reservation:
                    raise ValueError("publisher must preserve the reserved publication_id")
                if publication.output_revision_id != self.executions[work_item.work_item_id].output_revision_id:
                    raise ValueError("publication must bind to exact output revision")
                self.publications[work_item.work_item_id] = publication
                self._save_publication(work_item, publication)
                self._transition(
                    work_item,
                    FactoryState.DELIVERED,
                    "deliver",
                    release_authority,
                    publication_id=publication.publication_id,
                )

            publication = self.publications[work_item.work_item_id]
            if publication.externally_observable and self.states[work_item.work_item_id] == FactoryState.DELIVERED:
                self._transition(work_item, FactoryState.OBSERVED, "observe", "observation")
            self._materialize(work_item)
            return publication
        except Exception as exc:
            return self._fail(work_item, str(exc))

    def cancel(self, work_item: WorkItem, actor: str = "factory", reason: str = "cancelled") -> None:
        state = self.states.get(work_item.work_item_id)
        if state is None:
            raise InvalidTransition("work item has not been submitted")
        if FactoryState.CANCELLED not in self._allowed[state]:
            raise InvalidTransition(f"cannot cancel from {state.value}")
        self._transition(work_item, FactoryState.CANCELLED, "cancel", actor, reason=reason)
        self._materialize(work_item)

    def resolve_unknown(self, work_item: WorkItem, *, retry: bool, actor: str = "operator") -> None:
        if self.states.get(work_item.work_item_id) != FactoryState.UNKNOWN:
            raise InvalidTransition("work item is not UNKNOWN")
        if retry:
            event = self._new_event(work_item, FactoryState.ADMITTED, "resolve_unknown_retry", actor, operation_id=work_item.operation_id)
            if self.runtime_store is not None:
                self.runtime_store.transition(
                    work_item_id=work_item.work_item_id,
                    operation_id=work_item.operation_id,
                    revision_id=work_item.revision_id,
                    state=FactoryState.ADMITTED.value,
                    updated_at=event.timestamp,
                    event=event.__dict__,
                )
            self.states[work_item.work_item_id] = FactoryState.ADMITTED
            self.events.append(event)
        else:
            self._transition(work_item, FactoryState.FAILED, "resolve_unknown_fail", actor)

    def provenance(self, work_item_id: str) -> list[Event]:
        return [event for event in self.events if event.work_item_id == work_item_id]

    def _execute_with_attempts(self, work_item: WorkItem, capability: Capability) -> ExecutionResult | None:
        attempts = self.attempts.setdefault(work_item.work_item_id, [])
        max_attempts = self.policy.max_execution_attempts if capability.retryable and capability.idempotent else 1
        if len(attempts) >= max_attempts:
            raise ExecutionUnknown("no safe execution attempts remain")
        while len(attempts) < max_attempts:
            attempt_no = len(attempts) + 1
            execution_id = str(uuid4())
            attempt_id = str(uuid4())
            started_at = self._now()
            record = {
                "attempt_id": attempt_id,
                "operation_id": work_item.operation_id,
                "execution_id": execution_id,
                "attempt_no": attempt_no,
                "status": "RUNNING",
                "started_at": started_at,
                "completed_at": None,
                "error": None,
            }
            attempts.append(record)
            if self.runtime_store is not None:
                self.runtime_store.start_attempt(
                    attempt_id=attempt_id,
                    work_item_id=work_item.work_item_id,
                    operation_id=work_item.operation_id,
                    execution_id=execution_id,
                    attempt_no=attempt_no,
                    started_at=started_at,
                )
            try:
                capability.input_contract(work_item)
                execution = capability.executor(work_item, execution_id)
                if execution.execution_id != execution_id:
                    raise ValueError("capability must preserve execution_id")
                if execution.output_revision_id == work_item.revision_id:
                    raise ValueError("output revision must differ from work item revision")
                self._jsonable(execution.payload)
                record.update(status="SUCCEEDED", completed_at=self._now())
                if self.runtime_store is not None:
                    self.runtime_store.finish_attempt(
                        attempt_id,
                        status="SUCCEEDED",
                        completed_at=record["completed_at"],
                    )
                return execution
            except Exception as exc:
                record.update(status="FAILED", completed_at=self._now(), error=str(exc))
                if self.runtime_store is not None:
                    self.runtime_store.finish_attempt(
                        attempt_id,
                        status="FAILED",
                        completed_at=record["completed_at"],
                        error=record["error"],
                    )
                if len(attempts) >= max_attempts:
                    raise
        return None

    def _has_unknown_attempt(self, work_item_id: str) -> bool:
        return any(attempt["status"] == "UNKNOWN" for attempt in self.attempts.get(work_item_id, []))

    def _require_known_operation(self, work_item: WorkItem) -> None:
        known = self.operation_ids.get(work_item.work_item_id)
        if known is None:
            raise InvalidTransition("work item operation identity is not known")
        if known != work_item.operation_id:
            raise InvalidTransition("operation_id does not match durable work item identity")

    def _save_execution(self, work_item: WorkItem, execution: ExecutionResult) -> None:
        if self.runtime_store is not None:
            self.runtime_store.save_record(
                work_item.work_item_id,
                "execution",
                {
                    "execution_id": execution.execution_id,
                    "capability_id": execution.capability_id,
                    "output_revision_id": execution.output_revision_id,
                    "payload": self._jsonable(execution.payload),
                    "evidence_refs": list(execution.evidence_refs),
                },
            )

    def _save_verification(self, work_item: WorkItem, verification: VerificationResult) -> None:
        if self.runtime_store is not None:
            self.runtime_store.save_record(
                work_item.work_item_id,
                "verification",
                {
                    "output_revision_id": verification.output_revision_id,
                    "passed": verification.passed,
                    "evidence_refs": list(verification.evidence_refs),
                    "reason": verification.reason,
                },
            )

    def _save_acceptance(self, work_item: WorkItem, decision: AcceptanceDecision) -> None:
        if self.runtime_store is not None:
            self.runtime_store.save_record(
                work_item.work_item_id,
                "acceptance",
                {
                    "output_revision_id": decision.output_revision_id,
                    "accepted": decision.accepted,
                    "authority": decision.authority,
                    "reason": decision.reason,
                },
            )

    def _save_publication(self, work_item: WorkItem, publication: PublicationResult) -> None:
        if self.runtime_store is not None:
            self.runtime_store.save_record(
                work_item.work_item_id,
                "publication",
                {
                    "publication_id": publication.publication_id,
                    "output_revision_id": publication.output_revision_id,
                    "target": publication.target,
                    "externally_observable": publication.externally_observable,
                    "evidence_refs": list(publication.evidence_refs),
                },
            )

    def _transition(
        self,
        work_item: WorkItem,
        target: FactoryState,
        operation: str,
        actor: str,
        **data: Any,
    ) -> None:
        current = self.states[work_item.work_item_id]
        if target not in self._allowed[current]:
            raise InvalidTransition(f"{current} -> {target} is not allowed")
        data.setdefault("operation_id", work_item.operation_id)
        event = self._new_event(work_item, target, operation, actor, **data)
        if self.runtime_store is not None:
            self.runtime_store.transition(
                work_item_id=work_item.work_item_id,
                operation_id=work_item.operation_id,
                revision_id=work_item.revision_id,
                state=target.value,
                updated_at=event.timestamp,
                event=event.__dict__,
            )
        self.states[work_item.work_item_id] = target
        self.events.append(event)

    def _new_event(
        self,
        work_item: WorkItem,
        state: FactoryState,
        operation: str,
        actor: str,
        **data: Any,
    ) -> Event:
        return Event(
            event_id=str(uuid4()),
            timestamp=self._now(),
            work_item_id=work_item.work_item_id,
            revision_id=work_item.revision_id,
            state=state.value,
            operation=operation,
            actor=actor,
            data=data,
        )

    def _fail(self, work_item: WorkItem, reason: str) -> None:
        current = self.states[work_item.work_item_id]
        if FactoryState.FAILED in self._allowed[current]:
            self._transition(work_item, FactoryState.FAILED, "fail", "factory", reason=reason)
        self._materialize(work_item)
        return None

    def _materialize(self, work_item: WorkItem) -> None:
        if self.artifact_store is not None:
            self.artifact_store.record(work_item, self)
