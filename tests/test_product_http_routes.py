from content_factory.content_run import ContentRunStore
from content_factory.product_http import ProductHandler


class DummyHandler(ProductHandler):
    def __init__(self, path, body):
        self.path = path
        self.body = body
        self.status = None
        self.response_headers = {}
        self.content_runs = None
        self.service = None
        self.workspace = None
        self.content_run_planner = None

    def _protect_product_api(self):
        return True

    def _body(self):
        return self.body

    def _json(self, status, body, retry_after=None):
        self.status = status
        self.response = body


class Control:
    def __init__(self):
        self.events = []

    def record(self, *args, **kwargs):
        self.events.append((args, kwargs))

    def timeline(self, run_id):
        return []

    def replay_plan(self, run, *, changed_claim_ids, changes=None):
        return {
            "run_id": run["run_id"],
            "mode": "INCREMENTAL_REPLAY",
            "preserve": ["research", "knowledge", "editorial", "content_spec", "script"],
            "revise": [],
            "regenerate_asset_ids": [],
            "retain_asset_ids": [],
            "rerun": ["production", "assembly", "qc", "approval", "export"],
            "changed_claim_ids": changed_claim_ids,
            "changes": changes or {},
        }


class Service:
    def __init__(self):
        self.control = Control()


def test_create_run_is_durable(tmp_path):
    store = ContentRunStore(tmp_path / "runs.sqlite3")
    handler = DummyHandler("/api/runs", {
        "title": "Test",
        "brief": "A brief",
        "audience": "general",
        "goal": "video",
        "formats": ["short_video"],
        "constraints": [],
    })
    handler.content_runs = store
    handler.service = Service()
    ProductHandler.do_POST(handler)

    assert handler.status == 201
    run_id = handler.response["run_id"]
    assert store.get(run_id) is not None
    assert store.get(run_id).status == "DRAFT"
    store.close()


def test_replay_endpoint_is_read_only_and_returns_plan(tmp_path):
    store = ContentRunStore(tmp_path / "runs.sqlite3")
    run = store.create(
        title="Test",
        brief="A brief",
        audience="general",
        goal="video",
        formats=("short_video",),
        constraints=(),
    )
    handler = DummyHandler(f"/api/runs/{run.run_id}/replay", {"changed_claim_ids": ["kc-1"]})
    handler.content_runs = store
    handler.service = Service()
    ProductHandler.do_POST(handler)

    assert handler.status == 200
    assert handler.response["mode"] == "INCREMENTAL_REPLAY"
    assert handler.response["changed_claim_ids"] == ["kc-1"]
    assert store.get(run.run_id).status == "DRAFT"
    store.close()
