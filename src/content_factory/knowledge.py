from __future__ import annotations

import json
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _tokens(value: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[\w-]{3,}", value.lower())
        if token not in {"the", "and", "for", "with", "that", "this", "from"}
    }


@dataclass(frozen=True)
class KnowledgeSource:
    source_id: str
    title: str
    url: str
    first_seen_at: str


@dataclass(frozen=True)
class KnowledgeClaim:
    claim_id: str
    text: str
    confidence: str
    status: str
    revision_id: str
    scope: str
    known_unknowns: tuple[str, ...]
    source_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    first_seen_at: str


@dataclass(frozen=True)
class KnowledgeAngle:
    angle_id: str
    text: str
    status: str
    first_seen_at: str


class KnowledgeStore:
    """Durable research/knowledge index with an explicit promotion boundary.

    Research capture creates candidates. Only explicitly promoted candidates
    are eligible for retrieval as reusable knowledge.
    """

    CANDIDATE = "CANDIDATE"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(self.path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA journal_mode = WAL")
        self._connection.execute("PRAGMA synchronous = FULL")
        self._initialize()

    def _initialize(self) -> None:
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS knowledge_sources (
                source_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                first_seen_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS knowledge_evidence (
                evidence_id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                excerpt TEXT NOT NULL,
                locator TEXT NOT NULL,
                provenance TEXT NOT NULL,
                first_seen_at TEXT NOT NULL,
                FOREIGN KEY (source_id) REFERENCES knowledge_sources(source_id)
            );
            CREATE TABLE IF NOT EXISTS knowledge_claims (
                claim_id TEXT PRIMARY KEY,
                text TEXT NOT NULL UNIQUE,
                confidence TEXT NOT NULL,
                status TEXT NOT NULL,
                revision_id TEXT NOT NULL,
                scope TEXT NOT NULL,
                known_unknowns_json TEXT NOT NULL,
                first_seen_at TEXT NOT NULL,
                decision_ref TEXT,
                promoted_at TEXT
            );
            CREATE TABLE IF NOT EXISTS knowledge_claim_sources (
                claim_id TEXT NOT NULL,
                source_id TEXT NOT NULL,
                PRIMARY KEY (claim_id, source_id),
                FOREIGN KEY (claim_id) REFERENCES knowledge_claims(claim_id),
                FOREIGN KEY (source_id) REFERENCES knowledge_sources(source_id)
            );
            CREATE TABLE IF NOT EXISTS knowledge_claim_evidence (
                claim_id TEXT NOT NULL,
                evidence_id TEXT NOT NULL,
                PRIMARY KEY (claim_id, evidence_id),
                FOREIGN KEY (claim_id) REFERENCES knowledge_claims(claim_id),
                FOREIGN KEY (evidence_id) REFERENCES knowledge_evidence(evidence_id)
            );
            CREATE TABLE IF NOT EXISTS knowledge_claim_runs (
                claim_id TEXT NOT NULL,
                run_id TEXT NOT NULL,
                PRIMARY KEY (claim_id, run_id),
                FOREIGN KEY (claim_id) REFERENCES knowledge_claims(claim_id)
            );
            CREATE TABLE IF NOT EXISTS knowledge_angles (
                angle_id TEXT PRIMARY KEY,
                text TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL,
                first_seen_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS knowledge_runs (
                run_id TEXT PRIMARY KEY,
                captured_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_knowledge_claims_status
                ON knowledge_claims(status);
            CREATE INDEX IF NOT EXISTS idx_knowledge_angles_status
                ON knowledge_angles(status);
            """
        )
        self._connection.commit()

    def capture(self, *, run_id: str, research: dict[str, Any]) -> dict[str, int]:
        """Capture research as candidates; never promote it implicitly."""
        claims = research.get("claims")
        sources = research.get("sources")
        evidence = research.get("evidence", [])
        angles = research.get("editorial_angles", [])
        if not isinstance(claims, list) or not isinstance(sources, list):
            raise ValueError("research claims and sources must be arrays")
        if not isinstance(evidence, list) or not isinstance(angles, list):
            raise ValueError("research evidence and editorial_angles must be arrays")

        source_map: dict[str, str] = {}
        evidence_map: dict[str, str] = {}
        source_count = evidence_count = claim_count = angle_count = 0

        with self._connection:
            for source in sources:
                if not isinstance(source, dict):
                    raise ValueError("research source must be an object")
                source_id = str(source.get("id") or "").strip()
                title = str(source.get("title") or "").strip()
                url = str(source.get("url") or "").strip()
                if not source_id or not title or not url:
                    raise ValueError("every research source requires id, title, and url")
                existing = self._connection.execute(
                    "SELECT source_id FROM knowledge_sources WHERE url = ?", (url,)
                ).fetchone()
                if existing:
                    stable_id = str(existing["source_id"])
                else:
                    stable_id = f"ks-{uuid4().hex[:16]}"
                    self._connection.execute(
                        "INSERT INTO knowledge_sources(source_id,title,url,first_seen_at) VALUES(?,?,?,?)",
                        (stable_id, title, url, _now()),
                    )
                    source_count += 1
                source_map[source_id] = stable_id

            for item in evidence:
                if not isinstance(item, dict):
                    raise ValueError("research evidence must be an object")
                evidence_id = str(item.get("id") or "").strip()
                source_id = str(item.get("source_id") or "").strip()
                excerpt = str(item.get("excerpt") or "").strip()
                locator = str(item.get("locator") or "").strip()
                provenance = str(item.get("provenance") or "").strip()
                if not evidence_id or source_id not in source_map or not excerpt:
                    raise ValueError("every evidence item requires id, valid source_id, and excerpt")
                stable_source_id = source_map[source_id]
                existing = self._connection.execute(
                    """SELECT e.evidence_id FROM knowledge_evidence e
                    JOIN knowledge_sources s ON s.source_id=e.source_id
                    WHERE s.url=? AND e.excerpt=? AND e.locator=?""",
                    (str(sources[[s.get("id") for s in sources].index(source_id)].get("url") or ""), excerpt, locator),
                ).fetchone()
                if existing:
                    stable_evidence_id = str(existing["evidence_id"])
                else:
                    stable_evidence_id = f"ke-{uuid4().hex[:16]}"
                    self._connection.execute(
                        """
                        INSERT INTO knowledge_evidence(
                            evidence_id,source_id,excerpt,locator,provenance,first_seen_at
                        ) VALUES(?,?,?,?,?,?)
                        """,
                        (
                            stable_evidence_id,
                            stable_source_id,
                            excerpt,
                            locator,
                            provenance,
                            _now(),
                        ),
                    )
                    evidence_count += 1
                evidence_map[evidence_id] = stable_evidence_id

            for claim in claims:
                if not isinstance(claim, dict):
                    raise ValueError("research claim must be an object")
                text = str(claim.get("text") or "").strip()
                confidence = str(claim.get("confidence") or "low").strip().lower()
                source_refs = claim.get("source_ids")
                evidence_refs = claim.get("evidence_ids", [])
                scope = str(claim.get("scope") or "").strip()
                unknowns = claim.get("known_unknowns", [])
                if not text or confidence not in {"high", "medium", "low"}:
                    raise ValueError("every research claim requires text and valid confidence")
                if not isinstance(source_refs, list) or not source_refs or not all(ref in source_map for ref in source_refs):
                    raise ValueError(f"claim {claim.get('id')} has invalid source_ids")
                if not isinstance(evidence_refs, list) or not evidence_refs or not all(ref in evidence_map for ref in evidence_refs):
                    raise ValueError(f"claim {claim.get('id')} has invalid evidence_ids")
                if not isinstance(unknowns, list) or not all(isinstance(value, str) for value in unknowns):
                    raise ValueError(f"claim {claim.get('id')} known_unknowns must be an array")

                existing = self._connection.execute(
                    "SELECT claim_id,revision_id FROM knowledge_claims WHERE text = ?", (text,)
                ).fetchone()
                if existing:
                    stable_claim_id = str(existing["claim_id"])
                else:
                    stable_claim_id = f"kc-{uuid4().hex[:16]}"
                    self._connection.execute(
                        """
                        INSERT INTO knowledge_claims(
                            claim_id,text,confidence,status,revision_id,scope,
                            known_unknowns_json,first_seen_at
                        ) VALUES(?,?,?,?,?,?,?,?)
                        """,
                        (
                            stable_claim_id,
                            text,
                            confidence,
                            self.CANDIDATE,
                            f"{stable_claim_id}-r1",
                            scope,
                            json.dumps(unknowns, ensure_ascii=False),
                            _now(),
                        ),
                    )
                    claim_count += 1
                for ref in source_refs:
                    self._connection.execute(
                        "INSERT OR IGNORE INTO knowledge_claim_sources(claim_id,source_id) VALUES(?,?)",
                        (stable_claim_id, source_map[ref]),
                    )
                for ref in evidence_refs:
                    self._connection.execute(
                        "INSERT OR IGNORE INTO knowledge_claim_evidence(claim_id,evidence_id) VALUES(?,?)",
                        (stable_claim_id, evidence_map[ref]),
                    )
                self._connection.execute(
                    "INSERT OR IGNORE INTO knowledge_claim_runs(claim_id,run_id) VALUES(?,?)",
                    (stable_claim_id, run_id),
                )

            for angle in angles:
                if not isinstance(angle, str) or not angle.strip():
                    continue
                cursor = self._connection.execute(
                    "INSERT OR IGNORE INTO knowledge_angles(angle_id,text,status,first_seen_at) VALUES(?,?,?,?)",
                    (f"ka-{uuid4().hex[:16]}", angle.strip(), self.CANDIDATE, _now()),
                )
                if cursor.rowcount == 1:
                    angle_count += 1

            self._connection.execute(
                "INSERT OR REPLACE INTO knowledge_runs(run_id,captured_at) VALUES(?,?)",
                (run_id, _now()),
            )

        return {
            "sources_added": source_count,
            "evidence_added": evidence_count,
            "claims_added": claim_count,
            "angles_added": angle_count,
        }

    def resolve_research_refs(self, research: dict[str, Any]) -> dict[str, dict[str, str]]:
        """Resolve ephemeral research IDs to durable knowledge IDs."""
        claims = research.get("claims", [])
        sources = research.get("sources", [])
        evidence = research.get("evidence", [])
        if not isinstance(claims, list) or not isinstance(sources, list) or not isinstance(evidence, list):
            raise ValueError("research claims, sources and evidence must be arrays")

        source_rows = {
            str(row["url"]): str(row["source_id"])
            for row in self._connection.execute("SELECT source_id,url FROM knowledge_sources")
        }
        evidence_rows = {
            (str(row["source_url"]), str(row["excerpt"]), str(row["locator"])): str(row["evidence_id"])
            for row in self._connection.execute(
                """SELECT e.evidence_id,s.url AS source_url,e.excerpt,e.locator
                   FROM knowledge_evidence e JOIN knowledge_sources s ON s.source_id=e.source_id"""
            )
        }
        claim_rows = {
            str(row["text"]): str(row["claim_id"])
            for row in self._connection.execute("SELECT claim_id,text FROM knowledge_claims")
        }

        result: dict[str, dict[str, str]] = {"claims": {}, "sources": {}, "evidence": {}}
        for source in sources:
            if not isinstance(source, dict):
                continue
            local_id = str(source.get("id") or "").strip()
            url = str(source.get("url") or "").strip()
            if local_id and url in source_rows:
                result["sources"][local_id] = source_rows[url]
        source_urls = {
            str(source.get("id")): str(source.get("url"))
            for source in sources if isinstance(source, dict)
        }
        for item in evidence:
            if not isinstance(item, dict):
                continue
            local_id = str(item.get("id") or "").strip()
            source_url = source_urls.get(str(item.get("source_id")), "")
            key = (source_url, str(item.get("excerpt") or "").strip(), str(item.get("locator") or "").strip())
            if local_id and key in evidence_rows:
                result["evidence"][local_id] = evidence_rows[key]
        for claim in claims:
            if not isinstance(claim, dict):
                continue
            local_id = str(claim.get("id") or "").strip()
            claim_text = str(claim.get("text") or "").strip()
            if local_id and claim_text in claim_rows:
                result["claims"][local_id] = claim_rows[claim_text]
        return result

    def promote_claim(self, claim_id: str, *, decision_ref: str) -> KnowledgeClaim:
        if not decision_ref.strip():
            raise ValueError("decision_ref must not be empty")
        row = self._connection.execute(
            "SELECT * FROM knowledge_claims WHERE claim_id = ?", (claim_id,)
        ).fetchone()
        if row is None:
            raise ValueError("knowledge claim not found")
        if row["status"] != self.CANDIDATE:
            raise ValueError(f"knowledge claim cannot be promoted from status {row['status']}")
        evidence = self._connection.execute(
            "SELECT 1 FROM knowledge_claim_evidence WHERE claim_id = ? LIMIT 1",
            (claim_id,),
        ).fetchone()
        if evidence is None:
            raise ValueError("knowledge claim cannot be promoted without evidence")
        now = _now()
        with self._connection:
            self._connection.execute(
                """
                UPDATE knowledge_claims
                SET status=?, decision_ref=?, promoted_at=?
                WHERE claim_id=?
                """,
                (self.ACCEPTED, decision_ref.strip(), now, claim_id),
            )
        result = self.get_claim(claim_id)
        assert result is not None
        return result

    def get_claim(self, claim_id: str) -> KnowledgeClaim | None:
        row = self._connection.execute(
            "SELECT * FROM knowledge_claims WHERE claim_id = ?", (claim_id,)
        ).fetchone()
        if row is None:
            return None
        source_rows = self._connection.execute(
            "SELECT source_id FROM knowledge_claim_sources WHERE claim_id=? ORDER BY source_id",
            (claim_id,),
        ).fetchall()
        evidence_rows = self._connection.execute(
            "SELECT evidence_id FROM knowledge_claim_evidence WHERE claim_id=? ORDER BY evidence_id",
            (claim_id,),
        ).fetchall()
        return KnowledgeClaim(
            claim_id=row["claim_id"],
            text=row["text"],
            confidence=row["confidence"],
            status=row["status"],
            revision_id=row["revision_id"],
            scope=row["scope"],
            known_unknowns=tuple(json.loads(row["known_unknowns_json"])),
            source_ids=tuple(str(item["source_id"]) for item in source_rows),
            evidence_ids=tuple(str(item["evidence_id"]) for item in evidence_rows),
            first_seen_at=row["first_seen_at"],
        )

    def search(self, query: str, *, limit: int = 8, include_candidates: bool = False) -> dict[str, list[dict[str, Any]]]:
        terms = _tokens(query)
        if not terms:
            return {"claims": [], "sources": [], "editorial_angles": []}

        statuses = (self.ACCEPTED, self.CANDIDATE) if include_candidates else (self.ACCEPTED,)
        placeholders = ",".join("?" for _ in statuses)
        claim_rows = self._connection.execute(
            f"SELECT claim_id,text,confidence,revision_id,scope,status FROM knowledge_claims WHERE status IN ({placeholders})",
            statuses,
        ).fetchall()
        scored_claims: list[tuple[int, sqlite3.Row]] = []
        for row in claim_rows:
            score = len(terms & _tokens(row["text"]))
            if score:
                scored_claims.append((score, row))
        scored_claims.sort(key=lambda item: (-item[0], item[1]["claim_id"]))

        claims: list[dict[str, Any]] = []
        source_ids: set[str] = set()
        for _, row in scored_claims[:limit]:
            refs = self._connection.execute(
                """
                SELECT s.source_id,s.title,s.url
                FROM knowledge_sources s
                JOIN knowledge_claim_sources cs ON cs.source_id=s.source_id
                WHERE cs.claim_id=?
                ORDER BY s.source_id
                """,
                (row["claim_id"],),
            ).fetchall()
            evidence_refs = self._connection.execute(
                "SELECT evidence_id FROM knowledge_claim_evidence WHERE claim_id=? ORDER BY evidence_id",
                (row["claim_id"],),
            ).fetchall()
            source_ids.update(str(ref["source_id"]) for ref in refs)
            claims.append({
                "claim_id": row["claim_id"],
                "text": row["text"],
                "confidence": row["confidence"],
                "revision_id": row["revision_id"],
                "scope": row["scope"],
                "status": row["status"],
                "source_ids": [ref["source_id"] for ref in refs],
                "evidence_ids": [ref["evidence_id"] for ref in evidence_refs],
            })

        sources = []
        if source_ids:
            placeholders = ",".join("?" for _ in source_ids)
            rows = self._connection.execute(
                f"SELECT source_id,title,url FROM knowledge_sources WHERE source_id IN ({placeholders})",
                tuple(sorted(source_ids)),
            ).fetchall()
            sources = [dict(row) for row in rows]

        angle_rows = self._connection.execute(
            "SELECT angle_id,text FROM knowledge_angles WHERE status=?",
            (self.ACCEPTED,),
        ).fetchall()
        scored_angles = sorted(
            ((len(terms & _tokens(row["text"])), row) for row in angle_rows),
            key=lambda item: (-item[0], item[1]["angle_id"]),
        )
        angles = [
            {"angle_id": row["angle_id"], "text": row["text"]}
            for score, row in scored_angles[:limit]
            if score
        ]
        return {"claims": claims, "sources": sources, "editorial_angles": angles}

    def counts(self) -> dict[str, int]:
        return {
            "sources": self._connection.execute("SELECT COUNT(*) FROM knowledge_sources").fetchone()[0],
            "evidence": self._connection.execute("SELECT COUNT(*) FROM knowledge_evidence").fetchone()[0],
            "claims": self._connection.execute("SELECT COUNT(*) FROM knowledge_claims").fetchone()[0],
            "accepted_claims": self._connection.execute(
                "SELECT COUNT(*) FROM knowledge_claims WHERE status=?", (self.ACCEPTED,)
            ).fetchone()[0],
            "candidate_claims": self._connection.execute(
                "SELECT COUNT(*) FROM knowledge_claims WHERE status=?", (self.CANDIDATE,)
            ).fetchone()[0],
            "editorial_angles": self._connection.execute("SELECT COUNT(*) FROM knowledge_angles").fetchone()[0],
            "runs": self._connection.execute("SELECT COUNT(*) FROM knowledge_runs").fetchone()[0],
        }

    def close(self) -> None:
        self._connection.close()
