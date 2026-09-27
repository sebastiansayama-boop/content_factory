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
    source_ids: tuple[str, ...]
    first_seen_at: str


@dataclass(frozen=True)
class KnowledgeAngle:
    angle_id: str
    text: str
    first_seen_at: str


class KnowledgeStore:
    """Small durable store for reusable research knowledge.

    This is deliberately not a semantic/vector database. It provides stable
    persistence, deterministic retrieval, and source/claim relationships that
    later retrieval layers can replace without changing the product contract.
    """

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
            CREATE TABLE IF NOT EXISTS knowledge_claims (
                claim_id TEXT PRIMARY KEY,
                text TEXT NOT NULL UNIQUE,
                confidence TEXT NOT NULL,
                first_seen_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS knowledge_claim_sources (
                claim_id TEXT NOT NULL,
                source_id TEXT NOT NULL,
                PRIMARY KEY (claim_id, source_id),
                FOREIGN KEY (claim_id) REFERENCES knowledge_claims(claim_id),
                FOREIGN KEY (source_id) REFERENCES knowledge_sources(source_id)
            );
            CREATE TABLE IF NOT EXISTS knowledge_angles (
                angle_id TEXT PRIMARY KEY,
                text TEXT NOT NULL UNIQUE,
                first_seen_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS knowledge_runs (
                run_id TEXT PRIMARY KEY,
                captured_at TEXT NOT NULL
            );
            """
        )
        self._connection.commit()

    def capture(self, *, run_id: str, research: dict[str, Any]) -> dict[str, int]:
        claims = research.get("claims")
        sources = research.get("sources")
        angles = research.get("editorial_angles", [])
        if not isinstance(claims, list) or not isinstance(sources, list):
            raise ValueError("research claims and sources must be arrays")
        if not isinstance(angles, list):
            raise ValueError("research editorial_angles must be an array")

        source_map: dict[str, str] = {}
        source_count = 0
        claim_count = 0
        angle_count = 0

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

            for claim in claims:
                if not isinstance(claim, dict):
                    raise ValueError("research claim must be an object")
                text = str(claim.get("text") or "").strip()
                confidence = str(claim.get("confidence") or "low").strip().lower()
                refs = claim.get("source_ids")
                if not text or confidence not in {"high", "medium", "low"}:
                    raise ValueError("every research claim requires text and valid confidence")
                if not isinstance(refs, list) or not refs or not all(ref in source_map for ref in refs):
                    raise ValueError(f"claim {claim.get('id')} has invalid source_ids")
                existing = self._connection.execute(
                    "SELECT claim_id FROM knowledge_claims WHERE text = ?", (text,)
                ).fetchone()
                if existing:
                    stable_claim_id = str(existing["claim_id"])
                    self._connection.execute(
                        "UPDATE knowledge_claims SET confidence = ? WHERE claim_id = ?",
                        (confidence, stable_claim_id),
                    )
                else:
                    stable_claim_id = f"kc-{uuid4().hex[:16]}"
                    self._connection.execute(
                        "INSERT INTO knowledge_claims(claim_id,text,confidence,first_seen_at) VALUES(?,?,?,?)",
                        (stable_claim_id, text, confidence, _now()),
                    )
                    claim_count += 1
                for ref in refs:
                    self._connection.execute(
                        "INSERT OR IGNORE INTO knowledge_claim_sources(claim_id,source_id) VALUES(?,?)",
                        (stable_claim_id, source_map[ref]),
                    )

            for angle in angles:
                text = str(angle).strip()
                if not text:
                    continue
                self._connection.execute(
                    "INSERT OR IGNORE INTO knowledge_angles(angle_id,text,first_seen_at) VALUES(?,?,?)",
                    (f"ka-{uuid4().hex[:16]}", text, _now()),
                )
                if self._connection.execute(
                    "SELECT changes() AS changes"
                ).fetchone()["changes"]:
                    angle_count += 1

            self._connection.execute(
                "INSERT OR REPLACE INTO knowledge_runs(run_id,captured_at) VALUES(?,?)",
                (run_id, _now()),
            )

        return {"sources_added": source_count, "claims_added": claim_count, "angles_added": angle_count}

    def search(self, query: str, *, limit: int = 8) -> dict[str, list[dict[str, Any]]]:
        terms = _tokens(query)
        if not terms:
            return {"claims": [], "sources": [], "editorial_angles": []}

        claim_rows = self._connection.execute(
            "SELECT claim_id,text,confidence,first_seen_at FROM knowledge_claims"
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
            source_ids.update(str(ref["source_id"]) for ref in refs)
            claims.append({
                "claim_id": row["claim_id"],
                "text": row["text"],
                "confidence": row["confidence"],
                "source_ids": [ref["source_id"] for ref in refs],
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
            "SELECT angle_id,text,first_seen_at FROM knowledge_angles"
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
            "claims": self._connection.execute("SELECT COUNT(*) FROM knowledge_claims").fetchone()[0],
            "editorial_angles": self._connection.execute("SELECT COUNT(*) FROM knowledge_angles").fetchone()[0],
            "runs": self._connection.execute("SELECT COUNT(*) FROM knowledge_runs").fetchone()[0],
        }

    def close(self) -> None:
        self._connection.close()
