from content_factory.content_run import ContentRunStore
from content_factory.product_http import ProductHandler


class DummyRunsHandler(ProductHandler):
    def __init__(self, path="/api/runs"):
        self.path = path
        self.status = None
        self.body = None
        self.content_runs = None
        self.content_run_planner = None
        self.payload = {}
        self.response_headers = {}

    def _protect_product_api(self):
        return True

    def _body(self):
        return self.payload

    def _json(self, status, body, retry_after=None):
        self.status = status
        self.body = body


def test_content_run_store_persists_and_lists(tmp_path):
    path = tmp_path / "content-runs.sqlite3"
    store = ContentRunStore(path)
    created = store.create(
        title="Thai spirits",
        brief="Explain why Red Fanta is offered at spirit houses.",
        audience="General audience",
        goal="Prepare a research-backed video",
        formats=("long_video", "telegram"),
        constraints=("cite sources",),
    )
    planned = store.save_plan(
        created.run_id,
        {"objective": "Explain the topic", "deliverables": [{"format": "long_video"}]},
    )
    store.close()

    reopened = ContentRunStore(path)
    loaded = reopened.get(created.run_id)
    listed = reopened.list()
    reopened.close()

    assert loaded is not None
    assert loaded.to_dict() == planned.to_dict()
    assert loaded.status == "PLANNING"
    assert loaded.plan["objective"] == "Explain the topic"
    assert listed[0].run_id == created.run_id


def test_post_runs_creates_draft(tmp_path):
    handler = DummyRunsHandler()
    handler.content_runs = ContentRunStore(tmp_path / "runs.sqlite3")
    handler.payload = {
        "title": "Thai spirits",
        "brief": "Explain Red Fanta offerings.",
        "audience": "General audience",
        "goal": "Create a research-backed episode",
        "formats": ["long_video", "telegram"],
        "constraints": ["cite sources"],
    }

    ProductHandler.do_POST(handler)

    assert handler.status == 201
    assert handler.body["status"] == "DRAFT"
    assert handler.body["title"] == "Thai spirits"
    assert handler.content_runs.get(handler.body["run_id"]) is not None


def test_plan_endpoint_persists_runtime_backed_plan(tmp_path):
    store = ContentRunStore(tmp_path / "runs.sqlite3")
    created = store.create(
        title="Thai spirits",
        brief="Explain Red Fanta offerings.",
        formats=("long_video", "telegram"),
    )

    class Planner:
        def plan(self, **kwargs):
            assert kwargs["run_id"] == created.run_id
            return {
                "objective": "Explain the topic",
                "research_questions": ["Why is this offering used?"],
                "source_requirements": ["Thai-language sources"],
                "deliverables": [
                    {"format": "long_video", "purpose": "episode"},
                    {"format": "telegram", "purpose": "post"},
                ],
                "runtime": {"work_item_id": "content-run-plan-test"},
            }

    handler = DummyRunsHandler(f"/api/runs/{created.run_id}/plan")
    handler.content_runs = store
    handler.content_run_planner = Planner()

    ProductHandler.do_POST(handler)

    assert handler.status == 200
    assert handler.body["status"] == "PLANNING"
    assert handler.body["plan"]["runtime"]["work_item_id"] == "content-run-plan-test"
    assert store.get(created.run_id).plan["objective"] == "Explain the topic"
    store.close()


def test_plan_failure_marks_run_failed(tmp_path):
    store = ContentRunStore(tmp_path / "runs.sqlite3")
    created = store.create(title="One", brief="Brief")

    class Planner:
        def plan(self, **kwargs):
            raise ValueError("planner failed")

    handler = DummyRunsHandler(f"/api/runs/{created.run_id}/plan")
    handler.content_runs = store
    handler.content_run_planner = Planner()

    ProductHandler.do_POST(handler)

    assert handler.status == 400
    assert handler.body["error"] == "planner failed"
    assert store.get(created.run_id).status == "FAILED"
    store.close()


