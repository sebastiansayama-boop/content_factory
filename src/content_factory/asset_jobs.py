from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


JOB_STATUSES = {"QUEUED", "RUNNING", "SUBMITTED", "COMPLETED", "FAILED"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class AssetJob:
    job_id: str
    run_id: str
    asset_request_id: str
    script_unit_id: str
    asset_type: str
    status: str
    claim_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    acceptance_criteria: tuple[str, ...]
    result: dict[str, object] | None
    created_at: str
    updated_at: str

    def to_dict(self) -> dict[str, object]:
        value = asdict(self)
        value["claim_refs"] = list(self.claim_refs)
        value["evidence_refs"] = list(self.evidence_refs)
        value["acceptance_criteria"] = list(self.acceptance_criteria)
        return value


class AssetJobStore:
    """Durable production-job state; execution is supplied by a capability adapter."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(self.path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA journal_mode = WAL")
        self._connection.execute("PRAGMA synchronous = FULL")
        self._initialize()

    def _initialize(self) -> None:
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS asset_jobs (
                job_id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                asset_request_id TEXT NOT NULL,
                script_unit_id TEXT NOT NULL,
                asset_type TEXT NOT NULL,
                status TEXT NOT NULL,
                claim_refs_json TEXT NOT NULL,
                evidence_refs_json TEXT NOT NULL,
                acceptance_criteria_json TEXT NOT NULL,
                result_json TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(run_id, asset_request_id)
            )
            """
        )
        self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_asset_jobs_run ON asset_jobs(run_id, created_at)"
        )
        self._connection.commit()

    def create_from_plan(self, run_id: str, production_plan: dict[str, object]) -> list[AssetJob]:
        requests = production_plan.get("asset_requests")
        if not isinstance(requests, list) or not requests:
            raise ValueError("production plan must contain asset_requests")

        jobs: list[AssetJob] = []
        now = _now()
        with self._connection:
            for request in requests:
                if not isinstance(request, dict):
                    raise ValueError("asset request must be an object")
                request_id = str(request.get("asset_request_id") or "").strip()
                unit_id = str(request.get("script_unit_id") or "").strip()
                asset_type = str(request.get("type") or "").strip()
                if not request_id or not unit_id or not asset_type:
                    raise ValueError("asset request requires id, script_unit_id and type")
                claim_refs = self._strings(request.get("claim_refs"), "claim_refs")
                evidence_refs = self._strings(request.get("evidence_refs"), "evidence_refs")
                criteria = self._strings(request.get("acceptance_criteria"), "acceptance_criteria")
                job = AssetJob(
                    job_id=f"job-{run_id}-{request_id}",
                    run_id=run_id,
                    asset_request_id=request_id,
                    script_unit_id=unit_id,
                    asset_type=asset_type,
                    status="QUEUED",
                    claim_refs=tuple(claim_refs),
                    evidence_refs=tuple(evidence_refs),
                    acceptance_criteria=tuple(criteria),
                    result=None,
                    created_at=now,
                    updated_at=now,
                )
                self._connection.execute(
                    """
                    INSERT OR IGNORE INTO asset_jobs(
                        job_id, run_id, asset_request_id, script_unit_id, asset_type,
                        status, claim_refs_json, evidence_refs_json,
                        acceptance_criteria_json, result_json, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        job.job_id, job.run_id, job.asset_request_id, job.script_unit_id,
                        job.asset_type, job.status, json.dumps(job.claim_refs),
                        json.dumps(job.evidence_refs), json.dumps(job.acceptance_criteria),
                        None, job.created_at, job.updated_at,
                    ),
                )
                stored = self.get(job.job_id)
                if stored is not None:
                    jobs.append(stored)
        return jobs

    def get(self, job_id: str) -> AssetJob | None:
        row = self._connection.execute(
            "SELECT * FROM asset_jobs WHERE job_id = ?", (job_id,)
        ).fetchone()
        return self._from_row(row) if row else None

    def list_for_run(self, run_id: str) -> list[AssetJob]:
        rows = self._connection.execute(
            "SELECT * FROM asset_jobs WHERE run_id = ? ORDER BY created_at, job_id", (run_id,)
        ).fetchall()
        return [self._from_row(row) for row in rows]

    def mark_running(self, job_id: str) -> AssetJob:
        return self._transition(job_id, "RUNNING", None)

    def submit(self, job_id: str, result: dict[str, object]) -> AssetJob:
        return self._transition(job_id, "SUBMITTED", result)

    def complete(self, job_id: str, result: dict[str, object]) -> AssetJob:
        return self._transition(job_id, "COMPLETED", result)

    def fail(self, job_id: str, result: dict[str, object]) -> AssetJob:
        return self._transition(job_id, "FAILED", result)

    def _transition(self, job_id: str, status: str, result: dict[str, object] | None) -> AssetJob:
        if status not in JOB_STATUSES:
            raise ValueError(f"invalid asset job status: {status}")
        current = self.get(job_id)
        if current is None:
            raise ValueError("asset job not found")
        allowed = {
            "QUEUED": {"RUNNING", "FAILED"},
            "RUNNING": {"SUBMITTED", "COMPLETED", "FAILED"},
            "SUBMITTED": {"COMPLETED", "FAILED"},
            "COMPLETED": set(),
            "FAILED": {"RUNNING"},
        }
        if status not in allowed[current.status]:
            raise ValueError(f"asset job cannot transition {current.status} -> {status}")
        now = _now()
        with self._connection:
            self._connection.execute(
                "UPDATE asset_jobs SET status = ?, result_json = ?, updated_at = ? WHERE job_id = ?",
                (status, json.dumps(result, ensure_ascii=False) if result is not None else None, now, job_id),
            )
        updated = self.get(job_id)
        assert updated is not None
        return updated

    @staticmethod
    def _strings(value: object, name: str) -> list[str]:
        if not isinstance(value, list) or not all(isinstance(v, str) and v.strip() for v in value):
            raise ValueError(f"{name} must be an array of non-empty strings")
        return list(dict.fromkeys(v.strip() for v in value))

    @staticmethod
    def _from_row(row: sqlite3.Row) -> AssetJob:
        return AssetJob(
            job_id=row["job_id"],
            run_id=row["run_id"],
            asset_request_id=row["asset_request_id"],
            script_unit_id=row["script_unit_id"],
            asset_type=row["asset_type"],
            status=row["status"],
            claim_refs=tuple(json.loads(row["claim_refs_json"])),
            evidence_refs=tuple(json.loads(row["evidence_refs_json"])),
            acceptance_criteria=tuple(json.loads(row["acceptance_criteria_json"])),
            result=json.loads(row["result_json"]) if row["result_json"] else None,
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def close(self) -> None:
        self._connection.close()
