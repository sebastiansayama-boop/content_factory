import pytest

from content_factory.state_machine import (
    InvalidStateTransition,
    is_terminal,
    require_publication_parent,
    validate_transition,
)


def test_declared_lifecycles_allow_expected_transitions():
    validate_transition("content_run", "REVIEW", "APPROVED")
    validate_transition("publication", "PREPARED", "PUBLISHING")
    validate_transition("publication", "PUBLISHING", "PUBLISHED")
    validate_transition("execution", "RUNNING", "UNKNOWN")


def test_terminal_states_cannot_move_forward():
    with pytest.raises(InvalidStateTransition):
        validate_transition("content_run", "PUBLISHED", "FAILED")
    with pytest.raises(InvalidStateTransition):
        validate_transition("publication", "PUBLISHED", "PUBLISHING")
    assert is_terminal("content_run", "PUBLISHED")
    assert is_terminal("publication", "PUBLISHED")


def test_publication_requires_approved_parent_run():
    with pytest.raises(InvalidStateTransition):
        require_publication_parent("REVIEW", "PREPARED", "PUBLISHING")
    require_publication_parent("APPROVED", "PREPARED", "PUBLISHING")
    require_publication_parent("EXPORTED", "PREPARED", "PUBLISHING")


def test_publication_requires_publishing_state_before_published():
    with pytest.raises(InvalidStateTransition):
        require_publication_parent("APPROVED", "PREPARED", "PUBLISHED")
    require_publication_parent("APPROVED", "PUBLISHING", "PUBLISHED")
