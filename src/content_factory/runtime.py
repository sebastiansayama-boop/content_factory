from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Protocol
from uuid import uuid4

from .artifacts import ArtifactStore


class RuntimeErrorBase(Exception):
    """Base error for deterministic factory failures."""


class InvalidTransition(RuntimeErrorBase):
    pass


class AuthorityDenied(RuntimeErrorBase):
    pass


class CapabilityNotFound(RuntimeErrorBase):
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


@dataclass(frozen=True)
class Capability:
    capability_id: str
    input_contract: Callable[[WorkItem], None]
    executor: Callable[[WorkItem, str], "ExecutionResult"]
    quality_requirements: tuple[str, ...] = ()
    authority_requirements: tuple[str, ...] = ()


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
    def publish(self, work_item: WorkItem, execution: ExecutionResult) -> PublicationResult:
        ...


class FactoryRuntime:
    """Small deterministic orchestration kernel for one bounded work item.

    v0 keeps execution state in memory, while an explicit ArtifactStore can
    materialize the resulting evidence into durable repository artifacts.
    External publication is injected and therefore never implied by execution.
    """

    _allowed = {
        FactoryState.RECEIVED: {FactoryState.ADMITTED, FactoryState.FAILED},
        FactoryState.ADMITTED: {FactoryState.PRODUCED, FactoryState.FAILED},
        FactoryState.PRODUCED: {FactoryState.VERIFIED, FactoryState.FAILED},
        FactoryState.VERIFIED: {FactoryState.ACCEPTED, FactoryState.FAILED},
        FactoryState.ACCEPTED: {FactoryState.RELEASE_READY, FactoryState.FAILED},
        FactoryState.RELEASE_READY: {FactoryState.RELEASED, FactoryState.FAILED},
        FactoryState.RELEASED: {FactoryState.DELIVERED, FactoryState.FAILED},
        FactoryState.DELIVERED: {FactoryState.OBSERVED, FactoryState.FAILED},
        FactoryState.OBSERVED: set(),
        FactoryState.FAILED: set(),
    }

    def __init__(self, publisher: Publisher | None = None, artifact_store: ArtifactStore | None = None) -> None:
        self.publisher = publisher
        self.artifact_store = artifact_store
        self.capabilities: dict[str, Capability] = {}
        self.states: dict[str, FactoryState] = {}
        self.events: list[Event] = []
        self.executions: dict[str, ExecutionResult] = {}
        self.verifications: dict[str, VerificationResult] = {}
        self.acceptances: dict[str, AcceptanceDecision] = {}
        self.publications: dict[str, PublicationResult] = {}

    def register_capability(self, capability: Capability) -> None:
        if capability.capability_id in self.capabilities:
            raise ValueError(f"capability already registered: {capability.capability_id}")
        self.capabilities[capability.capability_id] = capability

    def submit(self, work_item: WorkItem, actor: str = "factory") -> None:
        if work_item.work_item_id in self.states:
            raise ValueError(f"work item already exists: {work_item.work_item_id}")
        if not work_item.required_capabilities:
            raise ValueError("work item requires at least one capability")
        self.states[work_item.work_item_id] = FactoryState.RECEIVED
        self._record(work_item, FactoryState.RECEIVED, "submit", actor)
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
        self._require_state(work_item, FactoryState.RECEIVED)
        self._transition(work_item, FactoryState.ADMITTED, "admit", actor)

        capability_id = work_item.required_capabilities[0]
        capability = self.capabilities.get(capability_id)
        if capability is None:
            return self._fail(work_item, f"capability not registered: {capability_id}")

        try:
            capability.input_contract(work_item)
            execution = capability.executor(work_item, str(uuid4()))
            if execution.output_revision_id == work_item.revision_id:
                raise ValueError("output revision must differ from work item revision")
            self.executions[work_item.work_item_id] = execution
            self._transition(work_item, FactoryState.PRODUCED, "execute", actor, execution_id=execution.execution_id)

            verified = verification(work_item, execution)
            if verified.output_revision_id != execution.output_revision_id:
                raise ValueError("verification must bind to exact output revision")
            self.verifications[work_item.work_item_id] = verified
            if not verified.passed:
                return self._fail(work_item, "verification failed")
            self._transition(work_item, FactoryState.VERIFIED, "verify", actor)

            decision = acceptance(work_item, verified)
            if decision.output_revision_id != execution.output_revision_id:
                raise ValueError("acceptance must bind to exact output revision")
            self.acceptances[work_item.work_item_id] = decision
            if not decision.accepted or not decision.authority:
                return self._fail(work_item, "acceptance denied or missing authority")
            self._transition(work_item, FactoryState.ACCEPTED, "accept", decision.authority)

            if release_authority is None:
                raise AuthorityDenied("release authority is required")
            self._transition(work_item, FactoryState.RELEASE_READY, "release_ready", release_authority)
            self._transition(work_item, FactoryState.RELEASED, "release", release_authority)

            if self.publisher is None:
                raise AuthorityDenied("no publisher configured; external effect is not implicit")
            publication = self.publisher.publish(work_item, execution)
            self.publications[work_item.work_item_id] = publication
            if publication.output_revision_id != execution.output_revision_id:
                raise ValueError("publication must bind to exact output revision")
            self._transition(work_item, FactoryState.DELIVERED, "deliver", release_authority, publication_id=publication.publication_id)

            if publication.externally_observable:
                self._transition(work_item, FactoryState.OBSERVED, "observe", "observation")
            self._materialize(work_item)
            return publication
        except Exception as exc:
            return self._fail(work_item, str(exc))

    def provenance(self, work_item_id: str) -> list[Event]:
        return [event for event in self.events if event.work_item_id == work_item_id]

    def _require_state(self, work_item: WorkItem, expected: FactoryState) -> None:
        actual = self.states.get(work_item.work_item_id)
        if actual != expected:
            raise InvalidTransition(f"expected {expected}, got {actual}")

    def _transition(self, work_item: WorkItem, target: FactoryState, operation: str, actor: str, **data: Any) -> None:
        current = self.states[work_item.work_item_id]
        if target not in self._allowed[current]:
            raise InvalidTransition(f"{current} -> {target} is not allowed")
        self.states[work_item.work_item_id] = target
        self._record(work_item, target, operation, actor, **data)

    def _fail(self, work_item: WorkItem, reason: str) -> None:
        current = self.states[work_item.work_item_id]
        if FactoryState.FAILED in self._allowed[current]:
            self._transition(work_item, FactoryState.FAILED, "fail", "factory", reason=reason)
        self._materialize(work_item)
        return None

    def _materialize(self, work_item: WorkItem) -> None:
        if self.artifact_store is not None:
            self.artifact_store.record(work_item, self)

    def _record(self, work_item: WorkItem, state: FactoryState, operation: str, actor: str, **data: Any) -> None:
        self.events.append(
            Event(
                event_id=str(uuid4()),
                timestamp=datetime.now(timezone.utc).isoformat(),
                work_item_id=work_item.work_item_id,
                revision_id=work_item.revision_id,
                state=state.value,
                operation=operation,
                actor=actor,
                data=data,
            )
        )
