import pytest

from content_factory.access_policy import (
    Action,
    ActionContext,
    ActorContext,
    ArtifactContext,
    AuthorizationError,
    CapabilityPolicy,
    Mode,
    Role,
)


def a(*roles, mode=Mode.PERSONAL, actor_id="actor-1"):
    return ActorContext(actor_id, frozenset(roles), mode)


def art(**kwargs):
    return ArtifactContext("v2", **kwargs)


policy = CapabilityPolicy()


def test_core_role_matrix_is_strict():
    policy.authorize(a(Role.OPERATOR), ActionContext(Action.CREATE, "DRAFT"))
    policy.authorize(a(Role.EDITOR), ActionContext(Action.EDIT, "REVIEW", art()))
    policy.authorize(a(Role.QC), ActionContext(Action.APPROVE, "REVIEW", art(qc_status="PASSED")))
    policy.authorize(a(Role.PUBLISHER), ActionContext(
        Action.PUBLISH, "APPROVED",
        art(qc_status="PASSED", approval_status="APPROVED", approved_version="v2"),
    ))


@pytest.mark.parametrize(
    ("role", "action"),
    [
        (Role.OPERATOR, Action.EDIT),
        (Role.OPERATOR, Action.APPROVE),
        (Role.OPERATOR, Action.PUBLISH),
        (Role.EDITOR, Action.CREATE),
        (Role.EDITOR, Action.APPROVE),
        (Role.EDITOR, Action.PUBLISH),
        (Role.QC, Action.CREATE),
        (Role.QC, Action.EDIT),
        (Role.QC, Action.PUBLISH),
        (Role.PUBLISHER, Action.CREATE),
        (Role.PUBLISHER, Action.EDIT),
        (Role.PUBLISHER, Action.APPROVE),
    ],
)
def test_cross_role_actions_are_denied(role, action):
    with pytest.raises(AuthorizationError):
        policy.authorize(a(role), ActionContext(
            action,
            "REVIEW" if action in {Action.EDIT, Action.APPROVE} else "DRAFT",
            art(qc_status="PASSED", approval_status="APPROVED", approved_version="v2"),
        ))


def test_personal_mode_allows_one_actor_to_hold_all_roles():
    actor = a(Role.OPERATOR, Role.EDITOR, Role.QC, Role.PUBLISHER)
    policy.authorize(actor, ActionContext(Action.CREATE, "DRAFT"))
    policy.authorize(actor, ActionContext(Action.EDIT, "REVIEW", art()))
    policy.authorize(actor, ActionContext(
        Action.APPROVE, "REVIEW", art(qc_status="PASSED")
    ))
    policy.authorize(actor, ActionContext(
        Action.PUBLISH, "APPROVED",
        art(qc_status="PASSED", approval_status="APPROVED", approved_version="v2"),
    ))


def test_personal_publish_still_requires_approved_version():
    with pytest.raises(AuthorizationError, match="approved artifact version"):
        policy.authorize(a(Role.PUBLISHER), ActionContext(
            Action.PUBLISH, "APPROVED",
            art(qc_status="PASSED", approval_status="APPROVED", approved_version="v1"),
        ))


def test_approval_requires_qc_pass():
    with pytest.raises(AuthorizationError, match="QC status PASSED"):
        policy.authorize(a(Role.QC), ActionContext(
            Action.APPROVE, "REVIEW", art(qc_status="FAILED")
        ))


def test_strict_sod_blocks_creator_from_approving():
    with pytest.raises(AuthorizationError, match="creator/editor"):
        policy.authorize(
            a(Role.QC, mode=Mode.STRICT_SOD, actor_id="creator"),
            ActionContext(
                Action.APPROVE, "REVIEW",
                art(qc_status="PASSED", creator_id="creator"),
            ),
        )


def test_strict_sod_blocks_approver_from_publishing():
    with pytest.raises(AuthorizationError, match="creator/editor/approver"):
        policy.authorize(
            a(Role.PUBLISHER, mode=Mode.STRICT_SOD, actor_id="qc-1"),
            ActionContext(
                Action.PUBLISH, "APPROVED",
                art(
                    qc_status="PASSED",
                    approval_status="APPROVED",
                    approved_version="v2",
                    approver_id="qc-1",
                ),
            ),
        )


def test_strict_sod_allows_distinct_actors():
    policy.authorize(
        a(Role.OPERATOR, actor_id="operator"),
        ActionContext(Action.CREATE, "DRAFT"),
    )
    policy.authorize(
        a(Role.EDITOR, mode=Mode.STRICT_SOD, actor_id="editor"),
        ActionContext(Action.EDIT, "REVIEW", art(creator_id="operator")),
    )
    policy.authorize(
        a(Role.QC, mode=Mode.STRICT_SOD, actor_id="qc"),
        ActionContext(
            Action.APPROVE, "REVIEW",
            art(qc_status="PASSED", creator_id="operator", editor_id="editor"),
        ),
    )
    policy.authorize(
        a(Role.PUBLISHER, mode=Mode.STRICT_SOD, actor_id="publisher"),
        ActionContext(
            Action.PUBLISH, "APPROVED",
            art(
                qc_status="PASSED",
                approval_status="APPROVED",
                approved_version="v2",
                creator_id="operator",
                editor_id="editor",
                approver_id="qc",
            ),
        ),
    )


def test_editing_approved_version_must_create_new_version():
    with pytest.raises(AuthorizationError, match="new artifact version"):
        policy.authorize(
            a(Role.EDITOR),
            ActionContext(
                Action.EDIT,
                "APPROVED",
                art(approved_version="v2"),
            ),
        )
