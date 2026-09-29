from __future__ import annotations

import re
from typing import Any


FUTURE_HISTORY_TERMS = {
    "future",
    "futures",
    "prophecy",
    "prophecies",
    "prophetic",
    "eschatology",
    "utopia",
    "utopian",
    "science",
    "fiction",
    "futurism",
    "futurist",
    "verne",
    "wells",
    "robida",
    "watkins",
    "ancient",
    "medieval",
    "historical",
    "history",
    "time",
    "society",
    "technology",
    "technological",
    "prediction",
    "predictions",
    "forecast",
    "forecasts",
    "speculation",
    "speculative",
    "gilgamesh",
    "augustine",
    "joachim",
}


def _tokens(value: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9-]{3,}", value.lower())
        if token not in {"the", "and", "for", "with", "that", "this", "from", "about", "into"}
    }


def _future_history_relevance(text: str) -> int:
    return len(_tokens(text) & FUTURE_HISTORY_TERMS)


def _generic_relevance(brief: str, text: str) -> float:
    brief_tokens = _tokens(brief)
    text_tokens = _tokens(text)
    if not brief_tokens or not text_tokens:
        return 0.0
    return len(brief_tokens & text_tokens) / len(brief_tokens)


def is_relevant_source(*, brief: str, title: str, extract: str) -> bool:
    material = f"{title} {extract}"
    lowered_brief = brief.lower()
    lowered = material.lower()

    future_history = any(token in lowered_brief for token in ("future", "будущ")) and any(
        token in lowered_brief for token in ("history", "histor", "истори", "древ", "эпох")
    )
    if future_history:
        return _future_history_relevance(material) >= 2

    return _generic_relevance(brief, material) >= 0.12


def is_relevant_claim(*, brief: str, claim: str, evidence: str) -> bool:
    lowered_brief = brief.lower()
    combined = f"{claim} {evidence}"
    future_history = any(token in lowered_brief for token in ("future", "будущ")) and any(
        token in lowered_brief for token in ("history", "histor", "истори", "древ", "эпох")
    )
    if future_history:
        claim_terms = _future_history_relevance(combined)
        return claim_terms >= 2

    return _generic_relevance(brief, combined) >= 0.10


def validate_research_relevance(*, brief: str, research: dict[str, Any]) -> dict[str, Any]:
    claims = research.get("claims", [])
    sources = research.get("sources", [])
    evidence = research.get("evidence", [])

    if not isinstance(claims, list) or not isinstance(sources, list) or not isinstance(evidence, list):
        return {
            "status": "FAIL",
            "reason": "claims, sources and evidence must be arrays",
            "relevant_claim_count": 0,
            "relevant_source_count": 0,
            "claim_count": len(claims) if isinstance(claims, list) else 0,
            "source_count": len(sources) if isinstance(sources, list) else 0,
        }

    source_by_id = {
        str(item.get("id")): item
        for item in sources
        if isinstance(item, dict) and item.get("id")
    }
    evidence_by_id = {
        str(item.get("id")): item
        for item in evidence
        if isinstance(item, dict) and item.get("id")
    }

    relevant_source_ids: set[str] = set()
    relevant_source_types: set[str] = set()
    relevant_claims = 0
    rejected_claim_ids: list[str] = []
    for claim in claims:
        if not isinstance(claim, dict):
            continue
        excerpts = []
        for evidence_id in claim.get("evidence_ids", []):
            item = evidence_by_id.get(str(evidence_id))
            if isinstance(item, dict):
                excerpts.append(str(item.get("excerpt", "")))
        if is_relevant_claim(
            brief=brief,
            claim=str(claim.get("text", "")),
            evidence=" ".join(excerpts),
        ):
            relevant_claims += 1
            for source_id in claim.get("source_ids", []):
                if str(source_id) in source_by_id:
                    relevant_source_ids.add(str(source_id))
                    source_type = str(source_by_id[str(source_id)].get("source_type", "unknown"))
                    relevant_source_types.add(source_type)
        elif claim.get("id"):
            rejected_claim_ids.append(str(claim["id"]))

    future_history = any(token in brief.lower() for token in ("future", "будущ")) and any(
        token in brief.lower() for token in ("history", "histor", "истори", "древ", "эпох")
    )
    min_claims = 3 if future_history else 1
    min_sources = 3 if future_history else 1
    min_source_types = 2 if future_history else 1
    passed = (\n        relevant_claims >= min_claims\n        and len(relevant_source_ids) >= min_sources\n        and len(relevant_source_types) >= min_source_types\n    )

    return {
        "status": "PASS" if passed else "FAIL",
        "relevant_claim_count": relevant_claims,
        "relevant_source_count": len(relevant_source_ids),\n        "relevant_source_types": sorted(relevant_source_types),\n        "minimum_source_types": min_source_types,
        "claim_count": len(claims),
        "source_count": len(sources),
        "rejected_claim_ids": rejected_claim_ids,
        "minimum_claims": min_claims,
        "minimum_sources": min_sources,
        "reason": (
            "research is sufficiently relevant to the requested brief"
            if passed
            else "research does not contain enough relevant claims, sources, and source diversity"
        ),
    }
