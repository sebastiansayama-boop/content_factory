from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


STATUSES = {
    "DRAFT",
    "RESEARCHING",
    "RESEARCH_READY",
    "PLANNING",
    "PRODUCING",
    "REVIEW",
    "APPROVED",
    "EXPORTED",
    "FAILED",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class ContentRun:
    run_id: str
    title: str
    brief: str
    audience: str
    goal: str
    formats: tuple[str, ...]
    constraints: tuple[str, ...]
    status: str
    plan: dict[str, object] | None
    created_at: str
    updated_at: str

    def to_dict(self) -> dict[str, object]:
        value = asdict(self)
        value["formats"] = list(self.formats)
        value["constraints"] = list(self.constraints)
        return value


class ContentRunStore:
    """Durable product-level ContentRun state, separate from execution state."""

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
            CREATE TABLE IF NOT EXISTS content_runs (
                run_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                brief TEXT NOT NULL,
                audience TEXT NOT NULL,
                goal TEXT NOT NULL,
                formats_json TEXT NOT NULL,
                constraints_json TEXT NOT NULL,
                status TEXT NOT NULL,
                plan_json TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        columns = {
            row["name"]
            for row in self._connection.execute("PRAGMA table_info(content_runs)")
        }
        if "plan_json" not in columns:
            self._connection.execute("ALTER TABLE content_runs ADD COLUMN plan_json TEXT")
        self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_content_runs_updated_at ON content_runs(updated_at DESC)"
        )
        self._connection.commit()

    def create(
        self,
        *,
        title: str,
        brief: str,
        audience: str = "",
        goal: str = "",
        formats: tuple[str, ...] = (),
        constraints: tuple[str, ...] = (),
    ) -> ContentRun:
        now = _now()
        run = ContentRun(
            run_id=f"run-{uuid4()}",
            title=title,
            brief=brief,
            audience=audience,
            goal=goal,
            formats=formats,
            constraints=constraints,
            status="DRAFT",
            plan=None,
            created_at=now,
            updated_at=now,
        )
        with self._connection:
            self._connection.execute(
                """
                INSERT INTO content_runs(
                    run_id, title, brief, audience, goal, formats_json,
                    constraints_json, status, plan_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run.run_id,
                    run.title,
                    run.brief,
                    run.audience,
                    run.goal,
                    json.dumps(run.formats, ensure_ascii=False),
                    json.dumps(run.constraints, ensure_ascii=False),
                    run.status,
                    None,
                    run.created_at,
                    run.updated_at,
                ),
            )
        return run

    def get(self, run_id: str) -> ContentRun | None:
        row = self._connection.execute(
            "SELECT * FROM content_runs WHERE run_id = ?", (run_id,)
        ).fetchone()
        return self._from_row(row) if row else None

    def list(self, limit: int = 50) -> list[ContentRun]:
        rows = self._connection.execute(
            "SELECT * FROM content_runs ORDER BY updated_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [self._from_row(row) for row in rows]

    def start_planning(self, run_id: str) -> ContentRun:
        now = _now()
        with self._connection:
            cursor = self._connection.execute(
                """
                UPDATE content_runs
                SET status = 'PLANNING', updated_at = ?
                WHERE run_id = ? AND status IN ('DRAFT', 'FAILED')
                """,
                (now, run_id),
            )
        if cursor.rowcount != 1:
            run = self.get(run_id)
            if run is None:
                raise ValueError("content run not found")
            raise ValueError(f"content run cannot start planning from status {run.status}")
        run = self.get(run_id)
        assert run is not None
        return run

    def save_plan(self, run_id: str, plan: dict[str, object]) -> ContentRun:
        now = _now()
        with self._connection:
            cursor = self._connection.execute(
                """
                UPDATE content_runs
                SET status = 'PLANNING', plan_json = ?, updated_at = ?
                WHERE run_id = ?
                """,
                (json.dumps(plan, ensure_ascii=False), now, run_id),
            )
        if cursor.rowcount != 1:
            raise ValueError("content run not found")
        run = self.get(run_id)
        assert run is not None
        return run

    def mark_failed(self, run_id: str) -> ContentRun:
        now = _now()
        with self._connection:
            cursor = self._connection.execute(
                "UPDATE content_runs SET status = 'FAILED', updated_at = ? WHERE run_id = ?",
                (now, run_id),
            )
        if cursor.rowcount != 1:
            raise ValueError("content run not found")
        run = self.get(run_id)
        assert run is not None
        return run

    @staticmethod
    def _from_row(row: sqlite3.Row) -> ContentRun:
        return ContentRun(
            run_id=row["run_id"],
            title=row["title"],
            brief=row["brief"],
            audience=row["audience"],
            goal=row["goal"],
            formats=tuple(json.loads(row["formats_json"])),
            constraints=tuple(json.loads(row["constraints_json"])),
            status=row["status"],
            plan=json.loads(row["plan_json"]) if row["plan_json"] else None,
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def close(self) -> None:
        self._connection.close()
