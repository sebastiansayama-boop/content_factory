from content_factory.factory_control import FactoryControlStore


def test_experience_records_capture_all_user_decisions(tmp_path):
    store = FactoryControlStore(tmp_path / "control.sqlite3")

    decisions = ["ACCEPT", "EDIT", "REGENERATE", "REJECT"]
    for decision in decisions:
        record = store.record_experience(
            run_id="run-1",
            prompt={"brief": "История компьютерных игр"},
            context={"platform": "telegram", "series_episode": 2},
            generated={"text": f"candidate-{decision.lower()}"},
            decision=decision,
            final={"text": "final"} if decision in {"ACCEPT", "EDIT"} else None,
            edits=[{"field": "text", "before": "old", "after": "final"}] if decision == "EDIT" else [],
            reason="too_generic" if decision == "EDIT" else "",
            qc={"status": "PASSED"},
            provenance={"run_id": "run-1", "source": "human"},
        )
        assert record["example_id"].startswith("ex-")
        assert record["decision"] == decision

    records = store.list_experiences("run-1")
    assert [record["decision"] for record in records] == decisions
    assert records[1]["edits"][0]["before"] == "old"
    assert records[1]["final"]["text"] == "final"
    assert records[0]["provenance"]["source"] == "human"
    store.close()


def test_experience_record_rejects_unknown_decision(tmp_path):
    store = FactoryControlStore(tmp_path / "control.sqlite3")
    try:
        store.record_experience(
            run_id="run-1",
            prompt="prompt",
            generated="generated",
            decision="MAYBE",
        )
    except ValueError as exc:
        assert "experience decision" in str(exc)
    else:
        raise AssertionError("unknown experience decision was accepted")
    store.close()
