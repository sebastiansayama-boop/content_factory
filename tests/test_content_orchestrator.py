from content_factory.agent_tools import AgentTool
from content_factory.content_orchestrator import ContentOrchestrator
from content_factory.content_run import ContentRunStore


class FakeControl:
    def __init__(self):
        self.events = []

    def record(self, *args, **kwargs):
        self.events.append((args, kwargs))

    def timeline(self, run_id):
        return []


class FakeService:
    def __init__(self):
        self.control = FakeControl()
        self.knowledge = type("Knowledge", (), {})()


class FakePlanner:
    def plan(self, **kwargs):
        return {"objective": "test", "deliverables": []}


class FakeReviewer:
    def __init__(self):
        self.calls = 0

    def review(self, **kwargs):
        self.calls += 1
        status = "REVISE" if self.calls == 1 else "PASS"
        return {
            "status": status,
            "issues": ["issue"] if status == "REVISE" else [],
            "required_changes": ["make it clearer"] if status == "REVISE" else [],
            "checked_claims": [],
            "confidence": 0.8 if status == "REVISE" else 0.95,
        }


def test_orchestrator_runs_bounded_review_loop(tmp_path):
    store = ContentRunStore(tmp_path / "runs.sqlite3")
    run = store.create(
        title="Future",
        brief="Explain the future.",
        audience="general",
        goal="Telegram post",
        formats=("social_post",),
        constraints=(),
    )
    service = FakeService()
    reviewer = FakeReviewer()
    orchestrator = ContentOrchestrator(
        service=service,
        workspace=object(),
        content_runs=store,
        planner=FakePlanner(),
        reviewer=reviewer,
    )

    orchestrator.tool_registry._tools["content_run.plan"] = AgentTool(
        "content_run.plan", "test planner", "planner", lambda **_: {"objective": "test", "deliverables": []}
    )
    orchestrator._research = lambda current: current
    writes = []

    def fake_write_tool(*, run, review_feedback):
        writes.append(list(review_feedback or []))
        return {
            "editorial": {},
            "content_spec": {"format": "social_post"},
            "script": {"units": [{"unit_id": "u1", "text": "Draft"}]},
            "production_plan": {"asset_requests": []},
            "knowledge": {"claim_refs": []},
        }

    orchestrator.tool_registry._tools["content.write"] = AgentTool(
        "content.write", "test writer", "writer", fake_write_tool
    )

    def fake_review_tool(*, run, result):
        reviewer.calls += 1
        status = "REVISE" if reviewer.calls == 1 else "PASS"
        return {
            "status": status,
            "issues": ["issue"] if status == "REVISE" else [],
            "required_changes": ["make it clearer"] if status == "REVISE" else [],
            "checked_claims": [],
            "confidence": 0.8 if status == "REVISE" else 0.95,
        }

    orchestrator.tool_registry._tools["content.review"] = AgentTool(
        "content.review", "test reviewer", "reviewer", fake_review_tool
    )

    orchestrator.tool_registry._tools["quality.check"] = AgentTool(
        "quality.check", "test quality", "quality", lambda **_: {"qc_id": "qc-1", "passed": True, "status": "PASSED"}
    )
    orchestrator.service.asset_registry = type("Assets", (), {"list_for_run": lambda self, run_id: []})()

    orchestrator._production = lambda run_id, result: (
        store.save_result(run_id, {**result, "review_history": result["review_history"]}),
        {"qc_id": "qc-1", "passed": True, "status": "PASSED"},
    )

    final_run, qc = orchestrator.run(run.run_id)

    assert reviewer.calls == 2
    assert writes == [[], ["make it clearer"]]
    assert len(final_run.result["review_history"]) == 2
    assert final_run.result["review_history"][0]["status"] == "REVISE"
    assert final_run.result["review_history"][1]["status"] == "PASS"
    assert qc["passed"] is True
    store.close()
