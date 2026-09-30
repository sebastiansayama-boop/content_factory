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

def test_factory_research_review_then_builds_production(tmp_path, monkeypatch):
    monkeypatch.setenv("FACTORY_DATA_DIR", str(tmp_path))
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setenv("FACTORY_PROVIDER", "local")

    from content_factory.service import FactoryService
    from content_factory.workspace import ContentWorkspace

    service = FactoryService()
    try:
        handler = DummyHandler("/api/runs", {
            "title": "Test factory",
            "brief": "Explain a topic with evidence.",
            "audience": "general",
            "goal": "short video",
            "formats": ["short_video"],
            "constraints": [],
        })
        handler.content_runs = service.content_runs
        handler.service = service
        handler.workspace = ContentWorkspace(service)
        run = handler.content_runs.create(
            title="Test factory",
            brief="Explain a topic with evidence.",
            audience="general",
            goal="short video",
            formats=("short_video",),
            constraints=(),
        )

        first = DummyHandler(f"/api/runs/{run.run_id}/factory", {})
        first.content_runs = service.content_runs
        first.service = service
        first.workspace = handler.workspace
        ProductHandler.do_POST(first)

        assert first.status == 409
        assert first.response["candidates"]
        candidate_id = first.response["candidates"][0]["claim_id"]
        candidate = service.knowledge.get_claim(candidate_id)
        assert candidate.status == "CANDIDATE"
        assert service.content_runs.get(run.run_id).status == "RESEARCH_READY"

        service.knowledge.promote_claim(candidate_id, decision_ref="TEST-FACTORY-REVIEW")

        second = DummyHandler(f"/api/runs/{run.run_id}/factory", {})
        second.content_runs = service.content_runs
        second.service = service
        second.workspace = handler.workspace
        ProductHandler.do_POST(second)

        assert second.status == 200, second.response
        result = second.response["run"]["result"]
        assert result["content_spec"]["claim_refs"] == [candidate_id]
        assert result["production"]["status"] == "READY_FOR_REVIEW", [item for item in result["production"].get("qc", {}).get("checks", []) if not item["passed"]]
        assert second.response["qc"]["status"] == "PASSED"
        assert service.content_runs.get(run.run_id).status == "REVIEW"

        trace_get = DummyHandler(f"/api/runs/{run.run_id}/execution-trace", {})
        trace_get.content_runs = service.content_runs
        trace_get.service = service
        trace_get.workspace = handler.workspace
        ProductHandler.do_GET(trace_get)
        assert trace_get.status == 200, trace_get.response
        trace_events = trace_get.response["events"]
        trace_stages = [event["data"]["stage"] for event in trace_events if event["operation"] == "trace"]
        assert trace_stages[-7:] == ["RESEARCH", "EDITORIAL", "EDITORIAL", "PRODUCTION", "PRODUCTION", "QC", "QC"]
        assert "RESEARCH" in trace_stages
        assert "EDITORIAL" in trace_stages
        assert "PRODUCTION" in trace_stages
        assert "QC" in trace_stages
        assert all(event["work_item_id"] == run.run_id for event in trace_events)
        assert all(event["revision_id"] == f"content-run:{run.run_id}:r1" for event in trace_events)
        assert trace_events[-1]["data"]["decision"] == "ACCEPT"
        assert trace_events[-1]["data"]["result"]["status"] == "PASSED"

        persisted_events = service.runtime_store.load_events(run.run_id)
        assert [event["event_id"] for event in persisted_events] == [event["event_id"] for event in trace_events]

        service.close()
        reopened = FactoryService()
        try:
            recovered_events = reopened.runtime_store.load_events(run.run_id)
            recovered_trace = [event for event in recovered_events if event["operation"] == "trace"]
            assert [event["event_id"] for event in recovered_trace] == [event["event_id"] for event in trace_events]
            assert recovered_trace[-1]["data"]["stage"] == "QC"
            assert recovered_trace[-1]["data"]["decision"] == "ACCEPT"
        finally:
            reopened.close()
        service = reopened

        approve = DummyHandler(f"/api/runs/{run.run_id}/approve", {"decision_ref": "TEST-HUMAN-APPROVAL"})
        approve.content_runs = service.content_runs
        approve.service = service
        approve.workspace = handler.workspace
        ProductHandler.do_POST(approve)
        assert approve.status == 200, approve.response
        assert approve.response["status"] == "APPROVED"

        export = DummyHandler(f"/api/runs/{run.run_id}/export", {})
        export.content_runs = service.content_runs
        export.service = service
        export.workspace = handler.workspace
        ProductHandler.do_POST(export)
        assert export.status == 200, export.response
        assert export.response["export"]["artifact_type"] == "content_package"
        assert service.content_runs.get(run.run_id).status == "EXPORTED"

        publish = DummyHandler(f"/api/runs/{run.run_id}/publish", {"channel": "local"})
        publish.content_runs = service.content_runs
        publish.service = service
        publish.workspace = handler.workspace
        ProductHandler.do_POST(publish)
        assert publish.status == 200, publish.response
        assert publish.response["status"] == "PUBLISHED"
        assert publish.response["external_id"].startswith("local-")
    finally:
        service.close()
