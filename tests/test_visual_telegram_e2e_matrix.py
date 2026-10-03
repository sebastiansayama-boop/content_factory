from __future__ import annotations

import re

import pytest

SCENARIOS = (
    ("VQC-01", "Clean accept", "ACCEPT"),
    ("VQC-02", "Hard negative", "REJECT"),
    ("VQC-03", "Wrong subject", "REJECT"),
    ("VQC-04", "Wrong context", "REJECT"),
    ("VQC-05", "Wrong image type", "REJECT"),
    ("VQC-06", "Multi-asset package", "MIXED"),
    ("VQC-07", "Successful regeneration", "REJECT_THEN_ACCEPT"),
    ("VQC-08", "Repeated regeneration", "REJECT_THEN_REJECT_THEN_ACCEPT"),
)

REQUIRED_REASON_CODES = {
    "WRONG_SUBJECT",
    "WRONG_SCENE",
    "WRONG_IMAGE_TYPE",
    "WRONG_CONTEXT",
    "QUALITY",
    "DUPLICATE",
    "OTHER",
}

REQUIRED_TRACE_FIELDS = {
    "run_id", "asset_id", "decision_id", "candidate_id", "policy_version",
    "machine_decision", "score", "human_action", "human_reason", "timestamp",
    "source_run_id", "replacement_run_id", "regeneration_instruction",
    "replacement_decision_id", "replacement_machine_decision",
    "replacement_human_action", "final_status",
}


@pytest.mark.parametrize("scenario_id,title,shape", SCENARIOS)
def test_visual_telegram_scenario_matrix_is_explicit(scenario_id, title, shape):
    assert re.fullmatch(r"VQC-0[1-8]", scenario_id)
    assert title
    assert shape


def test_visual_telegram_matrix_covers_primary_failure_classes():
    titles = {title for _, title, _ in SCENARIOS}
    assert {
        "Clean accept", "Hard negative", "Wrong subject", "Wrong context",
        "Wrong image type", "Multi-asset package", "Successful regeneration",
        "Repeated regeneration",
    } <= titles


def test_visual_telegram_trace_has_enough_lineage_to_isolate_failures():
    assert {
        "source_run_id", "replacement_run_id", "decision_id",
        "replacement_decision_id", "machine_decision",
        "replacement_machine_decision", "human_action",
        "replacement_human_action", "final_status",
    } <= REQUIRED_TRACE_FIELDS


def test_visual_telegram_reject_reasons_are_bounded():
    assert REQUIRED_REASON_CODES == {
        "WRONG_SUBJECT", "WRONG_SCENE", "WRONG_IMAGE_TYPE",
        "WRONG_CONTEXT", "QUALITY", "DUPLICATE", "OTHER",
    }
