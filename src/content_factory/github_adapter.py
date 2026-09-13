from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class GitHubChangeState(str, Enum):
    OPEN = "open"
    MERGED = "merged"
    CLOSED = "closed"


@dataclass(frozen=True)
class GitHubWorkContext:
    """Repository-facing identity for one Factory work item.

    GitHub identifiers are integration evidence. They do not replace the
    Factory WorkItem identity, runtime state, or semantic authority model.
    """

    work_item_id: str
    issue_number: int
    branch_name: str
    repository_full_name: str


@dataclass(frozen=True)
class GitHubChangeEvidence:
    """Normalized GitHub observations relevant to change verification."""

    repository_full_name: str
    pull_request_number: int
    head_sha: str
    base_branch: str
    change_state: GitHubChangeState
    ci_passed: bool
    review_count: int
    merged: bool


@dataclass(frozen=True)
class FactoryChangeVerification:
    """Factory-side interpretation of GitHub evidence.

    `verified` is deliberately narrower than semantic acceptance. A passing
    GitHub change check cannot grant Factory acceptance or publication
    authority by itself.
    """

    verified: bool
    evidence_refs: tuple[str, ...]
    unknowns: tuple[str, ...] = ()
    reason: str = ""


def bind_work_item_to_github(
    *,
    work_item_id: str,
    issue_number: int,
    branch_name: str,
    repository_full_name: str,
) -> GitHubWorkContext:
    """Create the explicit adapter identity between Factory and GitHub."""

    if not work_item_id:
        raise ValueError("work_item_id is required")
    if issue_number <= 0:
        raise ValueError("issue_number must be positive")
    if not branch_name:
        raise ValueError("branch_name is required")
    if not repository_full_name:
        raise ValueError("repository_full_name is required")

    return GitHubWorkContext(
        work_item_id=work_item_id,
        issue_number=issue_number,
        branch_name=branch_name,
        repository_full_name=repository_full_name,
    )


def verify_github_change(evidence: GitHubChangeEvidence) -> FactoryChangeVerification:
    """Normalize repository mechanics without promoting them to acceptance."""

    refs = (
        f"github://{evidence.repository_full_name}/pull/{evidence.pull_request_number}",
        f"github://{evidence.repository_full_name}/commit/{evidence.head_sha}",
    )

    if not evidence.ci_passed:
        return FactoryChangeVerification(
            verified=False,
            evidence_refs=refs,
            reason="required GitHub CI evidence is not passing; semantic acceptance remains external",
        )

    if evidence.change_state == GitHubChangeState.CLOSED and not evidence.merged:
        return FactoryChangeVerification(
            verified=False,
            evidence_refs=refs,
            reason="pull request is closed without a merge; semantic acceptance remains external",
        )

    unknowns: list[str] = []
    if evidence.review_count == 0:
        unknowns.append("independent review boundary was not observed")

    if evidence.merged:
        reason = "GitHub change mechanics verified; semantic acceptance remains external"
    else:
        reason = "GitHub change mechanics verified for an open pull request; semantic acceptance remains external"

    return FactoryChangeVerification(
        verified=True,
        evidence_refs=refs,
        unknowns=tuple(unknowns),
        reason=reason,
    )
