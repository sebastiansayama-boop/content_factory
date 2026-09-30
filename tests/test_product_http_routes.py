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

    def replay_plan(self, run, *, changed_claim_ids, content_brief, content_brief_revision_id, changes=None):
        return {
            "run_id": run["run_id"],
            "mode": "INCREMENTAL_REPLAY",
            "content_brief_id": content_brief["brief_id"],
            "content_brief_revision_id": content_brief_revision_id,
            "content_brief": content_brief,
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



def test_real_http_replay_r1_creates_new_artifact_and_qc(tmp_path, monkeypatch):
    import json
    import threading
    from http.client import HTTPConnection
    from http.server import ThreadingHTTPServer

    monkeypatch.setenv("FACTORY_DATA_DIR", str(tmp_path))
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setenv("FACTORY_PROVIDER", "local")
    monkeypatch.setenv("FACTORY_API_TOKEN", "e2e-token")

    from content_factory.service import FactoryService
    from content_factory.workspace import ContentWorkspace
    from content_factory.content_run_planner import ContentRunPlanner

    service = FactoryService()
    ProductHandler.service = service
    ProductHandler.workspace = ContentWorkspace(service)
    ProductHandler.content_runs = service.content_runs
    ProductHandler.content_run_planner = ContentRunPlanner(ProductHandler.workspace)
    server = ThreadingHTTPServer(("127.0.0.1", 0), ProductHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    def request(method, path, body=None):
        connection = HTTPConnection("127.0.0.1", server.server_port, timeout=10)
        payload = None if body is None else json.dumps(body).encode("utf-8")
        headers = {"Authorization": "Bearer e2e-token"}
        if payload is not None:
            headers["Content-Type"] = "application/json"
        connection.request(method, path, body=payload, headers=headers)
        response = connection.getresponse()
        raw = response.read()
        status = response.status
        connection.close()
        return status, json.loads(raw.decode("utf-8")) if raw else {}

    try:
        status, created = request("POST", "/api/runs", {
            "title": "HTTP replay E2E",
            "brief": "Explain a topic with evidence.",
            "audience": "general",
            "goal": "short video",
            "formats": ["short_video"],
            "constraints": [],
        })
        assert status == 201
        run_id = created["run_id"]

        status, first = request("POST", f"/api/runs/{run_id}/factory", {})
        assert status == 409
        candidate_id = first["candidates"][0]["claim_id"]
        status, promoted = request("POST", f"/api/knowledge/{candidate_id}/promote", {"decision_ref": "HTTP-E2E-REVIEW"})
        assert status == 200
        assert promoted["status"] == "PROMOTED"

        status, r1_run = request("POST", f"/api/runs/{run_id}/factory", {})
        assert status == 200, r1_run
        r1 = r1_run["result"]["content_brief"]["revision_id"]
        brief_id = r1_run["result"]["content_brief"]["brief_id"]
        r1_payload = dict(r1_run["result"]["content_brief"])
        r2_payload = {**r1_payload, "title": r1_payload["title"] + " — revision 2"}
        r2_revision = service.content_runs.save_content_brief(run_id, r2_payload)
        assert r2_revision.revision_id != r1

        status, revisions = request("GET", f"/api/runs/{run_id}/content-brief/revisions")
        assert status == 200
        assert [item["revision_id"] for item in revisions["revisions"]] == [r1, r2_revision.revision_id]

        status, replay = request("POST", f"/api/runs/{run_id}/replay", {
            "brief_id": brief_id,
            "revision_id": r1,
            "changed_claim_ids": [],
        })
        assert status == 200, replay
        replay_run = replay["run"]
        replay_run_id = replay_run["run_id"]
        assert replay_run_id != run_id
        assert replay_run["status"] == "REVIEW"
        assert replay_run["result"]["content_brief"]["revision_id"] == r1
        assert replay_run["result"]["content_brief"]["title"] == r1_payload["title"]
        assets = replay_run["result"]["production"]["assets"]
        assert assets
        assert all(asset["run_id"] == replay_run_id for asset in assets)
        assert replay_run["result"]["production"]["qc"]["status"] == "PASSED"

        status, trace = request("GET", f"/api/runs/{replay_run_id}/execution-trace")
        assert status == 200
        stages = [event["data"]["stage"] for event in trace["events"] if event["operation"] == "trace"]
        assert stages == ["REPLAY", "PRODUCTION", "QC"]
        assert all(event["revision_id"] == f"content-run:{replay_run_id}:{r1}" for event in trace["events"] if event["operation"] == "trace")
        assert trace["events"][-1]["data"]["decision"] == "ACCEPT"

        connection = HTTPConnection("127.0.0.1", server.server_port, timeout=10)
        connection.request("GET", "/")
        response = connection.getresponse()
        page = response.read().decode("utf-8")
        assert response.status == 200
        assert "Replay an exact ContentBrief revision" in page
        connection.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
        service.close()

def test_replay_endpoint_requires_durable_brief_revision(tmp_path):
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
    assert handler.status == 400
    assert handler.response["error"] == "brief_id and revision_id are required"
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
        brief_revision_id = result["content_brief"]["revision_id"]
        brief_get = DummyHandler(f"/api/runs/{run.run_id}/content-brief", {})
        brief_get.content_runs = service.content_runs
        brief_get.service = service
        brief_get.workspace = handler.workspace
        ProductHandler.do_GET(brief_get)
        assert brief_get.status == 200
        assert brief_get.response["revision_id"] == brief_revision_id
        assert brief_get.response["brief"]["brief_id"] == result["content_brief"]["brief_id"]

        revision_get = DummyHandler(f"/api/runs/{run.run_id}/content-brief/{brief_revision_id}", {})
        revision_get.content_runs = service.content_runs
        revision_get.service = service
        revision_get.workspace = handler.workspace
        ProductHandler.do_GET(revision_get)
        assert revision_get.status == 200
        assert revision_get.response["revision_id"] == brief_revision_id

        revisions_get = DummyHandler(f"/api/runs/{run.run_id}/content-brief/revisions", {})
        revisions_get.content_runs = service.content_runs
        revisions_get.service = service
        revisions_get.workspace = handler.workspace
        ProductHandler.do_GET(revisions_get)
        assert revisions_get.status == 200
        assert [item["revision_id"] for item in revisions_get.response["revisions"]] == [brief_revision_id]

        assert result["content_spec"]["claim_refs"] == [candidate_id]
        content_brief = result["content_brief"]
        assert content_brief["selected_claim_refs"] == [candidate_id]
        assert content_brief["editorial_points"]
        assert content_brief["content_elements"]
        point_ids = {point["point_id"] for point in content_brief["editorial_points"]}
        assert all(set(element["editorial_point_ids"]).issubset(point_ids) for element in content_brief["content_elements"])
        assert result["production_plan"]["content_brief_id"] == content_brief["brief_id"]
        assert set(result["production_plan"]["content_element_ids"]) == {
            element["element_id"] for element in content_brief["content_elements"]
        }
        assert all(request["content_element_ids"] for request in result["production_plan"]["asset_requests"])
        information_flow = result["information_flow"]
        assert information_flow["claim_count"] == len(content_brief["selected_claim_refs"])
        assert information_flow["editorial_point_count"] == len(content_brief["editorial_points"])
        assert information_flow["content_element_count"] == len(content_brief["content_elements"])
        assert information_flow["artifact_count"] == len(result["production"]["assets"])
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
        service = FactoryService()
        recovered_brief = service.content_runs.get_content_brief(run.run_id, revision_id=brief_revision_id)
        assert recovered_brief is not None
        assert recovered_brief.revision_id == brief_revision_id
        assert recovered_brief.payload["brief_id"] == result["content_brief"]["brief_id"]

        recovered_events = service.runtime_store.load_events(run.run_id)
        recovered_trace = [event for event in recovered_events if event["operation"] == "trace"]
        http_trace = [event for event in trace_events if event["operation"] == "trace"]
        assert [event["event_id"] for event in recovered_trace] == [event["event_id"] for event in http_trace]
        assert recovered_trace[-1]["data"]["stage"] == "QC"
        assert recovered_trace[-1]["data"]["decision"] == "ACCEPT"

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
