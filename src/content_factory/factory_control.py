from __future__ import annotations

import hashlib
import json
import sqlite3
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


@dataclass(frozen=True)
class FactoryEvent:
    event_id: str
    run_id: str
    event_type: str
    status: str
    actor: str
    input_refs: tuple[str, ...]
    output_refs: tuple[str, ...]
    evidence: dict[str, Any]
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["input_refs"] = list(self.input_refs)
        value["output_refs"] = list(self.output_refs)
        return value


class FactoryControlStore:
    """Durable timeline, distribution, observation, learning and replay state."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.executescript(
            """
            CREATE TABLE IF NOT EXISTS factory_events (
                event_id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                status TEXT NOT NULL,
                actor TEXT NOT NULL,
                input_refs_json TEXT NOT NULL,
                output_refs_json TEXT NOT NULL,
                evidence_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_factory_events_run
                ON factory_events(run_id, created_at);

            CREATE TABLE IF NOT EXISTS publications (
                publication_id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                channel TEXT NOT NULL,
                status TEXT NOT NULL,
                content_ref TEXT NOT NULL,
                external_id TEXT,
                external_url TEXT,
                response_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE UNIQUE INDEX IF NOT EXISTS idx_publication_idempotent
                ON publications(run_id, channel, content_ref);

            CREATE TABLE IF NOT EXISTS observations (
                observation_id TEXT PRIMARY KEY,
                publication_id TEXT NOT NULL,
                metrics_json TEXT NOT NULL,
                source TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS learning_candidates (
                learning_id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                observation_ids_json TEXT NOT NULL,
                hypothesis TEXT NOT NULL,
                proposed_changes_json TEXT NOT NULL,
                status TEXT NOT NULL,
                decision_ref TEXT,
                created_at TEXT NOT NULL,
                promoted_at TEXT
            );
            """
        )
        self.db.commit()

    def record(
        self,
        run_id: str,
        event_type: str,
        *,
        status: str = "COMPLETED",
        actor: str = "system",
        input_refs: tuple[str, ...] | list[str] = (),
        output_refs: tuple[str, ...] | list[str] = (),
        evidence: dict[str, Any] | None = None,
    ) -> FactoryEvent:
        event = FactoryEvent(
            event_id=f"evt-{uuid4()}",
            run_id=run_id,
            event_type=event_type,
            status=status,
            actor=actor,
            input_refs=tuple(input_refs),
            output_refs=tuple(output_refs),
            evidence=evidence or {},
            created_at=_now(),
        )
        with self.db:
            self.db.execute(
                "INSERT INTO factory_events VALUES (?,?,?,?,?,?,?,?,?)",
                (
                    event.event_id, event.run_id, event.event_type, event.status,
                    event.actor, _json(event.input_refs), _json(event.output_refs),
                    _json(event.evidence), event.created_at,
                ),
            )
        return event

    def timeline(self, run_id: str) -> list[FactoryEvent]:
        rows = self.db.execute(
            "SELECT * FROM factory_events WHERE run_id=? ORDER BY created_at, rowid",
            (run_id,),
        ).fetchall()
        return [
            FactoryEvent(
                event_id=row["event_id"],
                run_id=row["run_id"],
                event_type=row["event_type"],
                status=row["status"],
                actor=row["actor"],
                input_refs=tuple(json.loads(row["input_refs_json"])),
                output_refs=tuple(json.loads(row["output_refs_json"])),
                evidence=json.loads(row["evidence_json"]),
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def prepare_publication(
        self, run_id: str, channel: str, content_ref: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        now = _now()
        publication_id = f"pub-{uuid4()}"
        with self.db:
            existing = self.db.execute(
                "SELECT * FROM publications WHERE run_id=? AND channel=? AND content_ref=?",
                (run_id, channel, content_ref),
            ).fetchone()
            if existing:
                return dict(existing)
            self.db.execute(
                """INSERT INTO publications
                (publication_id,run_id,channel,status,content_ref,external_id,external_url,response_json,created_at,updated_at)
                VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (publication_id, run_id, channel, "PREPARED", content_ref, None, None,
                 _json(payload), now, now),
            )
        self.record(run_id, "publication.prepared", output_refs=(publication_id, channel))
        return dict(self.db.execute(
            "SELECT * FROM publications WHERE publication_id=?", (publication_id,)
        ).fetchone())

    def publish(self, publication_id: str, *, url: str | None = None, token: str | None = None) -> dict[str, Any]:
        row = self.db.execute(
            "SELECT * FROM publications WHERE publication_id=?", (publication_id,)
        ).fetchone()
        if not row:
            raise ValueError("publication not found")
        if row["status"] == "PUBLISHED":
            return dict(row)
        payload = json.loads(row["response_json"])
        channel = row["channel"]
        external_id = f"local-{publication_id}"
        external_url = None
        response: dict[str, Any] = {"mode": "local", "channel": channel}
        if url:
            body = _json({
                "publication_id": publication_id,
                "channel": channel,
                "content_ref": row["content_ref"],
                "content": payload,
            }).encode()
            headers = {"Content-Type": "application/json", "Idempotency-Key": publication_id}
            if token:
                headers["Authorization"] = f"Bearer {token}"
            request = urllib.request.Request(url, data=body, headers=headers, method="POST")
            try:
                with urllib.request.urlopen(request, timeout=30) as result:
                    raw = result.read(8192).decode("utf-8", errors="replace")
                    status_code = int(result.status)
            except urllib.error.HTTPError as exc:
                raise ValueError(f"publication endpoint returned HTTP {exc.code}") from exc
            except urllib.error.URLError as exc:
                raise ValueError(f"publication endpoint failed: {exc.reason}") from exc
            if not 200 <= status_code < 300:
                raise ValueError(f"publication endpoint returned HTTP {status_code}")
            response = {"mode": "webhook", "http_status": status_code, "body": raw[:4000]}
            external_id = publication_id
            external_url = url
        now = _now()
        with self.db:
            self.db.execute(
                """UPDATE publications SET status='PUBLISHED', external_id=?, external_url=?,
                response_json=?, updated_at=? WHERE publication_id=?""",
                (external_id, external_url, _json(response), now, publication_id),
            )
        run_id = row["run_id"]
        self.record(run_id, "publication.published", output_refs=(publication_id, external_id), evidence=response)
        return dict(self.db.execute(
            "SELECT * FROM publications WHERE publication_id=?", (publication_id,)
        ).fetchone())

    def list_publications(self, run_id: str) -> list[dict[str, Any]]:
        return [dict(row) for row in self.db.execute(
            "SELECT * FROM publications WHERE run_id=? ORDER BY created_at", (run_id,)
        ).fetchall()]

    def observe(self, publication_id: str, metrics: dict[str, Any], source: str = "api") -> dict[str, Any]:
        row = self.db.execute(
            "SELECT run_id FROM publications WHERE publication_id=?", (publication_id,)
        ).fetchone()
        if not row:
            raise ValueError("publication not found")
        observation_id = f"obs-{uuid4()}"
        created = _now()
        with self.db:
            self.db.execute(
                "INSERT INTO observations VALUES (?,?,?,?,?)",
                (observation_id, publication_id, _json(metrics), source, created),
            )
        self.record(row["run_id"], "observation.recorded", input_refs=(publication_id,),
                    output_refs=(observation_id,), evidence={"metrics": metrics, "source": source})
        return {
            "observation_id": observation_id,
            "publication_id": publication_id,
            "metrics": metrics,
            "source": source,
            "created_at": created,
        }

    def observations(self, run_id: str) -> list[dict[str, Any]]:
        rows = self.db.execute(
            """SELECT o.* FROM observations o JOIN publications p
               ON p.publication_id=o.publication_id WHERE p.run_id=? ORDER BY o.created_at""",
            (run_id,),
        ).fetchall()
        return [
            {
                "observation_id": r["observation_id"],
                "publication_id": r["publication_id"],
                "metrics": json.loads(r["metrics_json"]),
                "source": r["source"],
                "created_at": r["created_at"],
            } for r in rows
        ]

    def create_learning(
        self, run_id: str, observation_ids: list[str], hypothesis: str, proposed_changes: dict[str, Any]
    ) -> dict[str, Any]:
        if not hypothesis.strip():
            raise ValueError("hypothesis is required")
        learning_id = f"learn-{uuid4()}"
        now = _now()
        with self.db:
            self.db.execute(
                """INSERT INTO learning_candidates VALUES (?,?,?,?,?,?,?,?,?)""",
                (learning_id, run_id, _json(observation_ids), hypothesis.strip(),
                 _json(proposed_changes), "CANDIDATE", None, now, None),
            )
        self.record(run_id, "learning.candidate_created", input_refs=tuple(observation_ids),
                    output_refs=(learning_id,))
        return self.get_learning(learning_id)

    def get_learning(self, learning_id: str) -> dict[str, Any]:
        row = self.db.execute(
            "SELECT * FROM learning_candidates WHERE learning_id=?", (learning_id,)
        ).fetchone()
        if not row:
            raise ValueError("learning candidate not found")
        return {
            "learning_id": row["learning_id"], "run_id": row["run_id"],
            "observation_ids": json.loads(row["observation_ids_json"]),
            "hypothesis": row["hypothesis"],
            "proposed_changes": json.loads(row["proposed_changes_json"]),
            "status": row["status"], "decision_ref": row["decision_ref"],
            "created_at": row["created_at"], "promoted_at": row["promoted_at"],
        }

    def promote_learning(self, learning_id: str, decision_ref: str) -> dict[str, Any]:
        if not decision_ref.strip():
            raise ValueError("decision_ref is required")
        row = self.db.execute(
            "SELECT run_id,status FROM learning_candidates WHERE learning_id=?", (learning_id,)
        ).fetchone()
        if not row:
            raise ValueError("learning candidate not found")
        if row["status"] != "CANDIDATE":
            raise ValueError(f"learning candidate cannot be promoted from {row['status']}")
        promoted = _now()
        with self.db:
            self.db.execute(
                """UPDATE learning_candidates SET status='PROMOTED', decision_ref=?, promoted_at=?
                   WHERE learning_id=? AND status='CANDIDATE'""",
                (decision_ref.strip(), promoted, learning_id),
            )
        self.record(row["run_id"], "learning.promoted", input_refs=(learning_id,),
                    evidence={"decision_ref": decision_ref})
        return self.get_learning(learning_id)

    def replay_plan(
        self, run: dict[str, Any], *, changed_claim_ids: list[str], changes: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        result = run.get("result") or {}
        production = result.get("production") or {}
        assets = production.get("assets") or []
        changed = list(dict.fromkeys(changed_claim_ids))
        affected = [
            str(asset.get("asset_id"))
            for asset in assets
            if set(changed) & set(asset.get("claim_refs") or [])
        ]
        requested_changes = changes or {}
        return {
            "run_id": run["run_id"],
            "mode": "INCREMENTAL_REPLAY",
            "preserve": ["research", "knowledge", "editorial", "content_spec", "script"],
            "revise": ["content_spec.style_bible"] if requested_changes.get("style_bible") else [],
            "regenerate_asset_ids": affected,
            "retain_asset_ids": [
                str(asset.get("asset_id")) for asset in assets
                if str(asset.get("asset_id")) not in set(affected)
            ],
            "rerun": ["production", "assembly", "qc", "approval", "export"],
            "changed_claim_ids": changed,
            "changes": requested_changes,
        }

    def close(self) -> None:
        self.db.close()
