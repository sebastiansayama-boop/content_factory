from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class PersistedWorkItem:
    work_item_id: str
    operation_id: str
    revision_id: str
    state: str


class RuntimeStore:
    """Durable control state, execution projections, and event journal."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(self.path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._connection.execute("PRAGMA journal_mode = WAL")
        self._connection.execute("PRAGMA synchronous = FULL")
        self._initialize()

    def _initialize(self) -> None:
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS work_items (
                work_item_id TEXT PRIMARY KEY,
                operation_id TEXT,
                revision_id TEXT NOT NULL,
                state TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS events (
                event_id TEXT PRIMARY KEY,
                work_item_id TEXT NOT NULL,
                revision_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                state TEXT NOT NULL,
                operation TEXT NOT NULL,
                actor TEXT NOT NULL,
                data_json TEXT NOT NULL,
                FOREIGN KEY(work_item_id) REFERENCES work_items(work_item_id)
            );

            CREATE TABLE IF NOT EXISTS execution_attempts (
                attempt_id TEXT PRIMARY KEY,
                work_item_id TEXT NOT NULL,
                operation_id TEXT NOT NULL,
                execution_id TEXT NOT NULL,
                attempt_no INTEGER NOT NULL,
                status TEXT NOT NULL,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                error TEXT,
                FOREIGN KEY(work_item_id) REFERENCES work_items(work_item_id)
            );

            CREATE TABLE IF NOT EXISTS runtime_records (
                work_item_id TEXT NOT NULL,
                record_type TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                PRIMARY KEY(work_item_id, record_type),
                FOREIGN KEY(work_item_id) REFERENCES work_items(work_item_id)
            );

            CREATE TABLE IF NOT EXISTS publication_reservations (
                work_item_id TEXT PRIMARY KEY,
                publication_id TEXT NOT NULL,
                FOREIGN KEY(work_item_id) REFERENCES work_items(work_item_id)
            );

            CREATE INDEX IF NOT EXISTS idx_events_work_item
                ON events(work_item_id, timestamp, event_id);
            CREATE INDEX IF NOT EXISTS idx_attempts_work_item
                ON execution_attempts(work_item_id, attempt_no);
            """
        )
        columns = {row["name"] for row in self._connection.execute("PRAGMA table_info(work_items)").fetchall()}
        if "operation_id" not in columns:
            self._connection.execute("ALTER TABLE work_items ADD COLUMN operation_id TEXT")
        self._connection.execute(
            """
            UPDATE work_items
            SET operation_id = COALESCE(operation_id, 'op-recovered:' || work_item_id)
            WHERE operation_id IS NULL
            """
        )
        self._connection.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_work_items_operation_id ON work_items(operation_id)")
        self._connection.commit()

    def create_work_item(
        self,
        *,
        work_item_id: str,
        operation_id: str,
        revision_id: str,
        state: str,
        updated_at: str,
        event: dict[str, Any],
    ) -> None:
        with self._connection:
            self._connection.execute(
                """
                INSERT INTO work_items(work_item_id, operation_id, revision_id, state, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (work_item_id, operation_id, revision_id, state, updated_at),
            )
            self._insert_event(event)

    def transition(
        self,
        *,
        work_item_id: str,
        operation_id: str,
        revision_id: str,
        state: str,
        updated_at: str,
        event: dict[str, Any],
    ) -> None:
        with self._connection:
            cursor = self._connection.execute(
                """
                UPDATE work_items
                SET operation_id = ?, revision_id = ?, state = ?, updated_at = ?
                WHERE work_item_id = ?
                """,
                (operation_id, revision_id, state, updated_at, work_item_id),
            )
            if cursor.rowcount != 1:
                raise KeyError(f"unknown work item: {work_item_id}")
            self._insert_event(event)

    def _insert_event(self, event: dict[str, Any]) -> None:
        self._connection.execute(
            """
            INSERT INTO events(
                event_id, work_item_id, revision_id, timestamp,
                state, operation, actor, data_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event["event_id"],
                event["work_item_id"],
                event["revision_id"],
                event["timestamp"],
                event["state"],
                event["operation"],
                event["actor"],
                json.dumps(event.get("data", {}), sort_keys=True),
            ),
        )

    def start_attempt(
        self,
        *,
        attempt_id: str,
        work_item_id: str,
        operation_id: str,
        execution_id: str,
        attempt_no: int,
        started_at: str,
    ) -> None:
        with self._connection:
            self._connection.execute(
                """
                INSERT INTO execution_attempts(
                    attempt_id, work_item_id, operation_id, execution_id,
                    attempt_no, status, started_at
                ) VALUES (?, ?, ?, ?, ?, 'RUNNING', ?)
                """,
                (attempt_id, work_item_id, operation_id, execution_id, attempt_no, started_at),
            )

    def finish_attempt(
        self,
        attempt_id: str,
        *,
        status: str,
        completed_at: str,
        error: str | None = None,
    ) -> None:
        if status not in {"SUCCEEDED", "FAILED", "UNKNOWN", "CANCELLED"}:
            raise ValueError(f"unsupported attempt status: {status}")
        with self._connection:
            cursor = self._connection.execute(
                """
                UPDATE execution_attempts
                SET status = ?, completed_at = ?, error = ?
                WHERE attempt_id = ?
                """,
                (status, completed_at, error, attempt_id),
            )
            if cursor.rowcount != 1:
                raise KeyError(f"unknown attempt: {attempt_id}")

    def mark_running_attempts_unknown(self, completed_at: str) -> int:
        with self._connection:
            cursor = self._connection.execute(
                """
                UPDATE execution_attempts
                SET status = 'UNKNOWN', completed_at = ?, error = COALESCE(error, 'runtime restarted while attempt was RUNNING')
                WHERE status = 'RUNNING'
                """,
                (completed_at,),
            )
            return cursor.rowcount

    def load_attempts(self, work_item_id: str) -> list[dict[str, Any]]:
        rows = self._connection.execute(
            """
            SELECT attempt_id, operation_id, execution_id, attempt_no,
                   status, started_at, completed_at, error
            FROM execution_attempts
            WHERE work_item_id = ?
            ORDER BY attempt_no, attempt_id
            """,
            (work_item_id,),
        ).fetchall()
        return [dict(row) for row in rows]

    def save_record(self, work_item_id: str, record_type: str, payload: dict[str, Any]) -> None:
        with self._connection:
            self._connection.execute(
                """
                INSERT INTO runtime_records(work_item_id, record_type, payload_json)
                VALUES (?, ?, ?)
                ON CONFLICT(work_item_id, record_type)
                DO UPDATE SET payload_json = excluded.payload_json
                """,
                (work_item_id, record_type, json.dumps(payload, ensure_ascii=False, sort_keys=True)),
            )

    def load_record(self, work_item_id: str, record_type: str) -> dict[str, Any] | None:
        row = self._connection.execute(
            """
            SELECT payload_json
            FROM runtime_records
            WHERE work_item_id = ? AND record_type = ?
            """,
            (work_item_id, record_type),
        ).fetchone()
        if row is None:
            return None
        return json.loads(row["payload_json"])

    def reserve_publication_id(self, work_item_id: str, publication_id: str) -> str:
        with self._connection:
            row = self._connection.execute(
                "SELECT publication_id FROM publication_reservations WHERE work_item_id = ?",
                (work_item_id,),
            ).fetchone()
            if row is not None:
                return str(row["publication_id"])
            self._connection.execute(
                "INSERT INTO publication_reservations(work_item_id, publication_id) VALUES (?, ?)",
                (work_item_id, publication_id),
            )
            return publication_id

    def load_work_items(self) -> list[PersistedWorkItem]:
        rows = self._connection.execute(
            "SELECT work_item_id, operation_id, revision_id, state FROM work_items ORDER BY work_item_id"
        ).fetchall()
        return [
            PersistedWorkItem(
                row["work_item_id"],
                row["operation_id"],
                row["revision_id"],
                row["state"],
            )
            for row in rows
        ]

    def load_events(self, work_item_id: str | None = None) -> list[dict[str, Any]]:
        if work_item_id is None:
            rows = self._connection.execute(
                """
                SELECT event_id, work_item_id, revision_id, timestamp,
                       state, operation, actor, data_json
                FROM events
                ORDER BY timestamp, event_id
                """
            ).fetchall()
        else:
            rows = self._connection.execute(
                """
                SELECT event_id, work_item_id, revision_id, timestamp,
                       state, operation, actor, data_json
                FROM events
                WHERE work_item_id = ?
                ORDER BY timestamp, event_id
                """,
                (work_item_id,),
            ).fetchall()
        return [
            {
                "event_id": row["event_id"],
                "work_item_id": row["work_item_id"],
                "revision_id": row["revision_id"],
                "timestamp": row["timestamp"],
                "state": row["state"],
                "operation": row["operation"],
                "actor": row["actor"],
                "data": json.loads(row["data_json"]),
            }
            for row in rows
        ]

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> "RuntimeStore":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
