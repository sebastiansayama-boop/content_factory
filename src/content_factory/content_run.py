from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from typing import Any

from content_factory.state_machine import InvalidStateTransition, validate_transition


STATUSES = {
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
    result: dict[str, object] | None
    created_at: str
    updated_at: str

    def to_dict(self) -> dict[str, object]:
        value = asdict(self)
        value["formats"] = list(self.formats)
        value["constraints"] = list(self.constraints)
        return value


@dataclass(frozen=True)
class ContentBriefRevision:
    brief_id: str
    revision_id: str
    run_id: str
    payload: dict[str, Any]
    created_at: str

    def to_dict(self) -> dict[str, object]:
        return {
            "brief_id": self.brief_id,
            "revision_id": self.revision_id,
            "run_id": self.run_id,
            "brief": self.payload,
            "created_at": self.created_at,
        }


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
                result_json TEXT,
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
        if "result_json" not in columns:
            self._connection.execute("ALTER TABLE content_runs ADD COLUMN result_json TEXT")
        self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_content_runs_updated_at ON content_runs(updated_at DESC)"
        )
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS content_brief_revisions (
                brief_id TEXT NOT NULL,
                revision_id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE(brief_id, revision_id),
                FOREIGN KEY(run_id) REFERENCES content_runs(run_id)
            )
            """
        )
        self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_content_brief_revisions_run ON content_brief_revisions(run_id, created_at DESC)"
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
            result=None,
            created_at=now,
            updated_at=now,
        )
        with self._connection:
            self._connection.execute(
                """
                INSERT INTO content_runs(
                    run_id, title, brief, audience, goal, formats_json,
                    constraints_json, status, plan_json, result_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        current = self.get(run_id)
        if current is None:
            raise ValueError("content run not found")
        validate_transition("content_run", current.status, "PLANNING")
        now = _now()
        with self._connection:
            cursor = self._connection.execute(
                """
                UPDATE content_runs
                SET status = 'PLANNING', updated_at = ?
                WHERE run_id = ? AND status IN ('DRAFT', 'FAILED', 'RESEARCH_READY')
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
        current = self.get(run_id)
        if current is None:
            raise ValueError("content run not found")
        validate_transition("content_run", current.status, "PLANNING")
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

    def save_content_brief(self, run_id: str, brief: dict[str, object]) -> ContentBriefRevision:
        brief_id = str(brief.get("brief_id") or "").strip()
        if not brief_id:
            raise ValueError("content brief requires brief_id")
        if self.get(run_id) is None:
            raise ValueError("content run not found")
        previous = self.get_content_brief(run_id)
        revision_no = 1
        if previous is not None:
            prefix = f"{brief_id}-r"
            try:
                revision_no = max(
                    int(item["revision_id"].split("-r")[-1])
                    for item in self._connection.execute(
                        "SELECT revision_id FROM content_brief_revisions WHERE brief_id = ?",
                        (brief_id,),
                    )
                    if str(item["revision_id"]).startswith(prefix)
                ) + 1
            except ValueError:
                revision_no = 1
        revision_id = f"{brief_id}-r{revision_no}"
        created_at = _now()
        with self._connection:
            self._connection.execute(
                """
                INSERT INTO content_brief_revisions(
                    brief_id, revision_id, run_id, payload_json, created_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (brief_id, revision_id, run_id, json.dumps(brief, ensure_ascii=False), created_at),
            )
        return ContentBriefRevision(brief_id, revision_id, run_id, dict(brief), created_at)

    def get_content_brief(self, run_id: str, revision_id: str | None = None) -> ContentBriefRevision | None:
        if revision_id:
            row = self._connection.execute(
                "SELECT * FROM content_brief_revisions WHERE run_id = ? AND revision_id = ?",
                (run_id, revision_id),
            ).fetchone()
        else:
            row = self._connection.execute(
                """
                SELECT * FROM content_brief_revisions
                WHERE run_id = ?
                ORDER BY created_at DESC, revision_id DESC
                LIMIT 1
                """,
                (run_id,),
            ).fetchone()
        if row is None:
            return None
        return ContentBriefRevision(
            row["brief_id"], row["revision_id"], row["run_id"],
            json.loads(row["payload_json"]), row["created_at"],
        )

    def list_content_brief_revisions(self, run_id: str) -> list[ContentBriefRevision]:
        rows = self._connection.execute(
            """
            SELECT * FROM content_brief_revisions
            WHERE run_id = ?
            ORDER BY created_at ASC, revision_id ASC
            """,
            (run_id,),
        ).fetchall()
        return [
            ContentBriefRevision(
                row["brief_id"], row["revision_id"], row["run_id"],
                json.loads(row["payload_json"]), row["created_at"],
            )
            for row in rows
        ]

    def start_execution(self, run_id: str) -> ContentRun:
        current = self.get(run_id)
        if current is None:
            raise ValueError("content run not found")
        validate_transition("content_run", current.status, "RESEARCHING")
        now = _now()
        with self._connection:
            cursor = self._connection.execute(
                """
                UPDATE content_runs
                SET status = 'RESEARCHING', updated_at = ?
                WHERE run_id = ? AND status IN ('DRAFT', 'FAILED', 'PLANNING')
                """,
                (now, run_id),
            )
        if cursor.rowcount != 1:
            run = self.get(run_id)
            if run is None:
                raise ValueError("content run not found")
            raise ValueError(f"content run cannot execute from status {run.status}")
        run = self.get(run_id)
        assert run is not None
        return run

    def start_producing(self, run_id: str) -> ContentRun:
        current = self.get(run_id)
        if current is None:
            raise ValueError("content run not found")
        validate_transition("content_run", current.status, "PRODUCING")
        now = _now()
        with self._connection:
            cursor = self._connection.execute(
                """
                UPDATE content_runs
                SET status = 'PRODUCING', updated_at = ?
                WHERE run_id = ? AND status IN ('REVIEW', 'PLANNING', 'FAILED')
                """,
                (now, run_id),
            )
        if cursor.rowcount != 1:
            run = self.get(run_id)
            if run is None:
                raise ValueError("content run not found")
            raise ValueError(f"content run cannot start production from status {run.status}")
        run = self.get(run_id)
        assert run is not None
        return run

    def save_research_result(self, run_id: str, result: dict[str, object]) -> ContentRun:
        current = self.get(run_id)
        if current is None:
            raise ValueError("content run not found")
        validate_transition("content_run", current.status, "RESEARCH_READY")
        now = _now()
        with self._connection:
            cursor = self._connection.execute(
                """
                UPDATE content_runs
                SET status = 'RESEARCH_READY', result_json = ?, updated_at = ?
                WHERE run_id = ?
                """,
                (json.dumps(result, ensure_ascii=False), now, run_id),
            )
        if cursor.rowcount != 1:
            raise ValueError("content run not found")
        run = self.get(run_id)
        assert run is not None
        return run

    def save_result(self, run_id: str, result: dict[str, object]) -> ContentRun:
        current = self.get(run_id)
        if current is None:
            raise ValueError("content run not found")
        validate_transition("content_run", current.status, "REVIEW")
        now = _now()
        with self._connection:
            cursor = self._connection.execute(
                """
                UPDATE content_runs
                SET status = 'REVIEW', result_json = ?, updated_at = ?
                WHERE run_id = ?
                """,
                (json.dumps(result, ensure_ascii=False), now, run_id),
            )
        if cursor.rowcount != 1:
            raise ValueError("content run not found")
        run = self.get(run_id)
        assert run is not None
        return run

    def save_result_preserving_status(self, run_id: str, result: dict[str, object]) -> ContentRun:
        now = _now()
        with self._connection:
            cursor = self._connection.execute(
                """
                UPDATE content_runs
                SET result_json = ?, updated_at = ?
                WHERE run_id = ?
                """,
                (json.dumps(result, ensure_ascii=False), now, run_id),
            )
        if cursor.rowcount != 1:
            raise ValueError("content run not found")
        run = self.get(run_id)
        assert run is not None
        return run

    def save_production_result(self, run_id: str, result: dict[str, object]) -> ContentRun:
        current = self.get(run_id)
        if current is None:
            raise ValueError("content run not found")
        validate_transition("content_run", current.status, "PRODUCING")
        now = _now()
        with self._connection:
            cursor = self._connection.execute(
                """
                UPDATE content_runs
                SET status = 'PRODUCING', result_json = ?, updated_at = ?
                WHERE run_id = ?
                """,
                (json.dumps(result, ensure_ascii=False), now, run_id),
            )
        if cursor.rowcount != 1:
            raise ValueError("content run not found")
        run = self.get(run_id)
        assert run is not None
        return run

    def approve(self, run_id: str, *, decision_ref: str) -> ContentRun:
        current = self.get(run_id)
        if current is None:
            raise ValueError("content run not found")
        validate_transition("content_run", current.status, "APPROVED")
        decision_ref = decision_ref.strip()
        if not decision_ref:
            raise ValueError("decision_ref is required")
        now = _now()
        with self._connection:
            cursor = self._connection.execute(
                """
                UPDATE content_runs
                SET status = 'APPROVED', result_json = ?, updated_at = ?
                WHERE run_id = ? AND status = 'REVIEW'
                """,
                (
                    json.dumps(
                        {
                            **((self.get(run_id) or ContentRun("", "", "", "", "", (), (), "", None, None, "", "")).result or {}),
                            "approval": {
                                "status": "APPROVED",
                                "decision_ref": decision_ref,
                                "approved_at": now,
                            },
                        },
                        ensure_ascii=False,
                    ),
                    now,
                    run_id,
                ),
            )
        if cursor.rowcount != 1:
            run = self.get(run_id)
            if run is None:
                raise ValueError("content run not found")
            raise ValueError(f"content run cannot be approved from status {run.status}")
        run = self.get(run_id)
        assert run is not None
        return run

    def mark_published(self, run_id: str, publication: dict[str, object], result: dict[str, object] | None = None) -> ContentRun:
        publication_status = str(publication.get("status") or "").strip()
        if publication_status != "PUBLISHED":
            raise InvalidStateTransition("content run can become PUBLISHED only after publication is PUBLISHED")
        if not str(publication.get("external_id") or "").strip():
            raise InvalidStateTransition("published publication requires external_id")
        current = self.get(run_id)
        if current is None:
            raise ValueError("content run not found")
        validate_transition("content_run", current.status, "PUBLISHED")
        now = _now()
        with self._connection:
            cursor = self._connection.execute(
                """
                UPDATE content_runs
                SET status = 'PUBLISHED', result_json = ?, updated_at = ?
                WHERE run_id = ? AND status IN ('APPROVED', 'EXPORTED')
                """,
                (
                    json.dumps(
                        {
                            **((self.get(run_id) or ContentRun("", "", "", "", "", (), (), "", None, None, "", None)).result or {}),
                            **(result or {}),
                            "publication": publication,
                        },
                        ensure_ascii=False,
                    ),
                    now,
                    run_id,
                ),
            )
        if cursor.rowcount != 1:
            run = self.get(run_id)
            if run is None:
                raise ValueError("content run not found")
            raise ValueError(f"content run cannot be published from status {run.status}")
        run = self.get(run_id)
        assert run is not None
        return run

    def mark_exported(self, run_id: str, export: dict[str, object]) -> ContentRun:
        current = self.get(run_id)
        if current is None:
            raise ValueError("content run not found")
        validate_transition("content_run", current.status, "EXPORTED")
        now = _now()
        with self._connection:
            cursor = self._connection.execute(
                """
                UPDATE content_runs
                SET status = 'EXPORTED', result_json = ?, updated_at = ?
                WHERE run_id = ? AND status = 'APPROVED'
                """,
                (
                    json.dumps(
                        {
                            **((self.get(run_id) or ContentRun("", "", "", "", "", (), (), "", None, None, "", "")).result or {}),
                            "export": export,
                        },
                        ensure_ascii=False,
                    ),
                    now,
                    run_id,
                ),
            )
        if cursor.rowcount != 1:
            run = self.get(run_id)
            if run is None:
                raise ValueError("content run not found")
            raise ValueError(f"content run cannot be exported from status {run.status}")
        run = self.get(run_id)
        assert run is not None
        return run

    def mark_failed(self, run_id: str) -> ContentRun:
        current = self.get(run_id)
        if current is None:
            raise ValueError("content run not found")
        validate_transition("content_run", current.status, "FAILED")
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
            result=json.loads(row["result_json"]) if row["result_json"] else None,
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def close(self) -> None:
        self._connection.close()