def test_get_runs_lists_and_gets_one(tmp_path, monkeypatch):
    import http.client
    import threading
    from http.server import ThreadingHTTPServer

    store = ContentRunStore(tmp_path / "runs.sqlite3")
    created = store.create(title="One", brief="Brief")

    class RunsHandler(ProductHandler):
        content_runs = store

    monkeypatch.setenv("FACTORY_API_TOKEN", "test-token")
    server = ThreadingHTTPServer(("127.0.0.1", 0), RunsHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        connection = http.client.HTTPConnection(*server.server_address)
        connection.request("GET", "/api/runs", headers={"Authorization": "Bearer test-token"})
        response = connection.getresponse()
        body = response.read()
        assert response.status == 200
        assert created.run_id in body.decode("utf-8")

        connection.request(
            "GET",
            f"/api/runs/{created.run_id}",
            headers={"Authorization": "Bearer test-token"},
        )
        response = connection.getresponse()
        body = response.read()
        assert response.status == 200
        assert created.run_id in body.decode("utf-8")
        connection.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
        store.close()


def test_get_missing_run_returns_404(tmp_path):
    store = ContentRunStore(tmp_path / "runs.sqlite3")
    handler = DummyRunsHandler("/api/runs/run-missing")
    handler.content_runs = store

    ProductHandler.do_GET(handler)

    assert handler.status == 404
    assert handler.body["error"] == "content run not found"
    store.close()


def test_execute_persists_durable_knowledge_refs(tmp_path, monkeypatch):
    from content_factory import product_http

    store = ContentRunStore(tmp_path / "runs.sqlite3")
    created = store.create(title="Future cities", brief="Research future cities", formats=("article",))

    class FakeKnowledge:
        def counts(self):
            return {"sources": 1, "evidence": 1, "claims": 1, "accepted_claims": 1, "candidate_claims": 0, "editorial_angles": 0, "runs": 1}

    class FakeService:
        knowledge = FakeKnowledge()

    class FakeResult:
        run_id = created.run_id
        brief = created.brief
        research = {
            "claims": [{"id": "claim-1", "text": "A durable claim"}],
            "sources": [{"id": "source-1", "title": "Source", "url": "https://example.com"}],
            "knowledge_refs": {
                "claims": {"claim-1": "kc-durable"},
                "sources": {"source-1": "ks-durable"},
                "evidence": {"evidence-1": "ke-durable"},
            },
        }
        package = {"topic": "Future cities", "package": [{"id": "asset-1", "format": "article", "content": "draft", "claim_refs": ["claim-1"], "source_refs": ["source-1"]}]}
        quality = {"status": "PASS"}

    class FakeSlice:
        def __init__(self, knowledge_store=None):
            assert knowledge_store is not None
        def run(self, **kwargs):
            assert kwargs["run_id"] == created.run_id
            return FakeResult()
        @staticmethod
        def to_dict(result):
            return {"run_id": result.run_id, "brief": result.brief, "research": result.research, "package": result.package, "quality": result.quality}

    handler = DummyRunsHandler(f"/api/runs/{created.run_id}/execute")
    handler.content_runs = store
    handler.service = FakeService()
    monkeypatch.setattr(product_http, "ContentFactoryVerticalSlice", FakeSlice)

    ProductHandler.do_POST(handler)

    assert handler.status == 200
    persisted = store.get(created.run_id)
    assert persisted is not None
    assert persisted.status == "REVIEW"
    assert persisted.result["research"]["knowledge_refs"] == FakeResult.research["knowledge_refs"]
    store.close()


def test_promote_knowledge_endpoint_requires_decision_and_returns_revision(tmp_path):
    from content_factory.knowledge import KnowledgeStore

    knowledge = KnowledgeStore(tmp_path / "knowledge.sqlite3")
    payload = {
        "claims": [{
            "id": "claim-1",
            "text": "Automobiles changed expectations about urban mobility.",
            "confidence": "high",
            "source_ids": ["source-1"],
            "evidence_ids": ["evidence-1"],
            "scope": "urban mobility",
            "known_unknowns": [],
        }],
        "sources": [{
            "id": "source-1",
            "title": "Example",
            "url": "https://example.com/cities",
        }],
        "evidence": [{
            "id": "evidence-1",
            "source_id": "source-1",
            "excerpt": "Automobiles changed expectations about urban mobility.",
            "locator": "paragraph",
            "provenance": "example",
        }],
    }
    knowledge.capture(run_id="run-promotion", research=payload)
    claim_id = knowledge._connection.execute(
        "SELECT claim_id FROM knowledge_claims"
    ).fetchone()["claim_id"]

    class Service:
        pass

    service = Service()
    service.knowledge = knowledge
    handler = DummyRunsHandler(f"/api/knowledge/{claim_id}/promote")
    handler.service = service
    handler.payload = {"decision_ref": "DEC-HTTP-001"}

    ProductHandler.do_POST(handler)

    assert handler.status == 200
    assert handler.body["claim_id"] == claim_id
    assert handler.body["status"] == "ACCEPTED"
    assert handler.body["decision_ref"] == "DEC-HTTP-001"
    assert handler.body["revision_id"].startswith(f"{claim_id}-r")
    assert handler.body["promoted_at"]
    knowledge.close()
