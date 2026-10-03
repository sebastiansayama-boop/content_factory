from enum import StrEnum
from dataclasses import dataclass

class Role(StrEnum):
    OPERATOR = "OPERATOR"
    EDITOR = "EDITOR"
    QC = "QC"
    PUBLISHER = "PUBLISHER"

class Mode(StrEnum):
    PERSONAL = "PERSONAL"
    STRICT_SOD = "STRICT_SOD"

class Action(StrEnum):
    CREATE = "CREATE"
    EXECUTE = "EXECUTE"
    EDIT = "EDIT"
    REGENERATE = "REGENERATE"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    PUBLISH = "PUBLISH"
    EXPORT = "EXPORT"
    INSPECT = "INSPECT"

ROLE_CAPABILITIES = {
    Role.OPERATOR: frozenset({Action.CREATE, Action.EXECUTE, Action.INSPECT}),
    Role.EDITOR: frozenset({Action.EDIT, Action.REGENERATE, Action.INSPECT}),
    Role.QC: frozenset({Action.APPROVE, Action.REJECT, Action.REGENERATE, Action.INSPECT}),
    Role.PUBLISHER: frozenset({Action.PUBLISH, Action.EXPORT, Action.INSPECT}),
}

class AuthorizationError(ValueError):
    pass

@dataclass(frozen=True)
class ActorContext:
    actor_id: str
    roles: frozenset[Role]
    mode: Mode = Mode.PERSONAL

@dataclass(frozen=True)
class ArtifactContext:
    artifact_version: str
    approved_version: str | None = None
    qc_status: str | None = None
    approval_status: str | None = None
    creator_id: str | None = None
    editor_id: str | None = None
    approver_id: str | None = None
    publisher_id: str | None = None

@dataclass(frozen=True)
class ActionContext:
    action: Action
    run_status: str
    artifact: ArtifactContext | None = None

class CapabilityPolicy:
    def authorize(self, actor: ActorContext, context: ActionContext) -> None:
        if not actor.actor_id.strip():
            raise AuthorizationError("actor_id is required")
        if not any(context.action in ROLE_CAPABILITIES.get(role, frozenset()) for role in actor.roles):
            raise AuthorizationError(f"actor is not authorized for {context.action.value}")
        allowed = {
            Action.CREATE: {"DRAFT", "CREATED"},
            Action.EXECUTE: {"DRAFT", "PLANNING", "FAILED", "RESEARCH_READY"},
            Action.EDIT: {"REVIEW", "APPROVED", "EXPORTED"},
            Action.REGENERATE: {"REVIEW", "APPROVED", "EXPORTED"},
            Action.APPROVE: {"REVIEW"},
            Action.REJECT: {"REVIEW"},
            Action.PUBLISH: {"APPROVED", "EXPORTED"},
            Action.EXPORT: {"APPROVED"},
            Action.INSPECT: None,
        }[context.action]
        if allowed is not None and context.run_status not in allowed:
            raise AuthorizationError(f"{context.action.value} requires state {sorted(allowed)}")
        if context.action in {Action.EDIT, Action.REGENERATE}:
            self._check_mutation(context)
        if context.action in {Action.APPROVE, Action.PUBLISH}:
            self._check_release_gate(actor, context)

    def _check_mutation(self, context: ActionContext) -> None:
        artifact = context.artifact
        if artifact is None:
            raise AuthorizationError("artifact context is required for mutation")
        if (
            context.run_status in {"APPROVED", "EXPORTED"}
            and artifact.approved_version == artifact.artifact_version
        ):
            raise AuthorizationError(
                "mutation of an approved version requires creating a new artifact version"
            )

    def _check_release_gate(self, actor: ActorContext, context: ActionContext) -> None:
        artifact = context.artifact
        if artifact is None:
            raise AuthorizationError("artifact context is required")
        if artifact.qc_status != "PASSED":
            raise AuthorizationError("release requires QC status PASSED")
        if context.action == Action.APPROVE:
            if artifact.approval_status == "APPROVED":
                raise AuthorizationError("artifact is already approved")
            if artifact.approved_version == artifact.artifact_version:
                raise AuthorizationError("artifact version is already approved")
            if actor.mode == Mode.STRICT_SOD and actor.actor_id in {artifact.creator_id, artifact.editor_id}:
                raise AuthorizationError("strict SoD forbids creator/editor from approving")
        else:
            if artifact.approval_status != "APPROVED":
                raise AuthorizationError("publication requires approval")
            if artifact.approved_version != artifact.artifact_version:
                raise AuthorizationError("publication requires the approved artifact version")
            if actor.mode == Mode.STRICT_SOD and actor.actor_id in {
                artifact.creator_id, artifact.editor_id, artifact.approver_id
            }:
                raise AuthorizationError("strict SoD forbids creator/editor/approver from publishing")

def role_matrix() -> dict[str, dict[str, bool]]:
    return {
        role.value: {action.value: action in ROLE_CAPABILITIES[role] for action in Action}
        for role in Role
    }
