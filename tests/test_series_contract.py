import pytest

from content_factory.series_contract import SeriesContractError, validate_series_package


def _package(episode=1, *, series_id="series-1", established=None, unresolved=None, previous_run_id=None):
    source = {"id": "source-1", "title": "Source", "url": "https://example.com/source"}
    evidence = {"id": "evidence-1", "source_id": "source-1", "excerpt": "Supporting evidence."}
    claim = {
        "id": "claim-1",
        "text": "Bounded factual claim.",
        "source_ids": ["source-1"],
        "evidence_ids": ["evidence-1"],
    }
    state = {
        "central_question": "When did the future become imaginable?",
        "established": established if established is not None else ["Earlier knowledge"],
        "unresolved": unresolved if unresolved is not None else ["Next question"],
        "next_required_transition": "Move to the next historical transition.",
        "claims": ["claim-1"],
        "evidence": ["evidence-1"],
    }
    return {
        "claims": [claim],
        "sources": [source],
        "evidence": [evidence],
        "series": {
            "series_id": series_id,
            "title": "Future",
            "episode": episode,
            "previous_run_id": previous_run_id,
            "central_question": state["central_question"],
            "unresolved": state["unresolved"],
            "next_required_transition": state["next_required_transition"],
            "story_state": state,
        },
    }


def test_series_contract_accepts_first_episode():
    validate_series_package(_package())


def test_series_contract_accepts_no_unresolved_questions():
    validate_series_package(_package(unresolved=[]))


def test_series_contract_rejects_unknown_provenance():
    package = _package()
    package["claims"][0]["evidence_ids"] = ["missing"]
    with pytest.raises(SeriesContractError, match="unknown evidence"):
        validate_series_package(package)


def test_series_contract_requires_sequential_episode_and_changed_unresolved():
    previous = _package(episode=3, established=["Earlier knowledge", "Prophecy"])
    current = _package(
        episode=5,
        established=["Earlier knowledge", "Prophecy", "Imagined societies"],
        unresolved=previous["series"]["unresolved"],
        previous_run_id="run-3",
    )
    with pytest.raises(SeriesContractError, match="increment by exactly one"):
        validate_series_package(current, previous_package=previous, previous_run_id="run-3")

    current["series"]["episode"] = 4
    with pytest.raises(SeriesContractError, match="unresolved questions must change"):
        validate_series_package(current, previous_package=previous, previous_run_id="run-3")


def test_series_contract_requires_previous_run_to_match_persisted_predecessor():
    previous = _package(episode=3, established=["Earlier knowledge", "Prophecy"])
    current = _package(
        episode=4,
        established=["Earlier knowledge", "Prophecy", "Imagined societies"],
        unresolved=["How did imagined cities become future projects?"],
        previous_run_id="wrong-run",
    )
    with pytest.raises(SeriesContractError, match="previous_run_id"):
        validate_series_package(current, previous_package=previous, previous_run_id="run-3")
