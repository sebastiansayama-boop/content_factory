import hashlib

import pytest

from content_factory.visual_policy import VisualPolicyStore
from content_factory.visual_relevance import VisualVerification


def _verification(candidate_id: str, score: float, decision: str = "ACCEPT") -> VisualVerification:
    return VisualVerification(
        candidate_id=candidate_id,
        decision=decision,
        score=score,
        subject_present=decision == "ACCEPT",
        scene_present=decision == "ACCEPT",
        forbidden_present=False,
        image_type_match=True,
        reason="test",
    )


def _add_controlled_feedback(
    store: VisualPolicyStore,
    index: int,
    *,
    action: str,
    score: float,
    policy_version: str,
    holdout: bool,
) -> None:
    decision_id = store.record_decision(
        run_id=f"run-{index}",
        job_id=f"job-{index}",
        query="test subject",
        verification=_verification(f"candidate-{index}", score),
        policy_version=policy_version,
    )
    target_mod = 0 if holdout else 1
    suffix = 0
    while True:
        feedback_id = f"test-feedback-{index}-{suffix}"
        bucket = int(
            hashlib.sha256(feedback_id.encode("utf-8")).hexdigest()[:8],
            16,
        ) % store.HOLDOUT_MODULUS
        if bucket == target_mod:
            break
        suffix += 1
    with store.db:
        store.db.execute(
            """
            INSERT INTO visual_feedback(
                feedback_id, decision_id, action, reason, source, created_at
            ) VALUES (?, ?, ?, ?, ?, datetime('now'))
            """,
            (feedback_id, decision_id, action, "synthetic", "test"),
        )

def test_baseline_is_active_and_feedback_is_immutable(tmp_path):
    store = VisualPolicyStore(tmp_path / "visual_policy.sqlite3")
    try:
        active = store.active_policy()
        assert active.version == "v1"
        assert active.status == "ACTIVE"
        assert active.score_threshold == 0.0

        decision_id = store.record_decision(
            run_id="run-1",
            job_id="job-1",
            query="crocodile",
            verification=_verification("croc", 0.91),
            policy_version=active.version,
        )
        feedback = store.record_feedback(
            decision_id,
            action="REJECT",
            reason="wrong subject",
        )
        assert feedback["action"] == "REJECT"
        assert feedback["reason"] == "wrong subject"
        with pytest.raises(ValueError, match="already has feedback"):
            store.record_feedback(decision_id, action="ACCEPT")
        assert store.active_policy().version == "v1"
    finally:
        store.close()


def test_candidate_requires_independent_holdout_and_does_not_activate(tmp_path):
    store = VisualPolicyStore(tmp_path / "visual_policy.sqlite3")
    try:
        active = store.active_policy()

        # 40 holdout samples (20/20), followed by 60 training samples (30/30).
        for i in range(100):
            holdout = i < 40
            is_accept = i % 2 == 0
            score = 0.08 if is_accept else 0.02
            action = "ACCEPT" if is_accept else "REJECT"
            _add_controlled_feedback(
                store,
                i,
                action=action,
                score=score,
                policy_version=active.version,
                holdout=holdout,
            )

        candidate = store.propose_candidate()
        assert candidate["status"] == "CANDIDATE"
        assert candidate["parent_version"] == "v1"
        assert 0.0 < candidate["score_threshold"] <= 0.10
        assert candidate["evaluation"]["holdout_passed"] is True
        assert store.active_policy().version == "v1"

        with pytest.raises(ValueError, match="insufficient canary feedback"):
            store.promote(candidate["policy_id"], "test-promote")
    finally:
        store.close()

def test_canary_routes_deterministically_and_promotion_requires_live_evidence(tmp_path, monkeypatch):
    store = VisualPolicyStore(tmp_path / "visual_policy.sqlite3")
    try:
        active = store.active_policy()
        # Seed a validated candidate directly; its holdout gate is already represented
        # by the test fixture and promotion still requires independent canary feedback.
        with store.db:
            store.db.execute(
                """
                INSERT INTO visual_policies(
                    policy_id, version, status, parent_version, score_threshold,
                    max_threshold_delta, evaluation_json, created_at, promoted_at, decision_ref
                ) VALUES (?, ?, 'CANDIDATE', ?, ?, ?, ?, datetime('now'), NULL, NULL)
                """,
                (
                    "candidate-1",
                    "v2",
                    active.version,
                    0.08,
                    0.10,
                    '{"holdout_passed": true}',
                ),
            )

        monkeypatch.setenv("FACTORY_VISUAL_POLICY_CANARY_ID", "candidate-1")
        monkeypatch.setenv("FACTORY_VISUAL_POLICY_CANARY_RATE", "1")
        assert store.policy_for_run("any-run").version == "v2"

        monkeypatch.setenv("FACTORY_VISUAL_POLICY_CANARY_RATE", "0")
        assert store.policy_for_run("any-run").version == "v1"

        monkeypatch.setenv("FACTORY_VISUAL_POLICY_CANARY_RATE", "1")
        monkeypatch.setenv("FACTORY_VISUAL_POLICY_CANARY_ID", "missing")
        assert store.policy_for_run("any-run").version == "v1"
    finally:
        store.close()


def test_candidate_promotes_only_after_safe_canary(tmp_path):
    store = VisualPolicyStore(tmp_path / "visual_policy.sqlite3")
    try:
        active = store.active_policy()
        with store.db:
            store.db.execute(
                """
                INSERT INTO visual_policies(
                    policy_id, version, status, parent_version, score_threshold,
                    max_threshold_delta, evaluation_json, created_at, promoted_at, decision_ref
                ) VALUES (?, ?, 'CANDIDATE', ?, ?, ?, ?, datetime('now'), NULL, NULL)
                """,
                (
                    "candidate-1",
                    "v2",
                    active.version,
                    0.08,
                    0.10,
                    '{"holdout_passed": true}',
                ),
            )

        for i in range(20):
            action = "ACCEPT" if i < 10 else "REJECT"
            score = 0.08 if action == "ACCEPT" else 0.02
            decision_id = store.record_decision(
                run_id=f"canary-run-{i}",
                job_id=f"canary-job-{i}",
                query="subject",
                verification=_verification(f"canary-{i}", score),
                policy_version="v2",
            )
            store.record_feedback(
                decision_id,
                action=action,
                reason="canary",
                source="test",
            )

        promoted = store.promote("candidate-1", "human-canary-approval")
        assert promoted["status"] == "ACTIVE"
        assert promoted["version"] == "v2"
        assert store.active_policy().version == "v2"
    finally:
        store.close()
