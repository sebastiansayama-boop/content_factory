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

from content_factory.state_machine import InvalidStateTransition, require_publication_parent, validate_transition


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
                artifact_ids_json TEXT NOT NULL DEFAULT '[]',
                destination TEXT,
                provenance_json TEXT NOT NULL DEFAULT '{}',
                published_at TEXT,
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

            CREATE TABLE IF NOT EXISTS experience_records (
                example_id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                prompt_json TEXT NOT NULL,
                context_json TEXT NOT NULL,
                generated_json TEXT NOT NULL,
                decision TEXT NOT NULL,
                final_json TEXT,
                edits_json TEXT NOT NULL,
                reason TEXT NOT NULL,
                qc_json TEXT NOT NULL,
                provenance_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_experience_records_run
                ON experience_records(run_id, created_at);
            
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
        existing_columns = {row["name"] for row in self.db.execute("PRAGMA table_info(publications)").fetchall()}
        migrations = {"artifact_ids_json": "ALTER TABLE publications ADD COLUMN artifact_ids_json TEXT NOT NULL DEFAULT '[]'", "destination": "ALTER TABLE publications ADD COLUMN destination TEXT", "provenance_json": "ALTER TABLE publications ADD COLUMN provenance_json TEXT NOT NULL DEFAULT '{}'", "published_at": "ALTER TABLE publications ADD COLUMN published_at TEXT"}
        with self.db:
            for column, statement in migrations.items():
                if column not in existing_columns: self.db.execute(statement)
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

    def record_experience(
        self,
        *,
        run_id: str,
        prompt: dict[str, Any] | str,
        context: dict[str, Any] | None = None,
        generated: dict[str, Any] | str,
        decision: str,
        final: dict[str, Any] | str | None = None,
        edits: list[dict[str, Any]] | None = None,
        reason: str = "",
        qc: dict[str, Any] | None = None,
        provenance: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        decision = decision.strip().upper()
        if decision not in {"ACCEPT", "EDIT", "REGENERATE", "REJECT"}:
            raise ValueError("experience decision must be ACCEPT, EDIT, REGENERATE, or REJECT")
        if not run_id.strip():
            raise ValueError("run_id is required")
        example_id = f"ex-{uuid4()}"
        now = _now()
        record = {
            "example_id": example_id,
            "run_id": run_id,
            "prompt": prompt,
            "context": context or {},
            "generated": generated,
            "decision": decision,
            "final": final,
            "edits": edits or [],
            "reason": reason.strip(),
            "qc": qc or {},
            "provenance": provenance or {"run_id": run_id},
            "created_at": now,
        }
        with self.db:
            self.db.execute(
                """INSERT INTO experience_records
                (example_id, run_id, prompt_json, context_json, generated_json, decision,
                 final_json, edits_json, reason, qc_json, provenance_json, created_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    example_id, run_id, _json(prompt), _json(record["context"]),
                    _json(generated), decision,
                    _json(final) if final is not None else None,
                    _json(record["edits"]), record["reason"], _json(record["qc"]),
                    _json(record["provenance"]), now,
                ),
            )
        return record

    def list_experiences(self, run_id: str | None = None) -> list[dict[str, Any]]:
        if run_id:
            rows = self.db.execute(
                "SELECT * FROM experience_records WHERE run_id=? ORDER BY created_at, rowid",
                (run_id,),
            ).fetchall()
        else:
            rows = self.db.execute(
                "SELECT * FROM experience_records ORDER BY created_at, rowid"
            ).fetchall()
        return [
            {
                "example_id": row["example_id"],
                "run_id": row["run_id"],
                "prompt": json.loads(row["prompt_json"]),
                "context": json.loads(row["context_json"]),
                "generated": json.loads(row["generated_json"]),
                "decision": row["decision"],
                "final": json.loads(row["final_json"]) if row["final_json"] else None,
                "edits": json.loads(row["edits_json"]),
                "reason": row["reason"],
                "qc": json.loads(row["qc_json"]),
                "provenance": json.loads(row["provenance_json"]),
                "created_at": row["created_at"],
            }
            for row in rows
        ]



    def retrieve_experiences(
        self,
        *,
        topic: str,
        platform: str | None = None,
        limit: int = 3,
    ) -> list[dict[str, Any]]:
        """Return a small deterministic set of relevant prior content experiences."""
        topic_norm = " ".join(str(topic or "").casefold().split())
        platform_norm = str(platform or "").strip().casefold()
        if not topic_norm or limit <= 0:
            return []
        rows = self.db.execute(
            "SELECT * FROM experience_records ORDER BY created_at DESC, rowid DESC"
        ).fetchall()
        matches: list[dict[str, Any]] = []
        for row in rows:
            prompt = json.loads(row["prompt_json"])
            context = json.loads(row["context_json"])
            prompt_text = " ".join(
                str(prompt.get(key) or "") for key in ("brief", "title")
            ).casefold()
            if topic_norm not in prompt_text:
                continue
            if platform_norm and str(context.get("platform") or "").strip().casefold() != platform_norm:
                continue
            matches.append({
                "example_id": row["example_id"],
                "run_id": row["run_id"],
                "decision": row["decision"],
                "generated": json.loads(row["generated_json"]),
                "final": json.loads(row["final_json"]) if row["final_json"] else None,
                "reason": row["reason"],
                "qc": json.loads(row["qc_json"]),
                "created_at": row["created_at"],
            })
            if len(matches) >= min(limit, 3):
                break
        return matches

    def prepare_publication(
        self, run_id: str, channel: str, content_ref: str, payload: dict[str, Any], *, record_event: bool = True
    ) -> dict[str, Any]:
        now = _now()
        publication_id = f"pub-{uuid4()}"
        artifact_ids = list(dict.fromkeys(str(ref) for ref in payload.get("artifact_ids", []) if str(ref).strip()))
        destination = str(payload.get("destination") or "").strip() or None
        provenance = payload.get("provenance") if isinstance(payload.get("provenance"), dict) else {}
        with self.db:
            existing = self.db.execute("SELECT * FROM publications WHERE run_id=? AND channel=? AND content_ref=?", (run_id, channel, content_ref)).fetchone()
            if existing: return dict(existing)
            self.db.execute("INSERT INTO publications (publication_id,run_id,channel,status,content_ref,external_id,external_url,response_json,artifact_ids_json,destination,provenance_json,published_at,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (publication_id,run_id,channel,"PREPARED",content_ref,None,None,_json(payload),_json(artifact_ids),destination,_json(provenance),None,now,now))
        if record_event: self.record(run_id, "publication.prepared", output_refs=(publication_id, channel))
        publication = dict(self.db.execute("SELECT * FROM publications WHERE publication_id=?", (publication_id,)).fetchone())
        response = json.loads(publication.get("response_json") or "{}")
        if isinstance(response, dict):
            publication.update({key: response[key] for key in ("text", "media", "title", "output", "destination") if key in response})
        return publication

    def publish(self, publication_id: str, *, run_status: str, url: str | None = None, token: str | None = None, publisher: Any | None = None) -> dict[str, Any]:
        row = self.db.execute("SELECT * FROM publications WHERE publication_id=?", (publication_id,)).fetchone()
        if not row: raise ValueError("publication not found")
        if row["status"] == "PUBLISHED":
            published = dict(row)
            published["response"] = json.loads(published["response_json"])
            return published
        if row["status"] != "PREPARED":
            raise InvalidStateTransition(
                f"publication cannot be published from status {row['status']}"
            )
        require_publication_parent(run_status, row["status"], "PUBLISHING")
        now = _now()
        with self.db:
            cursor = self.db.execute(
                "UPDATE publications SET status='PUBLISHING', updated_at=? "
                "WHERE publication_id=? AND status='PREPARED'",
                (now, publication_id),
            )
        if cursor.rowcount != 1:
            raise InvalidStateTransition("publication was changed by another execution")
        payload = json.loads(row["response_json"])
        external_id, external_url = f"local-{publication_id}", None
        response: dict[str, Any] = {"mode":"local", "channel":row["channel"]}
        published_at = _now()
        try:
            if publisher is not None:
                result = publisher.publish(payload, publication_id=publication_id)
                if not isinstance(result, dict):
                    raise ValueError("publisher must return an object")
                response = result.get("response") if isinstance(result.get("response"), dict) else result
                external_id = str(result.get("external_id") or publication_id)
                external_url = result.get("external_url")
                published_at = str(result.get("published_at") or "").strip() or _now()
            elif url:
                body = _json({
                    "publication_id": publication_id,
                    "channel": row["channel"],
                    "content_ref": row["content_ref"],
                    "content": payload,
                }).encode()
                headers = {"Content-Type": "application/json", "Idempotency-Key": publication_id}
                if token:
                    headers["Authorization"] = f"Bearer {token}"
                request = urllib.request.Request(url, data=body, headers=headers, method="POST")
                with urllib.request.urlopen(request, timeout=30) as result:
                    raw = result.read(8192).decode("utf-8", errors="replace")
                    status_code = int(result.status)
                if not 200 <= status_code < 300:
                    raise ValueError(f"publication endpoint returned HTTP {status_code}")
                response = {"mode": "webhook", "http_status": status_code, "body": raw[:4000]}
                external_id = publication_id
                external_url = url
        except Exception as exc:
            with self.db:
                self.db.execute(
                    "UPDATE publications SET status='UNKNOWN', response_json=?, updated_at=? "
                    "WHERE publication_id=? AND status='PUBLISHING'",
                    (_json({"mode": "unknown", "error": str(exc)[:1000]}), _now(), publication_id),
                )
            self.record(
                row["run_id"],
                "publication.unknown",
                status="UNKNOWN",
                output_refs=(publication_id,),
                evidence={"error_type": type(exc).__name__},
            )
            raise
        validate_transition("publication", "PUBLISHING", "PUBLISHED")
        if not external_id.strip():
            raise InvalidStateTransition("published publication requires external_id")
        with self.db:
            self.db.execute(
                "UPDATE publications SET status='PUBLISHED', external_id=?, external_url=?, "
                "response_json=?, published_at=?, updated_at=? "
                "WHERE publication_id=? AND status='PUBLISHING'",
                (external_id, external_url, _json(response), published_at, _now(), publication_id),
            )
        self.record(row["run_id"], "publication.published", output_refs=(publication_id,external_id), evidence=response)
        published = dict(self.db.execute("SELECT * FROM publications WHERE publication_id=?", (publication_id,)).fetchone())
        published["response"] = response
        return published
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
        self,
        run: dict[str, Any],
        *,
        changed_claim_ids: list[str],
        content_brief: dict[str, Any],
        content_brief_revision_id: str,
        changes: dict[str, Any] | None = None,
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
        brief_id = str(content_brief.get("brief_id") or "").strip()
        if not brief_id or not content_brief_revision_id.strip():
            raise ValueError("replay requires a durable content brief revision")
        return {
            "run_id": run["run_id"],
            "mode": "INCREMENTAL_REPLAY",
            "content_brief_id": brief_id,
            "content_brief_revision_id": content_brief_revision_id,
            "content_brief": content_brief,
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
