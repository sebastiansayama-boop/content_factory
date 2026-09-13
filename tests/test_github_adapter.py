from content_factory.github_adapter import (
    GitHubChangeEvidence,
    GitHubChangeState,
    GitHubOperation,
    GitHubOperationIntent,
    GitHubOperationObservation,
    bind_work_item_to_github,
    reconcile_github_operation,
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


def test_github_operation_reconciles_against_independent_observation():
    intent = GitHubOperationIntent(
        operation_id="op-005",
        work_item_id="wi-005",
        operation=GitHubOperation.UPDATE_FILE,
        repository_full_name="sebastiansayama-boop/content_factory",
        branch_name="experiment/005-github-reconciliation-proof",
        path="10_records/2026-09-13-experiment-005-github-reconciliation.md",
    )
    observation = GitHubOperationObservation(
        operation_id="op-005",
        repository_full_name="sebastiansayama-boop/content_factory",
        operation=GitHubOperation.UPDATE_FILE,
        branch_name="experiment/005-github-reconciliation-proof",
        path="10_records/2026-09-13-experiment-005-github-reconciliation.md",
        commit_sha="abc123",
    )

    result = reconcile_github_operation(intent, observation)

    assert result.reconciled is True
    assert result.unknowns == ()
    assert result.mismatches == ()
    assert result.evidence_refs == (
        "github://sebastiansayama-boop/content_factory/commit/abc123",
        "github://sebastiansayama-boop/content_factory/blob/experiment/005-github-reconciliation-proof/10_records/2026-09-13-experiment-005-github-reconciliation.md",
    )
    assert "acceptance" in result.reason


def test_missing_github_observation_remains_unknown():
    intent = GitHubOperationIntent(
        operation_id="op-005",
        work_item_id="wi-005",
        operation=GitHubOperation.UPDATE_FILE,
        repository_full_name="sebastiansayama-boop/content_factory",
        branch_name="experiment/005-github-reconciliation-proof",
        path="x.md",
    )

    result = reconcile_github_operation(intent, None)

    assert result.reconciled is False
    assert result.unknowns == ("GitHub operation result was not observed",)


def test_mismatched_observation_is_not_reconciled():
    intent = GitHubOperationIntent(
        operation_id="op-005",
        work_item_id="wi-005",
        operation=GitHubOperation.UPDATE_FILE,
        repository_full_name="sebastiansayama-boop/content_factory",
        branch_name="experiment/005-github-reconciliation-proof",
        path="expected.md",
    )
    observation = GitHubOperationObservation(
        operation_id="op-other",
        repository_full_name="sebastiansayama-boop/content_factory",
        operation=GitHubOperation.UPDATE_FILE,
        branch_name="other-branch",
        path="actual.md",
        commit_sha="abc123",
    )

    result = reconcile_github_operation(intent, observation)

    assert result.reconciled is False
    assert result.unknowns == ()
    assert result.mismatches == (
        "operation identity differs",
        "branch differs",
        "path differs",
    )


def test_expected_commit_mismatch_is_explicit():
    intent = GitHubOperationIntent(
        operation_id="op-005",
        work_item_id="wi-005",
        operation=GitHubOperation.UPDATE_FILE,
        repository_full_name="sebastiansayama-boop/content_factory",
        branch_name="experiment/005-github-reconciliation-proof",
        path="x.md",
        expected_commit_sha="expected",
    )
    observation = GitHubOperationObservation(
        operation_id="op-005",
        repository_full_name="sebastiansayama-boop/content_factory",
        operation=GitHubOperation.UPDATE_FILE,
        branch_name="experiment/005-github-reconciliation-proof",
        path="x.md",
        commit_sha="actual",
    )

    result = reconcile_github_operation(intent, observation)

    assert result.reconciled is False
    assert result.mismatches == ("observed commit differs from expected commit",)


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
