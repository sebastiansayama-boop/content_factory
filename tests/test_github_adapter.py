from content_factory.github_adapter import (
    GitHubChangeEvidence,
    GitHubChangeState,
    bind_work_item_to_github,
    verify_github_change,
)


def test_factory_work_identity_is_explicitly_bound_to_github():
    context = bind_work_item_to_github(
        work_item_id="wi-github-004",
        issue_number=27,
        branch_name="experiment/004-github-semantic-adapter",
        repository_full_name="sebastiansayama-boop/content_factory",
    )

    assert context.work_item_id == "wi-github-004"
    assert context.issue_number == 27
    assert context.branch_name == "experiment/004-github-semantic-adapter"


def test_passing_github_change_is_verified_without_granting_acceptance():
    result = verify_github_change(
        GitHubChangeEvidence(
            repository_full_name="sebastiansayama-boop/content_factory",
            pull_request_number=999,
            head_sha="abc123",
            base_branch="main",
            change_state=GitHubChangeState.OPEN,
            ci_passed=True,
            review_count=1,
            merged=False,
        )
    )

    assert result.verified is True
    assert result.evidence_refs == (
        "github://sebastiansayama-boop/content_factory/pull/999",
        "github://sebastiansayama-boop/content_factory/commit/abc123",
    )
    assert result.unknowns == ()
    assert "acceptance" in result.reason


def test_ci_failure_is_not_verified():
    result = verify_github_change(
        GitHubChangeEvidence(
            repository_full_name="sebastiansayama-boop/content_factory",
            pull_request_number=999,
            head_sha="abc123",
            base_branch="main",
            change_state=GitHubChangeState.OPEN,
            ci_passed=False,
            review_count=1,
            merged=False,
        )
    )

    assert result.verified is False


def test_missing_review_remains_explicit_unknown():
    result = verify_github_change(
        GitHubChangeEvidence(
            repository_full_name="sebastiansayama-boop/content_factory",
            pull_request_number=999,
            head_sha="abc123",
            base_branch="main",
            change_state=GitHubChangeState.OPEN,
            ci_passed=True,
            review_count=0,
            merged=False,
        )
    )

    assert result.verified is True
    assert result.unknowns == ("independent review boundary was not observed",)


def test_closed_unmerged_change_is_not_verified():
    result = verify_github_change(
        GitHubChangeEvidence(
            repository_full_name="sebastiansayama-boop/content_factory",
            pull_request_number=999,
            head_sha="abc123",
            base_branch="main",
            change_state=GitHubChangeState.CLOSED,
            ci_passed=True,
            review_count=1,
            merged=False,
        )
    )

    assert result.verified is False
