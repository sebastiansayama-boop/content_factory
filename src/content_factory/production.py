from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ProductionJobStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    INVALIDATED = "INVALIDATED"


@dataclass(frozen=True)
class Artifact:
    artifact_id: str
    artifact_type: str
    revision_id: str
    reference: str | None = None
    payload: Any = None
    producer_job_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_now)


@dataclass(frozen=True)
class ProductionJob:
    job_id: str
    capability_id: str
    provider: str
    provider_job_id: str
    input_artifact_ids: tuple[str, ...] = ()
    parameters: dict[str, Any] = field(default_factory=dict)
    status: ProductionJobStatus = ProductionJobStatus.SUBMITTED
    output_artifact_ids: tuple[str, ...] = ()
    error: str | None = None
    created_at: str = field(default_factory=_now)
    started_at: str | None = None
    completed_at: str | None = None
    evidence_refs: tuple[str, ...] = ()


class ProductionContractError(ValueError):
    pass


class ProductionRegistry:
    """Minimal provider-neutral production job/artifact dependency registry.

    This is deliberately not a scheduler, provider router, or workflow engine.
    It only records production identity and enough dependency information to
    invalidate jobs when an input artifact changes.
    """

    def __init__(self) -> None:
        self.jobs: dict[str, ProductionJob] = {}
        self.artifacts: dict[str, Artifact] = {}

    def add_job(self, job: ProductionJob) -> ProductionJob:
        if job.job_id in self.jobs:
            raise ProductionContractError(f"job already exists: {job.job_id}")
        missing = [
            artifact_id
            for artifact_id in job.input_artifact_ids
            if artifact_id not in self.artifacts
        ]
        if missing:
            raise ProductionContractError(
                f"job references unknown input artifacts: {', '.join(missing)}"
            )
        self.jobs[job.job_id] = job
        return job

    def add_artifact(self, artifact: Artifact) -> Artifact:
        if artifact.artifact_id in self.artifacts:
            raise ProductionContractError(
                f"artifact already exists: {artifact.artifact_id}"
            )
        if artifact.producer_job_id is not None and artifact.producer_job_id not in self.jobs:
            raise ProductionContractError(
                f"artifact references unknown producer job: {artifact.producer_job_id}"
            )
        self.artifacts[artifact.artifact_id] = artifact
        return artifact

    def complete_job(
        self,
        job_id: str,
        output_artifacts: tuple[Artifact, ...] | list[Artifact],
        *,
        evidence_refs: tuple[str, ...] = (),
    ) -> ProductionJob:
        job = self.jobs[job_id]
        if job.status not in {ProductionJobStatus.SUBMITTED, ProductionJobStatus.RUNNING}:
            raise ProductionContractError(
                f"cannot complete job from {job.status.value}"
            )
        for artifact in output_artifacts:
            if artifact.producer_job_id != job_id:
                raise ProductionContractError(
                    f"artifact {artifact.artifact_id} must bind to producer job {job_id}"
                )
            self.add_artifact(artifact)
        completed = ProductionJob(
            **{
                **job.__dict__,
                "status": ProductionJobStatus.SUCCEEDED,
                "output_artifact_ids": tuple(
                    artifact.artifact_id for artifact in output_artifacts
                ),
                "completed_at": _now(),
                "evidence_refs": evidence_refs,
            }
        )
        self.jobs[job_id] = completed
        return completed

    def invalidate_jobs_consuming(self, artifact_id: str) -> tuple[str, ...]:
        if artifact_id not in self.artifacts:
            raise ProductionContractError(f"unknown artifact: {artifact_id}")
        invalidated: list[str] = []
        for job_id, job in self.jobs.items():
            if artifact_id in job.input_artifact_ids and job.status in {
                ProductionJobStatus.SUBMITTED,
                ProductionJobStatus.RUNNING,
                ProductionJobStatus.SUCCEEDED,
            }:
                self.jobs[job_id] = ProductionJob(
                    **{**job.__dict__, "status": ProductionJobStatus.INVALIDATED}
                )
                invalidated.append(job_id)
        return tuple(invalidated)
