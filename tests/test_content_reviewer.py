from content_factory.content_reviewer import ContentReviewer


class FakeWorkspace:
    class Factory:
        _capability = type("Capability", (), {"capability_id": "test.llm"})()

    factory = Factory()

    def __init__(self, payload):
        self.payload = payload

    def _run_product_work_item(self, item):
        return {
            "work_item_id": item.work_item_id,
            "operation_id": item.operation_id,
            "state": "ACCEPTED",
            "execution": {
                "execution_id": "exec-review-1",
                "output_revision_id": "review-output-1",
                "output": self.payload,
            },
        }


def test_reviewer_returns_bounded_review_contract():
    workspace = FakeWorkspace(
        '{"status":"REVISE","issues":["tone is too formal"],'
        '"required_changes":["use a more conversational tone"],'
        '"checked_claims":["kc-1"],"confidence":0.82}'
    )
    review = ContentReviewer(workspace).review(
        run_id="run-1",
        brief="Explain the topic simply.",
        audience="general",
        goal="Telegram post",
        result={
            "content_spec": {"format": "social_post"},
            "knowledge": {"claim_refs": ["kc-1"]},
            "script": {"units": [{"unit_id": "u1", "text": "Draft"}]},
        },
    )
    assert review["status"] == "REVISE"
    assert review["required_changes"] == ["use a more conversational tone"]
    assert review["checked_claims"] == ["kc-1"]
    assert review["confidence"] == 0.82
    assert review["runtime"]["execution_id"] == "exec-review-1"
