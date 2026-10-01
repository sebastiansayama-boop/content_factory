from content_factory.runtime import FactoryRuntime, WorkItem
from content_factory.runtime_store import RuntimeStore


def make_trace_item() -> WorkItem:
    return WorkItem(
        work_item_id="run-trace-1",
        operation_id="content-run:run-trace-1",
        revision_id="content-run:run-trace-1:r1",
        objective="trace stages",
        requested_outcome="durable execution trace",
        inputs=("run-trace-1",),
        knowledge_basis=(),
        required_capabilities=("content.factory.vertical_slice",),
        owner="test",
        acceptance_criteria=("trace exists",),
        release_requirements=(),
    )


def test_stage_trace_is_durable_and_does_not_change_control_state(tmp_path):
    database = tmp_path / "runtime.sqlite3"
    item = make_trace_item()

    with RuntimeStore(database) as store:
        runtime = FactoryRuntime(runtime_store=store)
        runtime.submit(item, actor="test")
        before = runtime.states[item.work_item_id]
        runtime.record_trace(
            item,
            stage="RESEARCH",
            task="research_brief",
            tool="FakeResearchAdapter",
            action="provider_call",
            result={"status": "completed", "http_status": 200},
            decision="ACCEPT",
            actor="test",
        )
        assert runtime.states[item.work_item_id] == before
        trace = [event for event in runtime.provenance(item.work_item_id) if event.operation == "trace"]
        assert trace[0].data["stage"] == "RESEARCH"
        assert trace[0].data["task"] == "research_brief"
        assert trace[0].data["tool"] == "FakeResearchAdapter"
        assert trace[0].data["decision"] == "ACCEPT"

    with RuntimeStore(database) as store:
        recovered = FactoryRuntime(runtime_store=store)
        trace = [event for event in recovered.provenance(item.work_item_id) if event.operation == "trace"]
        assert len(trace) == 1
        assert trace[0].data["action"] == "provider_call"
