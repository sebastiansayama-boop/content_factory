from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class PersistedWorkItem:
    work_item_id: str
    revision_id: str
    state: str


class RuntimeStore:
    """Durable control-state store for the bounded factory runtime.

    The store keeps control state and the append-only event journal together
    in one SQLite transaction. It is deliberately separate from ArtifactStore:
    this is recovery state, not a repository evidence projection.
    """

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(self.path)
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

            CREATE INDEX IF NOT EXISTS idx_events_work_item
                ON events(work_item_id, timestamp, event_id);
            """
        )
        self._connection.commit()

    def create_work_item(
        self,
        *,
        work_item_id: str,
        revision_id: str,
        state: str,
        updated_at: str,
        event: dict[str, Any],
    ) -> None:
        with self._connection:
            self._connection.execute(
                """
                INSERT INTO work_items(work_item_id, revision_id, state, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                (work_item_id, revision_id, state, updated_at),
            )
            self._insert_event(event)

    def transition(
        self,
        *,
        work_item_id: str,
        revision_id: str,
        state: str,
        updated_at: str,
        event: dict[str, Any],
    ) -> None:
        with self._connection:
            cursor = self._connection.execute(
                """
                UPDATE work_items
                SET revision_id = ?, state = ?, updated_at = ?
                WHERE work_item_id = ?
                """,
                (revision_id, state, updated_at, work_item_id),
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

    def load_work_items(self) -> list[PersistedWorkItem]:
        rows = self._connection.execute(
            "SELECT work_item_id, revision_id, state FROM work_items ORDER BY work_item_id"
        ).fetchall()
        return [PersistedWorkItem(row["work_item_id"], row["revision_id"], row["state"]) for row in rows]

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
