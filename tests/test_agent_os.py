from content_factory.agent_os import AgentManager, ContentAgentOS


class Control:
    def __init__(self):
        self.events = []

    def record(self, run_id, event, **kwargs):
        self.events.append((run_id, event, kwargs))


def test_agent_os_exposes_bounded_content_specialists():
    os = ContentAgentOS(Control())

    assert set(os.agents) == {
        "planner",
        "researcher",
        "writer",
        "reviewer",
        "producer",
        "quality",
    }
    assert os.spec("reviewer").authority == "review"
    assert os.spec("researcher").capabilities == (
        "research.public_sources",
        "knowledge.accept",
    )


def test_agent_manager_records_start_and_completion():
    control = Control()
    manager = AgentManager(ContentAgentOS(control))

    result = manager.run(
        name="writer",
        run_id="run-1",
        operation="write",
        action=lambda: {"ok": True},
    )

    assert result == {"ok": True}
    assert [event for _, event, _ in control.events] == [
        "agent.started",
        "agent.completed",
    ]
    assert control.events[0][2]["actor"] == "writer"
    assert control.events[1][2]["actor"] == "writer"


def test_agent_manager_records_failure_and_does_not_swallow_it():
    control = Control()
    manager = AgentManager(ContentAgentOS(control))

    try:
        manager.run(
            name="reviewer",
            run_id="run-2",
            operation="review",
            action=lambda: (_ for _ in ()).throw(RuntimeError("review failed")),
        )
    except RuntimeError as exc:
        assert str(exc) == "review failed"
    else:
        raise AssertionError("expected RuntimeError")

    assert [event for _, event, _ in control.events] == [
        "agent.started",
        "agent.failed",
    ]
    assert control.events[1][2]["evidence"]["error"] == "review failed"


def test_manager_maps_lifecycle_stages_to_specialists():
    manager = AgentManager(ContentAgentOS(Control()))

    assert manager.select("PLANNING").name == "planner"
    assert manager.select("RESEARCHING").name == "researcher"
    assert manager.select("RESEARCH_READY").name == "writer"
    assert manager.select("REVIEW").name == "reviewer"
    assert manager.select("PRODUCING").name == "producer"
    assert manager.select("READY_FOR_REVIEW").name == "quality"
