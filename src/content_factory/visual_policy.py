from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from .visual_relevance import VisualVerification


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _serialized(method):
    def wrapper(self, *args, **kwargs):
        with self._lock:
            return method(self, *args, **kwargs)
    return wrapper


@dataclass(frozen=True)
class VisualPolicy:
    policy_id: str
    version: str
    status: str
    parent_version: str | None
    score_threshold: float
    max_threshold_delta: float = 0.10

    def accepts(self, verification: VisualVerification) -> bool:
        return verification.accepted and verification.score >= self.score_threshold


class VisualPolicyStore:
    """Durable, conservative learning loop for visual relevance decisions.

    Policy changes are proposals first. The active policy is immutable until an
    explicit promotion passes historical holdout and live-canary gates.
    """

    DEFAULT_POLICY_VERSION = "v1"
    DEFAULT_SCORE_THRESHOLD = 0.0
    MIN_FEEDBACK_SAMPLES = 20
    MIN_CLASS_SAMPLES = 5
    MIN_HOLDOUT_SAMPLES = 10
    MIN_CANARY_SAMPLES = 20
    MAX_ALLOWED_ERROR_INCREASE = 0.0
    MAX_FALSE_NEGATIVE_RATE_INCREASE = 0.02
    MAX_COVERAGE_DROP = 0.05
    MIN_ERROR_IMPROVEMENT = 0.01
    HOLDOUT_MODULUS = 5

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self.db = sqlite3.connect(self.path, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self._initialize()

    def _initialize(self) -> None:
        with self.db:
            self.db.executescript(
                """
                CREATE TABLE IF NOT EXISTS visual_policies (
                    policy_id TEXT PRIMARY KEY,
                    version TEXT NOT NULL UNIQUE,
                    status TEXT NOT NULL,
                    parent_version TEXT,
                    score_threshold REAL NOT NULL,
                    max_threshold_delta REAL NOT NULL,
                    evaluation_json TEXT,
                    created_at TEXT NOT NULL,
                    promoted_at TEXT,
                    decision_ref TEXT
                );

                CREATE TABLE IF NOT EXISTS visual_decisions (
                    decision_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    job_id TEXT NOT NULL,
                    candidate_id TEXT NOT NULL,
                    policy_version TEXT NOT NULL,
                    query TEXT NOT NULL,
                    machine_decision TEXT NOT NULL,
                    score REAL NOT NULL,
                    subject_present INTEGER NOT NULL,
                    scene_present INTEGER NOT NULL,
                    forbidden_present INTEGER NOT NULL,
                    image_type_match INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS visual_feedback (
                    feedback_id TEXT PRIMARY KEY,
                    decision_id TEXT NOT NULL UNIQUE,
                    action TEXT NOT NULL,
                    reason TEXT,
                    source TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(decision_id) REFERENCES visual_decisions(decision_id)
                );

                CREATE INDEX IF NOT EXISTS idx_visual_decisions_policy
                    ON visual_decisions(policy_version);
                CREATE INDEX IF NOT EXISTS idx_visual_feedback_decision
                    ON visual_feedback(decision_id);

                CREATE TABLE IF NOT EXISTS visual_policy_activation (
                    policy_key TEXT PRIMARY KEY,
                    active_policy_id TEXT NOT NULL,
                    generation INTEGER NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(active_policy_id) REFERENCES visual_policies(policy_id)
                );

                CREATE TABLE IF NOT EXISTS visual_policy_audit (
                    audit_id TEXT PRIMARY KEY,
                    policy_key TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    from_policy_id TEXT,
                    to_policy_id TEXT NOT NULL,
                    from_version TEXT,
                    to_version TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    decision_ref TEXT NOT NULL,
                    generation_before INTEGER NOT NULL,
                    generation_after INTEGER NOT NULL,
                    request_id TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_visual_policy_audit_created
                    ON visual_policy_audit(created_at);
                """
            )
            row = self.db.execute(
                "SELECT 1 FROM visual_policies WHERE status='ACTIVE' LIMIT 1"
            ).fetchone()
            if row is None:
                self.db.execute(
                    """
                    INSERT INTO visual_policies(
                        policy_id, version, status, parent_version,
                        score_threshold, max_threshold_delta,
                        evaluation_json, created_at, promoted_at, decision_ref
                    ) VALUES (?, ?, 'ACTIVE', NULL, ?, ?, ?, ?, NULL, NULL)
                    """,
                    (
                        f"vpolicy-{uuid4()}",
                        self.DEFAULT_POLICY_VERSION,
                        self.DEFAULT_SCORE_THRESHOLD,
                        0.10,
                        json.dumps(
                            {
                                "kind": "baseline",
                                "reason": "preserve existing visual acceptance behavior",
                            },
                            sort_keys=True,
                        ),
                        _now(),
                    ),
                )

            active_row = self.db.execute(
                "SELECT policy_id, version FROM visual_policies "
                "WHERE status='ACTIVE' ORDER BY rowid DESC LIMIT 1"
            ).fetchone()
            if active_row is None:
                raise RuntimeError("cannot initialize visual policy activation")
            activation = self.db.execute(
                "SELECT 1 FROM visual_policy_activation WHERE policy_key=?",
                ("visual_relevance",),
            ).fetchone()
            if activation is None:
                self.db.execute(
                    """
                    INSERT INTO visual_policy_activation(
                        policy_key, active_policy_id, generation, updated_at
                    ) VALUES (?, ?, ?, ?)
                    """,
                    ("visual_relevance", active_row["policy_id"], 1, _now()),
                )

    def close(self) -> None:
        self.db.close()

    @_serialized
    def active_policy(self) -> VisualPolicy:
        row = self.db.execute(
            """
            SELECT p.* FROM visual_policies p
            JOIN visual_policy_activation a
              ON a.active_policy_id = p.policy_id
            WHERE a.policy_key=?
            """,
            ("visual_relevance",),
        ).fetchone()
        if row is None:
            raise RuntimeError("no active visual policy")
        return self._policy_from_row(row)

    @_serialized
    def activation_state(self) -> dict[str, Any]:
        row = self.db.execute(
            """
            SELECT a.active_policy_id, a.generation, a.updated_at, p.version
            FROM visual_policy_activation a
            JOIN visual_policies p ON p.policy_id=a.active_policy_id
            WHERE a.policy_key=?
            """,
            ("visual_relevance",),
        ).fetchone()
        if row is None:
            raise RuntimeError("visual policy activation is missing")
        return {
            "policy_key": "visual_relevance",
            "active_policy_id": row["active_policy_id"],
            "active_version": row["version"],
            "generation": int(row["generation"]),
            "updated_at": row["updated_at"],
        }

    @_serialized
    def audit(self, limit: int = 100) -> list[dict[str, Any]]:
        limit = max(1, min(int(limit), 500))
        rows = self.db.execute(
            "SELECT * FROM visual_policy_audit ORDER BY rowid DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]

    @_serialized
    def get_policy(self, policy_id: str) -> VisualPolicy:
        row = self.db.execute(
            "SELECT * FROM visual_policies WHERE policy_id=?", (policy_id,)
        ).fetchone()
        if row is None:
            raise ValueError("visual policy not found")
        return self._policy_from_row(row)

    @_serialized
    def list_policies(self) -> list[dict[str, Any]]:
        rows = self.db.execute(
            "SELECT * FROM visual_policies ORDER BY rowid DESC"
        ).fetchall()
        return [self._policy_dict(row) for row in rows]

    @_serialized
    def policy_for_run(self, run_id: str) -> VisualPolicy:
        active = self.active_policy()
        candidate_id = os.environ.get("FACTORY_VISUAL_POLICY_CANARY_ID", "").strip()
        if not candidate_id:
            return active

        try:
            rate = float(os.environ.get("FACTORY_VISUAL_POLICY_CANARY_RATE", "0"))
        except ValueError:
            return active
        if not 0.0 < rate <= 1.0:
            return active

        try:
            candidate = self.get_policy(candidate_id)
        except ValueError:
            return active
        if candidate.status != "CANDIDATE":
            return active

        evaluation = self._evaluation(candidate.policy_id)
        if not bool(evaluation.get("holdout_passed")):
            return active

        bucket = int(hashlib.sha256(run_id.encode("utf-8")).hexdigest()[:12], 16)
        return candidate if bucket / float(16**12 - 1) < rate else active

    @_serialized
    def record_decision(
        self,
        *,
        run_id: str,
        job_id: str,
        query: str,
        verification: VisualVerification,
        policy_version: str,
    ) -> str:
        decision_id = f"vdecision-{uuid4()}"
        with self.db:
            self.db.execute(
                """
                INSERT INTO visual_decisions(
                    decision_id, run_id, job_id, candidate_id, policy_version,
                    query, machine_decision, score, subject_present, scene_present,
                    forbidden_present, image_type_match, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    decision_id,
                    run_id,
                    job_id,
                    verification.candidate_id,
                    policy_version,
                    query.strip(),
                    verification.decision,
                    verification.score,
                    int(verification.subject_present),
                    int(verification.scene_present),
                    int(verification.forbidden_present),
                    int(verification.image_type_match),
                    _now(),
                ),
            )
        return decision_id

    @_serialized
    def record_feedback(
        self,
        decision_id: str,
        *,
        action: str,
        reason: str = "",
        source: str = "human",
    ) -> dict[str, Any]:
        normalized = action.strip().upper()
        if normalized not in {"ACCEPT", "REJECT"}:
            raise ValueError("visual feedback action must be ACCEPT or REJECT")
        decision = self.db.execute(
            "SELECT decision_id FROM visual_decisions WHERE decision_id=?",
            (decision_id,),
        ).fetchone()
        if decision is None:
            raise ValueError("visual decision not found")
        existing = self.db.execute(
            "SELECT feedback_id FROM visual_feedback WHERE decision_id=?",
            (decision_id,),
        ).fetchone()
        if existing is not None:
            raise ValueError("visual decision already has feedback")

        feedback_id = f"vfeedback-{uuid4()}"
        with self.db:
            self.db.execute(
                """
                INSERT INTO visual_feedback(
                    feedback_id, decision_id, action, reason, source, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    feedback_id,
                    decision_id,
                    normalized,
                    reason.strip()[:1000],
                    source.strip()[:120] or "human",
                    _now(),
                ),
            )
        row = self.db.execute(
            """
            SELECT f.feedback_id, f.decision_id, f.action, f.reason, f.source, f.created_at,
                   d.run_id, d.job_id, d.candidate_id, d.policy_version, d.score
            FROM visual_feedback f
            JOIN visual_decisions d ON d.decision_id=f.decision_id
            WHERE f.feedback_id=?
            """,
            (feedback_id,),
        ).fetchone()
        return dict(row)

    @_serialized
    def propose_candidate(self) -> dict[str, Any]:
        active = self.active_policy()
        rows = self.db.execute(
            """
            SELECT d.*, f.feedback_id, f.action
            FROM visual_decisions d
            JOIN visual_feedback f ON f.decision_id=d.decision_id
            ORDER BY f.created_at ASC
            """
        ).fetchall()

        if len(rows) < self.MIN_FEEDBACK_SAMPLES:
            raise ValueError(
                f"insufficient visual feedback: {len(rows)} < {self.MIN_FEEDBACK_SAMPLES}"
            )

        train = []
        holdout = []
        for row in rows:
            bucket = int(hashlib.sha256(row["feedback_id"].encode("utf-8")).hexdigest()[:8], 16)
            (holdout if bucket % self.HOLDOUT_MODULUS == 0 else train).append(row)

        if len(holdout) < self.MIN_HOLDOUT_SAMPLES:
            raise ValueError("insufficient independent visual holdout samples")
        if len(train) < self.MIN_FEEDBACK_SAMPLES - self.MIN_HOLDOUT_SAMPLES:
            raise ValueError("insufficient visual training samples")

        self._require_both_classes(train, "training")
        self._require_both_classes(holdout, "holdout")

        lower = max(0.0, active.score_threshold - active.max_threshold_delta)
        upper = min(1.0, active.score_threshold + active.max_threshold_delta)
        candidate_thresholds = {
            round(active.score_threshold, 6),
            *(
                round(float(row["score"]), 6)
                for row in train
                if lower <= float(row["score"]) <= upper
            ),
        }

        baseline_train = self._evaluate(train, active.score_threshold)
        baseline_holdout = self._evaluate(holdout, active.score_threshold)

        best_threshold: float | None = None
        best_holdout: dict[str, Any] | None = None
        best_train: dict[str, Any] | None = None

        for threshold in sorted(candidate_thresholds):
            train_metrics = self._evaluate(train, threshold)
            holdout_metrics = self._evaluate(holdout, threshold)
            if threshold == active.score_threshold:
                continue
            if not self._passes_gate(baseline_train, train_metrics):
                continue
            if not self._passes_gate(
                baseline_holdout,
                holdout_metrics,
                require_improvement=True,
            ):
                continue
            if (
                best_holdout is None
                or holdout_metrics["error_rate"] < best_holdout["error_rate"]
                or (
                    holdout_metrics["error_rate"] == best_holdout["error_rate"]
                    and holdout_metrics["false_negative_rate"]
                    < best_holdout["false_negative_rate"]
                )
            ):
                best_threshold = threshold
                best_holdout = holdout_metrics
                best_train = train_metrics

        if best_threshold is None or best_holdout is None or best_train is None:
            raise ValueError("no safe visual policy improvement found on holdout")

        version_number = self._next_version_number()
        policy_id = f"vpolicy-{uuid4()}"
        evaluation = {
            "kind": "learned_visual_threshold",
            "training": best_train,
            "baseline_training": baseline_train,
            "holdout": best_holdout,
            "baseline_holdout": baseline_holdout,
            "holdout_passed": True,
            "bounded_delta": round(best_threshold - active.score_threshold, 6),
            "sample_count": len(rows),
        }
        with self.db:
            self.db.execute(
                """
                INSERT INTO visual_policies(
                    policy_id, version, status, parent_version,
                    score_threshold, max_threshold_delta,
                    evaluation_json, created_at, promoted_at, decision_ref
                ) VALUES (?, ?, 'CANDIDATE', ?, ?, ?, ?, ?, NULL, NULL)
                """,
                (
                    policy_id,
                    f"v{version_number}",
                    active.version,
                    best_threshold,
                    active.max_threshold_delta,
                    json.dumps(evaluation, ensure_ascii=False, sort_keys=True),
                    _now(),
                ),
            )
        return self._policy_dict(
            self.db.execute(
                "SELECT * FROM visual_policies WHERE policy_id=?", (policy_id,)
            ).fetchone()
        )

    @_serialized
    def promote(
        self,
        policy_id: str,
        decision_ref: str,
        *,
        expected_generation: int | None = None,
        actor: str = "api",
        request_id: str | None = None,
    ) -> dict[str, Any]:
        if not decision_ref.strip():
            raise ValueError("decision_ref is required")
        candidate = self.get_policy(policy_id)
        if candidate.status != "CANDIDATE":
            raise ValueError("visual policy must be CANDIDATE before promotion")
        evaluation = self._evaluation(policy_id)
        if not evaluation.get("holdout_passed"):
            raise ValueError("visual policy failed holdout gate")
        canary = self._canary_evaluation(candidate)
        if not canary["passed"]:
            raise ValueError(canary["reason"])

        request_id = request_id or f"policy-request-{uuid4()}"
        self.db.execute("BEGIN IMMEDIATE")
        try:
            activation = self.db.execute(
                "SELECT active_policy_id, generation FROM visual_policy_activation "
                "WHERE policy_key=?",
                ("visual_relevance",),
            ).fetchone()
            if activation is None:
                raise RuntimeError("visual policy activation is missing")
            generation_before = int(activation["generation"])
            if expected_generation is not None and generation_before != expected_generation:
                raise ValueError(
                    f"visual policy generation conflict: expected {expected_generation}, "
                    f"actual {generation_before}"
                )
            active_row = self.db.execute(
                "SELECT * FROM visual_policies WHERE policy_id=?",
                (activation["active_policy_id"],),
            ).fetchone()
            candidate_row = self.db.execute(
                "SELECT * FROM visual_policies WHERE policy_id=?",
                (policy_id,),
            ).fetchone()
            if active_row is None or candidate_row is None:
                raise RuntimeError("visual policy version disappeared during promotion")
            if candidate_row["status"] != "CANDIDATE":
                raise ValueError("visual policy is no longer a candidate")
            if candidate_row["parent_version"] != active_row["version"]:
                raise ValueError("visual policy parent is no longer active")

            now = _now()
            next_generation = generation_before + 1
            self.db.execute(
                "UPDATE visual_policies SET status='RETIRED' WHERE policy_id=?",
                (active_row["policy_id"],),
            )
            self.db.execute(
                "UPDATE visual_policies SET status='ACTIVE', promoted_at=?, decision_ref=? "
                "WHERE policy_id=? AND status='CANDIDATE'",
                (now, decision_ref.strip(), policy_id),
            )
            changed = self.db.execute(
                """
                UPDATE visual_policy_activation
                SET active_policy_id=?, generation=?, updated_at=?
                WHERE policy_key=? AND generation=?
                """,
                (
                    policy_id,
                    next_generation,
                    now,
                    "visual_relevance",
                    generation_before,
                ),
            )
            if changed.rowcount != 1:
                raise ValueError("visual policy activation changed concurrently")
            self.db.execute(
                """
                INSERT INTO visual_policy_audit(
                    audit_id, policy_key, operation, from_policy_id, to_policy_id,
                    from_version, to_version, reason, actor, decision_ref,
                    generation_before, generation_after, request_id, created_at
                ) VALUES (?, ?, 'PROMOTE', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    f"vaudit-{uuid4()}",
                    "visual_relevance",
                    active_row["policy_id"],
                    policy_id,
                    active_row["version"],
                    candidate_row["version"],
                    "candidate passed holdout and canary gates",
                    actor.strip() or "api",
                    decision_ref.strip(),
                    generation_before,
                    next_generation,
                    request_id,
                    now,
                ),
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

        return self._policy_dict(
            self.db.execute(
                "SELECT * FROM visual_policies WHERE policy_id=?", (policy_id,)
            ).fetchone()
        )

    @_serialized
    def rollback(
        self,
        *,
        expected_generation: int,
        reason: str,
        decision_ref: str,
        actor: str = "api",
        request_id: str | None = None,
    ) -> dict[str, Any]:
        if expected_generation < 1:
            raise ValueError("expected_generation must be >= 1")
        if not reason.strip():
            raise ValueError("rollback reason is required")
        if not decision_ref.strip():
            raise ValueError("decision_ref is required")

        request_id = request_id or f"policy-request-{uuid4()}"
        self.db.execute("BEGIN IMMEDIATE")
        try:
            activation = self.db.execute(
                "SELECT active_policy_id, generation FROM visual_policy_activation "
                "WHERE policy_key=?",
                ("visual_relevance",),
            ).fetchone()
            if activation is None:
                raise RuntimeError("visual policy activation is missing")
            generation_before = int(activation["generation"])
            if generation_before != expected_generation:
                raise ValueError(
                    f"visual policy generation conflict: expected {expected_generation}, "
                    f"actual {generation_before}"
                )

            current = self.db.execute(
                "SELECT * FROM visual_policies WHERE policy_id=?",
                (activation["active_policy_id"],),
            ).fetchone()
            if current is None:
                raise RuntimeError("active visual policy not found")

            last_activation = self.db.execute(
                """
                SELECT * FROM visual_policy_audit
                WHERE policy_key=? AND to_policy_id=?
                ORDER BY rowid DESC LIMIT 1
                """,
                ("visual_relevance", current["policy_id"]),
            ).fetchone()
            if last_activation is None or last_activation["operation"] != "PROMOTE":
                raise ValueError(
                    "rollback is available only for the latest promoted active policy"
                )

            target = self.db.execute(
                "SELECT * FROM visual_policies WHERE policy_id=?",
                (last_activation["from_policy_id"],),
            ).fetchone()
            if target is None:
                raise RuntimeError("rollback target policy not found")
            if target["policy_id"] == current["policy_id"]:
                raise RuntimeError("rollback target equals active policy")

            now = _now()
            next_generation = generation_before + 1
            self.db.execute(
                "UPDATE visual_policies SET status='RETIRED' WHERE policy_id=?",
                (current["policy_id"],),
            )
            self.db.execute(
                "UPDATE visual_policies SET status='ACTIVE' WHERE policy_id=?",
                (target["policy_id"],),
            )
            changed = self.db.execute(
                """
                UPDATE visual_policy_activation
                SET active_policy_id=?, generation=?, updated_at=?
                WHERE policy_key=? AND generation=?
                """,
                (
                    target["policy_id"],
                    next_generation,
                    now,
                    "visual_relevance",
                    generation_before,
                ),
            )
            if changed.rowcount != 1:
                raise ValueError("visual policy activation changed concurrently")

            self.db.execute(
                """
                INSERT INTO visual_policy_audit(
                    audit_id, policy_key, operation, from_policy_id, to_policy_id,
                    from_version, to_version, reason, actor, decision_ref,
                    generation_before, generation_after, request_id, created_at
                ) VALUES (?, ?, 'ROLLBACK', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    f"vaudit-{uuid4()}",
                    "visual_relevance",
                    current["policy_id"],
                    target["policy_id"],
                    current["version"],
                    target["version"],
                    reason.strip()[:2000],
                    actor.strip() or "api",
                    decision_ref.strip(),
                    generation_before,
                    next_generation,
                    request_id,
                    now,
                ),
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

        result = self._policy_dict(
            self.db.execute(
                "SELECT * FROM visual_policies WHERE policy_id=?",
                (target["policy_id"],),
            ).fetchone()
        )
        result["rollback"] = {
            "from_version": current["version"],
            "to_version": target["version"],
            "generation_before": generation_before,
            "generation_after": next_generation,
            "decision_ref": decision_ref.strip(),
            "request_id": request_id,
        }
        return result

    def _canary_evaluation(self, candidate: VisualPolicy) -> dict[str, Any]:
        active = self.active_policy()
        rows = self.db.execute(
            """
            SELECT d.*, f.feedback_id, f.action
            FROM visual_decisions d
            JOIN visual_feedback f ON f.decision_id=d.decision_id
            WHERE d.policy_version=?
            ORDER BY f.created_at ASC
            """,
            (candidate.version,),
        ).fetchall()
        if len(rows) < self.MIN_CANARY_SAMPLES:
            return {
                "passed": False,
                "reason": (
                    f"insufficient canary feedback: {len(rows)} < "
                    f"{self.MIN_CANARY_SAMPLES}"
                ),
            }

        try:
            self._require_both_classes(rows, "canary")
        except ValueError as exc:
            return {"passed": False, "reason": str(exc)}

        baseline = self._evaluate(rows, active.score_threshold)
        candidate_metrics = self._evaluate(rows, candidate.score_threshold)
        passed = self._passes_gate(baseline, candidate_metrics)
        return {
            "passed": passed,
            "reason": (
                "canary metrics passed"
                if passed
                else "canary metrics exceeded safety limits"
            ),
            "candidate": candidate_metrics,
            "baseline": baseline,
        }

    @classmethod
    def _passes_gate(
        cls,
        baseline: dict[str, Any],
        candidate: dict[str, Any],
        *,
        require_improvement: bool = False,
    ) -> bool:
        error_ok = candidate["error_rate"] <= (
            baseline["error_rate"] + cls.MAX_ALLOWED_ERROR_INCREASE
        )
        fn_ok = candidate["false_negative_rate"] <= (
            baseline["false_negative_rate"] + cls.MAX_FALSE_NEGATIVE_RATE_INCREASE
        )
        coverage_ok = candidate["coverage"] >= (
            baseline["coverage"] - cls.MAX_COVERAGE_DROP
        )
        improved = candidate["error_rate"] <= (
            baseline["error_rate"] - cls.MIN_ERROR_IMPROVEMENT
        )
        return error_ok and fn_ok and coverage_ok and (improved if require_improvement else True)

    @staticmethod
    def _require_both_classes(rows: list[sqlite3.Row], label: str) -> None:
        accepts = sum(row["action"] == "ACCEPT" for row in rows)
        rejects = sum(row["action"] == "REJECT" for row in rows)
        if accepts < VisualPolicyStore.MIN_CLASS_SAMPLES:
            raise ValueError(
                f"insufficient {label} ACCEPT feedback: {accepts} < "
                f"{VisualPolicyStore.MIN_CLASS_SAMPLES}"
            )
        if rejects < VisualPolicyStore.MIN_CLASS_SAMPLES:
            raise ValueError(
                f"insufficient {label} REJECT feedback: {rejects} < "
                f"{VisualPolicyStore.MIN_CLASS_SAMPLES}"
            )

    @staticmethod
    def _evaluate(rows: list[sqlite3.Row], threshold: float) -> dict[str, Any]:
        tp = fp = tn = fn = 0
        for row in rows:
            machine_eligible = (
                row["machine_decision"] == "ACCEPT"
                and bool(row["subject_present"])
                and not bool(row["forbidden_present"])
            )
            predicted = machine_eligible and float(row["score"]) >= threshold
            actual = row["action"] == "ACCEPT"
            if predicted and actual:
                tp += 1
            elif predicted and not actual:
                fp += 1
            elif not predicted and actual:
                fn += 1
            else:
                tn += 1

        total = len(rows)
        positives = tp + fn
        coverage = (tp + fp) / total if total else 0.0
        return {
            "samples": total,
            "true_positive": tp,
            "false_positive": fp,
            "true_negative": tn,
            "false_negative": fn,
            "error_rate": (fp + fn) / total if total else 0.0,
            "false_negative_rate": fn / positives if positives else 0.0,
            "coverage": coverage,
        }

    def _next_version_number(self) -> int:
        rows = self.db.execute("SELECT version FROM visual_policies").fetchall()
        numbers = []
        for row in rows:
            try:
                numbers.append(int(str(row["version"]).removeprefix("v")))
            except ValueError:
                continue
        return max(numbers or [0]) + 1

    @staticmethod
    def _policy_from_row(row: sqlite3.Row) -> VisualPolicy:
        return VisualPolicy(
            policy_id=row["policy_id"],
            version=row["version"],
            status=row["status"],
            parent_version=row["parent_version"],
            score_threshold=float(row["score_threshold"]),
            max_threshold_delta=float(row["max_threshold_delta"]),
        )

    @staticmethod
    def _policy_dict(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "policy_id": row["policy_id"],
            "version": row["version"],
            "status": row["status"],
            "parent_version": row["parent_version"],
            "score_threshold": float(row["score_threshold"]),
            "max_threshold_delta": float(row["max_threshold_delta"]),
            "evaluation": json.loads(row["evaluation_json"] or "{}"),
            "created_at": row["created_at"],
            "promoted_at": row["promoted_at"],
            "decision_ref": row["decision_ref"],
        }

    def _evaluation(self, policy_id: str) -> dict[str, Any]:
        row = self.db.execute(
            "SELECT evaluation_json FROM visual_policies WHERE policy_id=?",
            (policy_id,),
        ).fetchone()
        if row is None:
            raise ValueError("visual policy not found")
        return json.loads(row["evaluation_json"] or "{}")
