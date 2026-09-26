from content_factory.content_run import ContentRunStore
from content_factory.product_http import ProductHandler


class DummyRunsHandler(ProductHandler):
    def __init__(self, path="/api/runs"):
        self.path = path
        self.status = None
        self.body = None
        self.content_runs = None
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
    store.close()

    reopened = ContentRunStore(path)
    loaded = reopened.get(created.run_id)
    listed = reopened.list()
    reopened.close()

    assert loaded is not None
    assert loaded.to_dict() == created.to_dict()
    assert listed[0].run_id == created.run_id


def test_post_runs_creates_draft():
    handler = DummyRunsHandler()
    handler.content_runs = ContentRunStore(":memory:")
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


def test_get_runs_lists_and_gets_one():
    store = ContentRunStore(":memory:")
    created = store.create(title="One", brief="Brief")

    handler = DummyRunsHandler("/api/runs")
    handler.content_runs = store
    ProductHandler.do_GET(handler)

    assert handler.status == 200
    assert handler.body["runs"][0]["run_id"] == created.run_id

    handler = DummyRunsHandler(f"/api/runs/{created.run_id}")
    handler.content_runs = store
    ProductHandler.do_GET(handler)

    assert handler.status == 200
    assert handler.body["run_id"] == created.run_id
    store.close()


def test_get_missing_run_returns_404():
    store = ContentRunStore(":memory:")
    handler = DummyRunsHandler("/api/runs/run-missing")
    handler.content_runs = store

    ProductHandler.do_GET(handler)

    assert handler.status == 404
    assert handler.body["error"] == "content run not found"
    store.close()
