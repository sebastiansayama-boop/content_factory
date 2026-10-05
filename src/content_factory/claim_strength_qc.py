from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any, Literal


ClaimType = Literal["fact", "interpretation", "causality", "generalization"]
CausalLevel = Literal["C0", "C1", "C2", "C3", "C4"]
Verdict = Literal["PASS", "REVIEW", "FAIL"]
RepairAction = Literal["NONE", "WEAKEN", "ADD_EVIDENCE", "REMOVE"]


@dataclass(frozen=True)
class ClaimStrengthAssessment:
    claim_id: str
    text: str
    claim_type: ClaimType | None
    claim_strength: int
    causal_level: CausalLevel
    evidence_strength: int
    evidence_count: int
    source_count: int
    support_index: int
    verdict: Verdict
    repair_action: RepairAction
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# Claim strength is an editorial scale, not a truth score.
# 0 = directly descriptive fact.
# 1 = limited interpretation.
# 2 = bounded synthesis / broad interpretation.
# 3 = material causal or broad general claim.
# 4 = decisive, universal, or exclusive causal/general claim.
_CLAIM_STRENGTH_LABELS = {
    0: "fact",
    1: "limited_interpretation",
    2: "bounded_interpretation",
    3: "strong_causality_or_generalization",
    4: "decisive_or_universal_claim",
}

_STRONG_CAUSAL_PATTERNS = (
    "именно ",
    "единственн",
    "главн",
    "решающ",
    "без него",
    "без неё",
    "без него",
    "без нее",
    "только благодаря",
    "solely",
    "sole cause",
    "decisive cause",
    "the only reason",
    "directly caused",
)

_CAUSAL_PATTERNS = (
    "привел к",
    "привела к",
    "привело к",
    "привели к",
    "стал причиной",
    "стала причиной",
    "стало причиной",
    "причиной стал",
    "причиной стала",
    "из-за ",
    "благодаря ",
    "способствовал",
    "способствовала",
    "способствовали",
    "помог ",
    "помогла ",
    "помогли ",
    "позволил ",
    "позволила ",
    "позволили ",
    "сформировал",
    "сформировала",
    "сформировали",
    "превратил",
    "превратила",
    "превратили",
    "изменил",
    "изменила",
    "изменили",
    "изменило",
    "доказал",
    "доказала",
    "доказали",
    "перевел",
    "перевела",
    "перевели",
    "создал условия",
    "создала условия",
    "создали условия",
    "led to",
    "caused",
    "contributed",
    "helped",
    "enabled",
    "transformed",
    "changed",
)

_ASSOCIATION_PATTERNS = (
    "связан с",
    "связана с",
    "связано с",
    "связаны с",
    "сопровождал",
    "сопровождала",
    "correlated",
    "associated with",
)

_GENERALIZATION_PATTERNS = (
    "игровую индустрию",
    "игровой индустрии",
    "игровая индустрия",
    "индустрию",
    "индустрии",
    "рынок",
    "рынка",
    "рынке",
    "все игры",
    "всех игр",
    "игры стали",
    "игры превратились",
    "the game industry",
    "the industry",
    "all games",
    "the market",
)

_LIMITED_INTERPRETATION_PATTERNS = (
    "показывает",
    "показывала",
    "показывает,",
    "помогает понять",
    "иллюстрирует",
    "хорошо показывает",
    "можно рассматривать",
    "представляет собой",
    "suggests",
    "illustrates",
    "shows that",
)

_YEAR_PATTERN = re.compile(r"\b(?:1[0-9]{3}|20[0-9]{2}|9[0-9]{3})\b")


def _fold(text: str) -> str:
    return " ".join(str(text or "").casefold().split())


def _contains_any(text: str, patterns: tuple[str, ...]) -> bool:
    folded = _fold(text)
    return any(pattern in folded for pattern in patterns)


def classify_claim(text: str) -> tuple[ClaimType, int, CausalLevel]:
    """Conservatively classify a claim from surface language.

    This is a fallback classifier for QC calibration. LLM-produced structured
    metadata may supply the same fields, but deterministic gate logic remains
    responsible for the final verdict.
    """
    folded = _fold(text)
    if _contains_any(folded, _STRONG_CAUSAL_PATTERNS):
        return (
            "generalization" if _contains_any(folded, _GENERALIZATION_PATTERNS) else "causality",
            4,
            "C4",
        )

    if _contains_any(folded, _CAUSAL_PATTERNS):
        broad = _contains_any(folded, _GENERALIZATION_PATTERNS)
        return ("generalization" if broad else "causality", 3, "C3")

    if _contains_any(folded, _ASSOCIATION_PATTERNS):
        return ("interpretation", 1, "C1")

    if _contains_any(folded, _LIMITED_INTERPRETATION_PATTERNS):
        broad = _contains_any(folded, _GENERALIZATION_PATTERNS)
        return ("generalization" if broad else "interpretation", 2 if broad else 1, "C0")

    # A bounded factual claim with a date is treated as the safest class.
    if _YEAR_PATTERN.search(folded):
        return ("fact", 0, "C0")

    return ("fact", 0, "C0")


