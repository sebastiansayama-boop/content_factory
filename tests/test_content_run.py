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


class FakeVerticalSlice:
    def __init__(self):
        pass

    def run(self, *, run_id, brief, formats):
        assert run_id.startswith("run-")
        assert brief == "Research this topic."
        assert formats == ["article", "social_post", "visual_card"]
        from content_factory.vertical_slice import VerticalSliceResult

        return VerticalSliceResult(
            run_id=run_id,
            brief=brief,
            research={
                "topic": "Test topic",
                "summary": "Research summary",
                "claims": [{"id": "claim-1", "text": "A fact", "source_ids": ["source-1"]}],
                "sources": [{"id": "source-1", "title": "Test source", "url": "https://example.com/source"}],
                "editorial_angles": ["Test angle"],
            },
            package={
                "topic": "Test topic",
                "package": [{
                    "id": "test-article-v1",
                    "format": "article",
                    "title": "Test article",
                    "content": "Generated content",
                    "claim_refs": ["claim-1"],
                    "source_refs": ["source-1"],
                }],
            },
            quality={"status": "PASS", "errors": [], "asset_count": 1, "claim_count": 1, "source_count": 1},
        )


def test_execute_endpoint_runs_vertical_slice_and_persists_result(tmp_path):
    store = ContentRunStore(tmp_path / "runs.sqlite3")
    created = store.create(
        title="Test run",
        brief="Research this topic.",
        formats=("article", "social_post", "visual_card"),
    )

    class RunsHandler(DummyRunsHandler):
        content_runs = store
        vertical_slice_factory = FakeVerticalSlice

    handler = RunsHandler(f"/api/runs/{created.run_id}/execute")
    handler.content_runs = store
    ProductHandler.do_POST(handler)

    assert handler.status == 200
    assert handler.body["status"] == "REVIEW"
    assert handler.body["result"]["quality"]["status"] == "PASS"
    assert handler.body["result"]["research"]["claims"][0]["id"] == "claim-1"
    assert store.get(created.run_id).result["package"]["package"][0]["id"] == "test-article-v1"
    store.close()


def test_execute_failure_marks_run_failed(tmp_path):
    store = ContentRunStore(tmp_path / "runs.sqlite3")
    created = store.create(title="Test run", brief="Research this topic.")

    class FailingVerticalSlice:
        def run(self, **kwargs):
            raise ValueError("research failed")

    class RunsHandler(DummyRunsHandler):
        content_runs = store
        vertical_slice_factory = FailingVerticalSlice

    handler = RunsHandler(f"/api/runs/{created.run_id}/execute")
    handler.content_runs = store
    ProductHandler.do_POST(handler)

    assert handler.status == 400
    assert handler.body["error"] == "research failed"
    assert store.get(created.run_id).status == "FAILED"
    store.close()
