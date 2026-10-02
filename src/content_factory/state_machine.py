from __future__ import annotations

from typing import Mapping


class InvalidStateTransition(ValueError):
    """Raised when a state change violates a declared lifecycle."""


STATE_TRANSITIONS: Mapping[str, Mapping[str, frozenset[str]]] = {
    "command": {
        "CREATED": frozenset({"VALIDATED", "CANCELLED"}),
        "VALIDATED": frozenset({"DISPATCHED", "CANCELLED"}),
        "DISPATCHED": frozenset({"SUCCEEDED", "FAILED", "CANCELLED"}),
        "SUCCEEDED": frozenset(),
        "FAILED": frozenset(),
        "CANCELLED": frozenset(),
    },
    "execution": {
        "QUEUED": frozenset({"RUNNING", "CANCELLED"}),
        "RUNNING": frozenset({"WAITING_APPROVAL", "SUCCEEDED", "FAILED", "UNKNOWN", "CANCELLED"}),
        "WAITING_APPROVAL": frozenset({"RUNNING", "CANCELLED", "FAILED"}),
        "SUCCEEDED": frozenset(),
        "FAILED": frozenset(),
        "UNKNOWN": frozenset(),
        "CANCELLED": frozenset(),
    },
    "content_run": {
        "DRAFT": frozenset({"RESEARCHING", "RESEARCH_READY", "PLANNING", "FAILED"}),
        "RESEARCHING": frozenset({"RESEARCH_READY", "FAILED"}),
        "RESEARCH_READY": frozenset({"PLANNING", "FAILED"}),
        "PLANNING": frozenset({"RESEARCHING", "PRODUCING", "REVIEW", "FAILED"}),
        "PRODUCING": frozenset({"PRODUCING", "REVIEW", "FAILED"}),
        "REVIEW": frozenset({"PRODUCING", "APPROVED", "FAILED"}),
        "APPROVED": frozenset({"EXPORTED", "PUBLISHED"}),
        "EXPORTED": frozenset({"PUBLISHED"}),
        "FAILED": frozenset({"RESEARCHING", "RESEARCH_READY", "PLANNING", "PRODUCING"}),
        "PUBLISHED": frozenset(),
    },
    "approval": {
        "REQUESTED": frozenset({"APPROVED", "REJECTED", "EXPIRED", "CANCELLED"}),
        "APPROVED": frozenset(),
        "REJECTED": frozenset(),
        "EXPIRED": frozenset(),
        "CANCELLED": frozenset(),
    },
    "publication": {
        "PREPARED": frozenset({"PUBLISHING", "CANCELLED"}),
        "PUBLISHING": frozenset({"PUBLISHED", "FAILED", "UNKNOWN"}),
        "FAILED": frozenset(),
        "UNKNOWN": frozenset(),
        "PUBLISHED": frozenset(),
        "CANCELLED": frozenset(),
    },
}


TERMINAL_STATES: Mapping[str, frozenset[str]] = {
    entity: frozenset(states)
    for entity, states in {
        "command": {"SUCCEEDED", "FAILED", "CANCELLED"},
        "execution": {"SUCCEEDED", "FAILED", "UNKNOWN", "CANCELLED"},
        "content_run": {"PUBLISHED"},
        "approval": {"APPROVED", "REJECTED", "EXPIRED", "CANCELLED"},
        "publication": {"FAILED", "UNKNOWN", "PUBLISHED", "CANCELLED"},
    }.items()
}


def validate_transition(entity: str, current: str, target: str) -> None:
    """Validate one lifecycle transition; same-state writes are always allowed."""
    transitions = STATE_TRANSITIONS.get(entity)
    if transitions is None:
        raise InvalidStateTransition(f"unknown state entity: {entity}")
    if current == target:
        return
    allowed = transitions.get(current)
    if allowed is None:
        raise InvalidStateTransition(f"unknown {entity} state: {current}")
    if target not in allowed:
        raise InvalidStateTransition(
            f"{entity} cannot transition from {current} to {target}"
        )


def require_state(entity: str, current: str, *allowed: str) -> None:
    if current not in allowed:
        expected = ", ".join(allowed)
        raise InvalidStateTransition(
            f"{entity} requires state in {{{expected}}}; current state is {current}"
        )


def require_publication_parent(run_status: str, publication_status: str, target: str) -> None:
    """Cross-entity invariants for a publication owned by a ContentRun."""
    if target in {"PUBLISHING", "PUBLISHED"} and run_status not in {"APPROVED", "EXPORTED"}:
        raise InvalidStateTransition(
            f"publication cannot enter {target} while content run is {run_status}"
        )
    if target == "PUBLISHED" and publication_status != "PUBLISHING":
        raise InvalidStateTransition(
            f"publication cannot enter PUBLISHED from {publication_status}"
        )
    if target == "PUBLISHING" and publication_status != "PREPARED":
        raise InvalidStateTransition(
            f"publication cannot enter PUBLISHING from {publication_status}"
        )


def is_terminal(entity: str, state: str) -> bool:
    return state in TERMINAL_STATES.get(entity, frozenset())
