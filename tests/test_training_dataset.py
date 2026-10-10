from content_factory.training_dataset import build_preference_examples, build_sft_examples


def test_build_sft_examples_uses_final_after_edit():
    records = [{
        "example_id": "ex-1", "decision": "EDIT", "prompt": {"brief": "topic"},
        "generated": {"text": "draft"}, "final": {"text": "final"},
        "context": {"platform": "instagram"}, "qc": {"passed": True},
        "provenance": {"run_id": "run-1"},
    }]
    rows = build_sft_examples(records)
    assert rows[0]["completion"] == {"text": "final"}


def test_build_preference_examples_requires_explicit_pair():
    records = [{
        "example_id": "ex-2", "decision": "REJECT", "prompt": {"brief": "topic"},
        "preference": {"chosen": {"text": "good"}, "rejected": {"text": "bad"}},
    }]
    rows = build_preference_examples(records)
    assert rows[0]["chosen"]["text"] == "good"
    assert rows[0]["rejected"]["text"] == "bad"


def test_rejected_experience_is_not_fabricated_into_preference_data():
    records = [{"example_id": "ex-3", "decision": "REJECT", "prompt": {"brief": "topic"}, "generated": {"text": "bad"}}]
    assert build_preference_examples(records) == []
