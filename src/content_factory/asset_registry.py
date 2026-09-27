from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class RegisteredAsset:
    asset_id: str
    run_id: str
    job_id: str
    asset_request_id: str
    script_unit_id: str
    asset_type: str
    provider: str
    uri: str
    claim_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    metadata: dict[str, object]
    created_at: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self) | {
            "claim_refs": list(self.claim_refs),
            "evidence_refs": list(self.evidence_refs),
        }


class AssetRegistry:
    """Durable registry of provider outputs that passed job completion."""

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
            CREATE TABLE IF NOT EXISTS assets (
                asset_id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                job_id TEXT NOT NULL UNIQUE,
                asset_request_id TEXT NOT NULL,
                script_unit_id TEXT NOT NULL,
                asset_type TEXT NOT NULL,
                provider TEXT NOT NULL,
                uri TEXT NOT NULL,
                claim_refs_json TEXT NOT NULL,
                evidence_refs_json TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_assets_run ON assets(run_id, created_at)"
        )
        self._connection.commit()

    def register_completed_job(self, job) -> RegisteredAsset:
        if job.status != "COMPLETED":
            raise ValueError("only COMPLETED asset jobs can be registered")
        result = job.result
        if not isinstance(result, dict):
            raise ValueError("completed asset job has no result")
        asset_id = str(result.get("asset_id") or "").strip()
        if not asset_id:
            raise ValueError("completed asset result requires asset_id")
        provider = str(result.get("provider") or "").strip()
        uri = str(result.get("uri") or result.get("path") or "").strip()
        if not provider or not uri:
            raise ValueError("completed asset result requires provider and uri/path")
        metadata = result.get("metadata", {})
        if not isinstance(metadata, dict):
            raise ValueError("asset metadata must be an object")
        asset = RegisteredAsset(
            asset_id=asset_id,
            run_id=job.run_id,
            job_id=job.job_id,
            asset_request_id=job.asset_request_id,
            script_unit_id=job.script_unit_id,
            asset_type=job.asset_type,
            provider=provider,
            uri=uri,
            claim_refs=job.claim_refs,
            evidence_refs=job.evidence_refs,
            metadata=dict(metadata),
            created_at=_now(),
        )
        with self._connection:
            self._connection.execute(
                """
                INSERT INTO assets(
                    asset_id, run_id, job_id, asset_request_id, script_unit_id,
                    asset_type, provider, uri, claim_refs_json, evidence_refs_json,
                    metadata_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(job_id) DO UPDATE SET
                    asset_id=excluded.asset_id,
                    uri=excluded.uri,
                    provider=excluded.provider,
                    metadata_json=excluded.metadata_json
                """,
                (
                    asset.asset_id, asset.run_id, asset.job_id, asset.asset_request_id,
                    asset.script_unit_id, asset.asset_type, asset.provider, asset.uri,
                    json.dumps(asset.claim_refs), json.dumps(asset.evidence_refs),
                    json.dumps(asset.metadata, ensure_ascii=False), asset.created_at,
                ),
            )
        stored = self.get_by_job(job.job_id)
        assert stored is not None
        return stored

    def get(self, asset_id: str) -> RegisteredAsset | None:
        row = self._connection.execute(
            "SELECT * FROM assets WHERE asset_id = ?", (asset_id,)
        ).fetchone()
        return self._from_row(row) if row else None

    def get_by_job(self, job_id: str) -> RegisteredAsset | None:
        row = self._connection.execute(
            "SELECT * FROM assets WHERE job_id = ?", (job_id,)
        ).fetchone()
        return self._from_row(row) if row else None

    def list_for_run(self, run_id: str) -> list[RegisteredAsset]:
        rows = self._connection.execute(
            "SELECT * FROM assets WHERE run_id = ? ORDER BY created_at, asset_id",
            (run_id,),
        ).fetchall()
        return [self._from_row(row) for row in rows]

    @staticmethod
    def _from_row(row: sqlite3.Row) -> RegisteredAsset:
        return RegisteredAsset(
            asset_id=row["asset_id"],
            run_id=row["run_id"],
            job_id=row["job_id"],
            asset_request_id=row["asset_request_id"],
            script_unit_id=row["script_unit_id"],
            asset_type=row["asset_type"],
            provider=row["provider"],
            uri=row["uri"],
            claim_refs=tuple(json.loads(row["claim_refs_json"])),
            evidence_refs=tuple(json.loads(row["evidence_refs_json"])),
            metadata=json.loads(row["metadata_json"]),
            created_at=row["created_at"],
        )

    def close(self) -> None:
        self._connection.close()
