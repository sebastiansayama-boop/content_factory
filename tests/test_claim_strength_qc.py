import json
from pathlib import Path

from content_factory.claim_strength_qc import (
    assess_claim,
    assess_claims,
    summarize_assessments,
)


def _evidence(*, evidence_id="e1", source_id="s1", excerpt="Direct support."):
    return {"id": evidence_id, "source_id": source_id, "excerpt": excerpt}


def _source(source_id="s1"):
    return {"id": source_id, "title": "Primary source", "url": "https://example.com"}


def test_strong_claim_with_one_direct_source_requires_review():
    assessment = assess_claim(
        {
            "id": "c1",
            "text": "Именно Steam перевёл игровую индустрию на цифровую модель.",
            "source_ids": ["s1"],
            "evidence_ids": ["e1"],
        },
        evidence={"e1": _evidence()},
        sources={"s1": _source()},
    )

    assert assessment.claim_type == "generalization"
    assert assessment.claim_strength == 4
    assert assessment.causal_level == "C4"
    assert assessment.evidence_strength == 3
    assert assessment.support_index == -1
    assert assessment.verdict == "REVIEW"
    assert assessment.repair_action == "WEAKEN"


def test_bounded_causality_with_direct_evidence_passes():
    assessment = assess_claim(
        {
            "id": "c2",
            "text": "Steam помог распространению цифровой дистрибуции игр.",
            "source_ids": ["s1"],
            "evidence_ids": ["e1"],
        },
        evidence={"e1": _evidence()},
        sources={"s1": _source()},
    )

    assert assessment.claim_type == "causality"
    assert assessment.claim_strength == 3
    assert assessment.causal_level == "C3"
    assert assessment.evidence_strength == 3
    assert assessment.verdict == "PASS"


def test_two_direct_sources_raise_evidence_to_level_four():
    assessment = assess_claim(
        {
            "id": "c3",
            "text": "Именно Steam стал решающим фактором перехода индустрии к цифре.",
            "source_ids": ["s1", "s2"],
            "evidence_ids": ["e1", "e2"],
        },
        evidence={
            "e1": _evidence(evidence_id="e1", source_id="s1"),
            "e2": _evidence(evidence_id="e2", source_id="s2"),
        },
        sources={"s1": _source("s1"), "s2": _source("s2")},
    )

    assert assessment.evidence_strength == 4
    assert assessment.verdict == "PASS"


def test_unsupported_strong_claim_fails():
    assessment = assess_claim(
        {
            "id": "c4",
            "text": "Именно X навсегда изменил всю игровую индустрию.",
            "source_ids": ["s1"],
            "evidence_ids": [],
        },
        evidence={},
        sources={"s1": _source()},
    )

    assert assessment.claim_strength == 4
    assert assessment.evidence_strength == 0
    assert assessment.verdict == "FAIL"
    assert assessment.repair_action == "REMOVE"


def test_missing_claim_text_is_skipped_without_blocking():
    assessment = assess_claim(
        {"id": "c5", "source_ids": ["s1"], "evidence_ids": ["e1"]},
        evidence={"e1": _evidence()},
        sources={"s1": _source()},
    )
    assert assessment.verdict == "PASS"
    assert assessment.claim_type is None
    assert "skipped" in assessment.reason


def test_series_calibration_current_library():
    root = Path(__file__).resolve().parents[1]
    library = json.loads(
        (root / "library/telegram/computer-games-series.json").read_text(encoding="utf-8")
    )
    claims = []
    evidence = []
    sources = []
    for episode in library["episodes"]:
        claims.extend(episode.get("claims", []))
        evidence.extend(episode.get("evidence", []))
        sources.extend(episode.get("sources", []))

    assessments = assess_claims(
        claims,
        evidence_items=evidence,
        source_items=sources,
    )
    summary = summarize_assessments(assessments)

    print("\n=== CLAIM STRENGTH QC CALIBRATION ===")
    print(json.dumps(summary, ensure_ascii=False))
    for item in assessments:
        if item.verdict != "PASS":
            print(json.dumps(item.to_dict(), ensure_ascii=False))

    assert summary["claims"] == 51
    assert summary["verdicts"]["FAIL"] == 0
