import pytest

from content_factory.access_policy import (
    Action,
    ActionContext,
    ActorContext,
    ArtifactContext,
    AuthorizationError,
    CapabilityPolicy,
    Mode,
    ROLE_CAPABILITIES,
    Role,
)


ALL_STATES = (
    "DRAFT",
    "RESEARCHING",
    "RESEARCH_READY",
    "PLANNING",
    "PRODUCING",
    "REVIEW",
    "APPROVED",
    "EXPORTED",
    "PUBLISHED",
    "FAILED",
)


def actor(*roles, mode=Mode.PERSONAL, actor_id="actor-1"):
    return ActorContext(actor_id, frozenset(roles), mode)


def artifact(**kwargs):
    return ArtifactContext("v2", **kwargs) if "artifact_version" not in kwargs else ArtifactContext(**kwargs)


def context_for(action, state):
    if action == Action.CREATE:
        return ActionContext(action, state)
    if action in {Action.EDIT, Action.REGENERATE}:
        return ActionContext(action, state, artifact())
    if action == Action.APPROVE:
        return ActionContext(action, state, artifact(qc_status="PASSED"))
    if action == Action.REJECT:
        return ActionContext(action, state, artifact())
    if action == Action.PUBLISH:
        return ActionContext(
            action,
            state,
            artifact(qc_status="PASSED", approval_status="APPROVED", approved_version="v2"),
        )
    if action == Action.EXPORT:
        return ActionContext(action, state)
    return ActionContext(action, state)


policy = CapabilityPolicy()


@pytest.mark.parametrize("role", list(Role))
@pytest.mark.parametrize(
    "action",
    [Action.CREATE, Action.EDIT, Action.APPROVE, Action.PUBLISH],
)
def test_core_role_action_matrix(role, action):
    allowed = action in ROLE_CAPABILITIES[role]
    state = {
        Action.CREATE: "DRAFT",
        Action.EDIT: "REVIEW",
        Action.APPROVE: "REVIEW",
        Action.PUBLISH: "APPROVED",
    }[action]
    context = context_for(action, state)

    if allowed:
        policy.authorize(actor(role), context)
    else:
        with pytest.raises(AuthorizationError):
            policy.authorize(actor(role), context)


@pytest.mark.parametrize("action", list(Action))
def test_each_action_has_explicit_capability_owner(action):
    owners = [role for role in Role if action in ROLE_CAPABILITIES[role]]
    if action == Action.INSPECT:
        assert set(owners) == set(Role)
    elif action == Action.REGENERATE:
        assert set(owners) == {Role.EDITOR, Role.QC}
    else:
        assert len(owners) == 1


@pytest.mark.parametrize("state", ALL_STATES)
@pytest.mark.parametrize(
    ("action", "allowed_states"),
    [
        (Action.CREATE, {"DRAFT", "CREATED"}),
        (Action.EDIT, {"REVIEW", "APPROVED", "EXPORTED"}),
        (Action.APPROVE, {"REVIEW"}),
        (Action.PUBLISH, {"APPROVED", "EXPORTED"}),
    ],
)
def test_core_action_state_matrix(action, allowed_states, state):
    roles = {
        Action.CREATE: Role.OPERATOR,
        Action.EDIT: Role.EDITOR,
        Action.APPROVE: Role.QC,
        Action.PUBLISH: Role.PUBLISHER,
    }
    context = context_for(action, state)

    if state in allowed_states:
        try:
            policy.authorize(actor(roles[action]), context)
        except AuthorizationError:
            pytest.fail(f"{action} unexpectedly denied in state {state}")
    else:
        with pytest.raises(AuthorizationError):
            policy.authorize(actor(roles[action]), context)


@pytest.mark.parametrize("qc_status", [None, "FAILED", "UNKNOWN", "PASSED"])
def test_approve_qc_gate(qc_status):
    context = ActionContext(
        Action.APPROVE,
        "REVIEW",
        artifact(qc_status=qc_status),
    )
    if qc_status == "PASSED":
        policy.authorize(actor(Role.QC), context)
    else:
        with pytest.raises(AuthorizationError, match="QC status PASSED"):
            policy.authorize(actor(Role.QC), context)


@pytest.mark.parametrize(
    ("current_version", "approved_version", "approval_status", "expected"),
    [
        ("v2", "v2", "APPROVED", True),
        ("v2", "v1", "APPROVED", False),
        ("v2", None, None, False),
        ("v2", "v2", "REJECTED", False),
    ],
)
def test_publish_version_and_approval_matrix(
    current_version, approved_version, approval_status, expected
):
    context = ActionContext(
        Action.PUBLISH,
        "APPROVED",
        ArtifactContext(
            artifact_version=current_version,
            approved_version=approved_version,
            qc_status="PASSED",
            approval_status=approval_status,
        ),
    )

    if expected:
        policy.authorize(actor(Role.PUBLISHER), context)
    else:
        with pytest.raises(AuthorizationError):
            policy.authorize(actor(Role.PUBLISHER), context)


def test_editing_approved_version_must_create_new_version():
    with pytest.raises(AuthorizationError, match="new artifact version"):
        policy.authorize(
            actor(Role.EDITOR),
            ActionContext(
                Action.EDIT,
                "APPROVED",
                artifact(approved_version="v2"),
            ),
        )