def estimate_evidence_strength(
    *,
    claim: dict[str, Any],
    evidence: dict[str, dict[str, Any]],
    sources: dict[str, dict[str, Any]],
) -> tuple[int, int, int]:
    evidence_ids = [
        str(value).strip()
        for value in claim.get("evidence_ids", [])
        if str(value).strip()
    ]
    source_ids = [
        str(value).strip()
        for value in claim.get("source_ids", [])
        if str(value).strip()
    ]

    resolved_evidence = [
        evidence[evidence_id]
        for evidence_id in evidence_ids
        if evidence_id in evidence
    ]
    direct_evidence = [
        item
        for item in resolved_evidence
        if str(item.get("excerpt") or "").strip()
        and str(item.get("source_id") or "").strip()
        in sources
    ]
    linked_source_ids = {
        str(item.get("source_id") or "").strip()
        for item in direct_evidence
        if str(item.get("source_id") or "").strip()
    }

    evidence_count = len(resolved_evidence)
    source_count = len({source_id for source_id in source_ids if source_id in sources})

    if not resolved_evidence:
        return 0, evidence_count, source_count
    if not direct_evidence:
        return 1, evidence_count, source_count
    if len(linked_source_ids) >= 2:
        return 4, evidence_count, source_count
    return 3, evidence_count, source_count


def assess_claim(
    claim: dict[str, Any],
    *,
    evidence: dict[str, dict[str, Any]],
    sources: dict[str, dict[str, Any]],
) -> ClaimStrengthAssessment:
    claim_id = str(claim.get("id") or claim.get("claim_id") or "").strip()
    text = str(claim.get("text") or "").strip()

    if not text:
        return ClaimStrengthAssessment(
            claim_id=claim_id,
            text=text,
            claim_type=None,
            claim_strength=0,
            causal_level="C0",
            evidence_strength=0,
            evidence_count=0,
            source_count=0,
            support_index=0,
            verdict="PASS",
            repair_action="NONE",
            reason="claim text is missing; claim-strength check is skipped",
        )

    claim_type, claim_strength, causal_level = classify_claim(text)
    evidence_strength, evidence_count, source_count = estimate_evidence_strength(
        claim=claim,
        evidence=evidence,
        sources=sources,
    )
    support_index = evidence_strength - claim_strength

    if support_index >= 0:
        verdict: Verdict = "PASS"
        repair_action: RepairAction = "NONE"
        reason = (
            f"claim strength {claim_strength} ({_CLAIM_STRENGTH_LABELS[claim_strength]}) "
            f"is covered by evidence strength {evidence_strength}"
        )
    elif support_index == -1:
        verdict = "REVIEW"
        repair_action = "WEAKEN" if claim_type in {"causality", "generalization"} else "ADD_EVIDENCE"
        reason = (
            f"claim strength {claim_strength} exceeds evidence strength "
            f"{evidence_strength} by one level"
        )
    elif evidence_strength == 0:
        verdict = "FAIL"
        repair_action = "REMOVE" if claim_strength >= 3 else "ADD_EVIDENCE"
        reason = "claim has no resolvable evidence"
    else:
        verdict = "FAIL"
        repair_action = "WEAKEN"
        reason = (
            f"claim strength {claim_strength} exceeds evidence strength "
            f"{evidence_strength} by at least two levels"
        )

    return ClaimStrengthAssessment(
        claim_id=claim_id,
        text=text,
        claim_type=claim_type,
        claim_strength=claim_strength,
        causal_level=causal_level,
        evidence_strength=evidence_strength,
        evidence_count=evidence_count,
        source_count=source_count,
        support_index=support_index,
        verdict=verdict,
        repair_action=repair_action,
        reason=reason,
    )


def assess_claims(
    claims: list[dict[str, Any]],
    *,
    evidence_items: list[dict[str, Any]],
    source_items: list[dict[str, Any]],
) -> list[ClaimStrengthAssessment]:
    evidence = {
        str(item.get("id") or item.get("evidence_id") or "").strip(): item
        for item in evidence_items
        if isinstance(item, dict) and str(item.get("id") or item.get("evidence_id") or "").strip()
    }
    sources = {
        str(item.get("id") or item.get("source_id") or "").strip(): item
        for item in source_items
        if isinstance(item, dict) and str(item.get("id") or item.get("source_id") or "").strip()
    }
    return [
        assess_claim(claim, evidence=evidence, sources=sources)
        for claim in claims
        if isinstance(claim, dict)
    ]


def summarize_assessments(items: list[ClaimStrengthAssessment]) -> dict[str, Any]:
    counts = {value: 0 for value in ("PASS", "REVIEW", "FAIL")}
    by_type: dict[str, int] = {}
    for item in items:
        counts[item.verdict] += 1
        if item.claim_type:
            by_type[item.claim_type] = by_type.get(item.claim_type, 0) + 1

    return {
        "claims": len(items),
        "verdicts": counts,
        "claim_types": by_type,
        "pass_rate": round(counts["PASS"] / max(len(items), 1), 3),
        "review_rate": round(counts["REVIEW"] / max(len(items), 1), 3),
        "fail_rate": round(counts["FAIL"] / max(len(items), 1), 3),
    }
