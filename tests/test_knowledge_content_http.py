from content_factory.content_run import ContentRunStore
from content_factory.product_http import ProductHandler


class DummyBuildHandler(ProductHandler):
    def __init__(self, path):
        self.path = path
        self.status = None
        self.body = None
        self.content_runs = None
        self.payload = {}
        self.response_headers = {}

    def _protect_product_api(self):
        return True

    def _json(self, status, body, retry_after=None):
        self.status = status
        self.body = body


def test_build_endpoint_persists_knowledge_content_graph(tmp_path, monkeypatch):
    import content_factory.product_http as product_http

    store = ContentRunStore(tmp_path / "runs.sqlite3")
    created = store.create(
        title="Thai spirits",
        brief="Explain spirit house offerings.",
        audience="General audience",
        goal="Create a short video",
        formats=("short_video",),
        constraints=("no alcohol",),
    )

    class FakeKnowledge:
        pass

    class FakeService:
        knowledge = FakeKnowledge()

    class Builder:
        def __init__(self, workspace, knowledge):
            assert knowledge is not None

        def build(self, **kwargs):
            assert kwargs["run_id"] == created.run_id
            return {
                "editorial": {"selected_idea": {"idea_id": "idea-1"}, "ideas": []},
                "content_spec": {"spec_id": "spec-1"},
                "script": {"script_id": "script-1", "units": []},
                "production_plan": {"production_plan_id": "production-1", "asset_requests": []},
                "knowledge": {"claim_refs": ["kc-1"], "evidence_refs": ["ke-1"]},
            }

    monkeypatch.setattr(product_http, "KnowledgeContentBuilder", Builder)

    handler = DummyBuildHandler(f"/api/runs/{created.run_id}/build")
    handler.content_runs = store
    handler.service = FakeService()
    handler.workspace = object()

    ProductHandler.do_POST(handler)

    assert handler.status == 200
    assert handler.body["status"] == "REVIEW"
    assert handler.body["result"]["content_spec"]["spec_id"] == "spec-1"
    assert handler.body["result"]["script"]["script_id"] == "script-1"
    assert handler.body["result"]["production_plan"]["production_plan_id"] == "production-1"
    store.close()