def test_editing_approved_run_as_new_version_is_allowed():
    policy.authorize(
        actor(Role.EDITOR),
        ActionContext(
            Action.EDIT,
            "APPROVED",
            artifact(artifact_version="v3", approved_version="v2"),
        ),
    )


def test_personal_mode_allows_one_actor_to_cross_all_four_gates():
    same_actor = actor(
        Role.OPERATOR,
        Role.EDITOR,
        Role.QC,
        Role.PUBLISHER,
        actor_id="owner",
    )

    policy.authorize(same_actor, ActionContext(Action.CREATE, "DRAFT"))
    policy.authorize(same_actor, ActionContext(
        Action.EDIT, "REVIEW", artifact=artifact()
    ))
    policy.authorize(same_actor, ActionContext(
        Action.APPROVE, "REVIEW", artifact=artifact(qc_status="PASSED")
    ))
    policy.authorize(same_actor, ActionContext(
        Action.PUBLISH,
        "APPROVED",
        artifact=artifact(
            qc_status="PASSED",
            approval_status="APPROVED",
            approved_version="v2",
        ),
    ))


@pytest.mark.parametrize(
    ("action", "role"),
    [
        (Action.CREATE, Role.EDITOR),
        (Action.EDIT, Role.OPERATOR),
        (Action.APPROVE, Role.EDITOR),
        (Action.PUBLISH, Role.QC),
    ],
)
def test_core_cross_role_actions_are_denied(action, role):
    state = {
        Action.CREATE: "DRAFT",
        Action.EDIT: "REVIEW",
        Action.APPROVE: "REVIEW",
        Action.PUBLISH: "APPROVED",
    }[action]
    with pytest.raises(AuthorizationError):
        policy.authorize(actor(role), context_for(action, state))


@pytest.mark.parametrize(
    "role",
    [Role.OPERATOR, Role.EDITOR, Role.QC, Role.PUBLISHER],
)
def test_personal_role_union_does_not_remove_state_gates(role):
    same_actor = actor(Role.OPERATOR, Role.EDITOR, Role.QC, Role.PUBLISHER)

    invalid_context = {
        Role.OPERATOR: ActionContext(Action.CREATE, "PUBLISHED"),
        Role.EDITOR: ActionContext(Action.EDIT, "DRAFT", artifact=artifact()),
        Role.QC: ActionContext(Action.APPROVE, "DRAFT", artifact=artifact(qc_status="PASSED")),
        Role.PUBLISHER: ActionContext(
            Action.PUBLISH,
            "REVIEW",
            artifact=artifact(qc_status="PASSED", approval_status="APPROVED", approved_version="v2"),
        ),
    }[role]

    action = invalid_context.action
    with pytest.raises(AuthorizationError):
        policy.authorize(same_actor, invalid_context)


@pytest.mark.parametrize(
    ("action", "lineage_field"),
    [
        (Action.APPROVE, "creator_id"),
        (Action.APPROVE, "editor_id"),
        (Action.PUBLISH, "creator_id"),
        (Action.PUBLISH, "editor_id"),
        (Action.PUBLISH, "approver_id"),
    ],
)
def test_strict_sod_blocks_conflicting_lineage(action, lineage_field):
    role = Role.QC if action == Action.APPROVE else Role.PUBLISHER
    values = {
        "creator_id": None,
        "editor_id": None,
        "approver_id": None,
    }
    values[lineage_field] = "owner"

    context = ActionContext(
        action,
        "REVIEW" if action == Action.APPROVE else "APPROVED",
        artifact(
            qc_status="PASSED",
            approval_status="APPROVED" if action == Action.PUBLISH else None,
            approved_version="v2" if action == Action.PUBLISH else None,
            **values,
        ),
    )

    with pytest.raises(AuthorizationError):
        policy.authorize(
            actor(role, mode=Mode.STRICT_SOD, actor_id="owner"),
            context,
        )


def test_strict_sod_allows_distinct_actor_lineage():
    policy.authorize(
        actor(Role.QC, mode=Mode.STRICT_SOD, actor_id="qc"),
        ActionContext(
            Action.APPROVE,
            "REVIEW",
            artifact(qc_status="PASSED", creator_id="operator", editor_id="editor"),
        ),
    )
    policy.authorize(
        actor(Role.PUBLISHER, mode=Mode.STRICT_SOD, actor_id="publisher"),
        ActionContext(
            Action.PUBLISH,
            "APPROVED",
            artifact(
                qc_status="PASSED",
                approval_status="APPROVED",
                approved_version="v2",
                creator_id="operator",
                editor_id="editor",
                approver_id="qc",
            ),
        ),
    )


def test_full_positive_personal_transition_is_contiguous():
    same_actor = actor(
        Role.OPERATOR, Role.EDITOR, Role.QC, Role.PUBLISHER, actor_id="owner"
    )

    policy.authorize(same_actor, ActionContext(Action.CREATE, "DRAFT"))
    policy.authorize(same_actor, ActionContext(Action.EDIT, "REVIEW", artifact=artifact()))
    policy.authorize(
        same_actor,
        ActionContext(Action.APPROVE, "REVIEW", artifact=artifact(qc_status="PASSED")),
    )
    policy.authorize(
        same_actor,
        ActionContext(
            Action.PUBLISH,
            "APPROVED",
            artifact(
                qc_status="PASSED",
                approval_status="APPROVED",
                approved_version="v2",
            ),
        ),
    )
