from __future__ import annotations

from typing import Any


class SeriesContractError(ValueError):
    """Raised when a persisted series package violates continuity or provenance."""


def _nonempty(value: Any) -> str:
    return str(value or "").strip()


def validate_series_package(
    package: dict[str, Any],
    *,
    previous_package: dict[str, Any] | None = None,
    previous_run_id: str | None = None,
) -> None:
    series = package.get("series")
    if not isinstance(series, dict):
        return

    required = ("series_id", "title", "episode", "central_question", "unresolved", "next_required_transition", "story_state")
    missing = [key for key in required if key not in series]
    if missing:
        raise SeriesContractError(f"series missing required fields: {', '.join(missing)}")

    try:
        episode = int(series.get("episode"))
    except (TypeError, ValueError):
        raise SeriesContractError("series episode must be an integer") from None
    if episode < 1:
        raise SeriesContractError("series episode must be >= 1")

    central_question = _nonempty(series.get("central_question"))
    if not central_question:
        raise SeriesContractError("series central_question is required")

    state = series.get("story_state")
    if not isinstance(state, dict):
        raise SeriesContractError("series story_state is required")
    if _nonempty(state.get("central_question")) != central_question:
        raise SeriesContractError("story_state central_question must match series central_question")

    if not isinstance(state.get("established"), list) or not state.get("established"):
        raise SeriesContractError("story_state established must be a non-empty list")
    if not isinstance(state.get("unresolved"), list):
        raise SeriesContractError("story_state unresolved must be a list")
    if not _nonempty(state.get("next_required_transition")):
        raise SeriesContractError("story_state next_required_transition is required")

    claims = package.get("claims")
    sources = package.get("sources")
    evidence = package.get("evidence")
    if not isinstance(claims, list) or not isinstance(sources, list) or not isinstance(evidence, list):
        raise SeriesContractError("series package requires claims, sources and evidence lists")

    source_ids = {_nonempty(item.get("id")) for item in sources if isinstance(item, dict)}
    evidence_ids = {_nonempty(item.get("id")) for item in evidence if isinstance(item, dict)}
    claim_ids = {_nonempty(item.get("id")) for item in claims if isinstance(item, dict)}
    source_ids.discard("")
    evidence_ids.discard("")
    claim_ids.discard("")

    for item in evidence:
        if not isinstance(item, dict):
            raise SeriesContractError("evidence entries must be objects")
        evidence_id = _nonempty(item.get("id"))
        source_id = _nonempty(item.get("source_id"))
        if not evidence_id or not source_id:
            raise SeriesContractError("evidence requires id and source_id")
        if source_id not in source_ids:
            raise SeriesContractError(f"evidence {evidence_id} references unknown source {source_id}")

    for claim in claims:
        if not isinstance(claim, dict):
            raise SeriesContractError("claim entries must be objects")
        claim_id = _nonempty(claim.get("id"))
        if not claim_id:
            raise SeriesContractError("claim requires id")
        claim_sources = claim.get("source_ids")
        claim_evidence = claim.get("evidence_ids")
        if not isinstance(claim_sources, list) or not claim_sources:
            raise SeriesContractError(f"claim {claim_id} requires source_ids")
        if not isinstance(claim_evidence, list) or not claim_evidence:
            raise SeriesContractError(f"claim {claim_id} requires evidence_ids")
        if not {_nonempty(x) for x in claim_sources}.issubset(source_ids):
            raise SeriesContractError(f"claim {claim_id} references unknown source")
        if not {_nonempty(x) for x in claim_evidence}.issubset(evidence_ids):
            raise SeriesContractError(f"claim {claim_id} references unknown evidence")

    state_claims = {_nonempty(x) for x in (state.get("claims") or [])}
    state_evidence = {_nonempty(x) for x in (state.get("evidence") or [])}
    if not state_claims or not state_claims.issubset(claim_ids):
        raise SeriesContractError("story_state claims must reference existing claims")
    if not state_evidence or not state_evidence.issubset(evidence_ids):
        raise SeriesContractError("story_state evidence must reference existing evidence")

    if previous_package is None:
        return

    previous_series = previous_package.get("series")
    if not isinstance(previous_series, dict):
        raise SeriesContractError("previous package has no series state")
    try:
        previous_episode = int(previous_series.get("episode"))
    except (TypeError, ValueError):
        raise SeriesContractError("previous series episode must be an integer") from None

    if _nonempty(series.get("series_id")) != _nonempty(previous_series.get("series_id")):
        raise SeriesContractError("series_id must remain stable across episodes")
    if episode != previous_episode + 1:
        raise SeriesContractError("series episode must increment by exactly one")
    if central_question != _nonempty(previous_series.get("central_question")):
        raise SeriesContractError("central_question must remain stable across episodes")

    previous_state = previous_series.get("story_state")
    if not isinstance(previous_state, dict):
        raise SeriesContractError("previous series story_state is required")
    previous_established = previous_state.get("established") or []
    current_established = state.get("established") or []
    if not set(map(str, previous_established)).issubset(set(map(str, current_established))):
        raise SeriesContractError("established knowledge must be preserved and extended")
    if state.get("unresolved") == previous_state.get("unresolved"):
        raise SeriesContractError("unresolved questions must change between episodes")
    if not _nonempty(series.get("next_required_transition")):
        raise SeriesContractError("next_required_transition is required")

    expected_previous_run_id = _nonempty(series.get("previous_run_id"))
    if previous_run_id is not None and expected_previous_run_id != _nonempty(previous_run_id):
        raise SeriesContractError("previous_run_id does not match persisted predecessor")
