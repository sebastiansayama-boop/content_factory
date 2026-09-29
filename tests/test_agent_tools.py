from content_factory.agent_tools import AgentTool, AgentToolRegistry


class Control:
    def __init__(self):
        self.events = []

    def record(self, *args, **kwargs):
        self.events.append((args, kwargs))


def test_registry_restricts_tools_to_owner():
    registry = AgentToolRegistry()
    registry.register(
        AgentTool("research.public", "public research", "researcher", lambda **_: "ok")
    )

    assert [tool.name for tool in registry.for_agent("researcher")] == ["research.public"]
    try:
        registry.invoke(
            "research.public",
            actor="writer",
            run_id="run-1",
            control=Control(),
        )
    except PermissionError:
        pass
    else:
        raise AssertionError("expected owner check")


def test_registry_records_tool_execution():
    registry = AgentToolRegistry()
    control = Control()
    registry.register(
        AgentTool("content.write", "write", "writer", lambda **_: {"text": "ok"})
    )

    result = registry.invoke(
        "content.write",
        actor="writer",
        run_id="run-2",
        control=control,
    )

    assert result == {"text": "ok"}
    assert [event[0][1] for event in control.events] == [
        "agent.tool.started",
        "agent.tool.completed",
    ]


def test_registry_records_tool_failure():
    registry = AgentToolRegistry()
    control = Control()

    def fail(**_):
        raise RuntimeError("boom")

    registry.register(AgentTool("quality.check", "quality", "quality", fail))

    try:
        registry.invoke(
            "quality.check",
            actor="quality",
            run_id="run-3",
            control=control,
        )
    except RuntimeError:
        pass
    else:
        raise AssertionError("expected RuntimeError")

    assert control.events[-1][0][1] == "agent.tool.failed"
    assert control.events[-1][1]["evidence"]["error"] == "boom"
