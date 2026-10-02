from __future__ import annotations

from types import SimpleNamespace

from content_factory.agent_tool_capability import (
    content_tool_capability_specs,
    register_agent_tool_capabilities,
)
from content_factory.agent_tools import AgentToolRegistry, register_content_tools
from content_factory.artifacts import ArtifactStore
from content_factory.content_run import ContentRunStore
from content_factory.factory_control import FactoryControlStore
from content_factory.runtime import FactoryRuntime, WorkItem
from content_factory.runtime_store import RuntimeStore


class FakeKnowledge:
    def search(self, brief: str):
        return {"brief": brief, "matches": ["accepted-knowledge-1"]}


class FakeService:
    def __init__(self):
        self.knowledge = FakeKnowledge()


class FakeWorkspace:
    pass


def test_runtime_executes_existing_registered_agent_tool(tmp_path):
    service = FakeService()
    registry = AgentToolRegistry()
    register_content_tools(
        registry,
        service=service,
        workspace=FakeWorkspace(),
    )

    runs = ContentRunStore(tmp_path / "content_runs.sqlite3")
    run = runs.create(
        title="Runtime bridge",
        brief="How do unrelated animals evolve similar traits?",
        formats=("article",),
    )
    control = FactoryControlStore(tmp_path / "control.sqlite3")

    with RuntimeStore(tmp_path / "runtime.sqlite3") as store:
        runtime = FactoryRuntime(
            runtime_store=store,
            artifact_store=ArtifactStore(tmp_path / "artifacts"),
        )
        register_agent_tool_capabilities(
            runtime,
            registry,
            run_loader=runs.get,
            control=control,
            specs=(content_tool_capability_specs()[0],),
        )

        item = WorkItem(
            work_item_id=run.run_id,
            revision_id="runtime-bridge-r1",
            objective=run.brief,
            requested_outcome="accepted knowledge for production",
            inputs=(f"brief:{run.brief}",),
            knowledge_basis=(),
            required_capabilities=("knowledge.search",),
            owner="intelligence",
            acceptance_criteria=("knowledge lookup executed",),
            release_requirements=("internal",),
        )
        runtime.submit(item, actor="intelligence")
        result = runtime.run_capability_chain(item)

    assert result.state == "PRODUCED"
    assert result.executions[0].capability_id == "knowledge.search"
    assert result.final_payload == {
        "brief": run.brief,
        "matches": ["accepted-knowledge-1"],
    }
    events = control.timeline(run.run_id)
    assert [event.event_type for event in events] == [
        "agent.tool.started",
        "agent.tool.completed",
    ]

    control.close()
    runs.close()
