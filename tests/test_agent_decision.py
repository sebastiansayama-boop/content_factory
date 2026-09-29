from content_factory.agent_decision import AgentDecision, JsonToolDecisionPolicy
from content_factory.agent_os import ContentAgentOS
from content_factory.agent_tools import AgentTool, AgentToolRegistry


class Control:
    def __init__(self):
        self.events = []

    def record(self, run_id, event, **kwargs):
        self.events.append((run_id, event, kwargs))


def test_decision_loop_selects_owned_tools_and_keeps_observations():
    control = Control()
    registry = AgentToolRegistry()
    registry.register(AgentTool("research.a", "first", "researcher", lambda **_: {"found": True}))
    registry.register(AgentTool("research.b", "second", "researcher", lambda **_: {"done": True}))
    os = ContentAgentOS(control, registry)

    choices = iter([
        AgentDecision("research.a", reason="step-1"),
        AgentDecision("research.b", reason="step-2"),
        AgentDecision("", reason="objective complete", terminal=True),
    ])

    def decide(context, tools):
        return next(choices)

    result = os.run_decision_loop(
        name="researcher",
        run_id="run-loop-1",
        objective="research",
        state={"phase": "research"},
        decide=decide,
        invoke=lambda tool, context: registry.invoke(
            tool, actor="researcher", run_id="run-loop-1", control=control
        ),
    )

    assert [item["tool"] for item in result.observations] == ["research.a", "research.b"]
    assert [item["result"] for item in result.observations] == [{"found": True}, {"done": True}]
    assert [event for _, event, _ in control.events].count("agent.decision") == 2
    assert [event for _, event, _ in control.events].count("agent.observation") == 2


def test_decision_loop_rejects_tool_outside_agent_authority():
    control = Control()
    registry = AgentToolRegistry()
    registry.register(AgentTool("content.write", "write", "writer", lambda **_: "ok"))
    os = ContentAgentOS(control, registry)

    try:
        os.run_decision_loop(
            name="writer",
            run_id="run-loop-2",
            objective="write",
            state={},
            decide=lambda context, tools: AgentDecision("research.public"),
            invoke=lambda tool, context: None,
        )
    except PermissionError as exc:
        assert "unavailable tool" in str(exc)
    else:
        raise AssertionError("expected PermissionError")


def test_json_tool_decision_policy_requires_strict_json():
    policy = JsonToolDecisionPolicy(lambda _: '{"tool":"content.write","reason":"write now","terminal":false}')
    decision = policy(
        type("Context", (), {
            "snapshot": lambda self, tools: {"available_tools": [tool.name for tool in tools]}
        })(),
        (AgentTool("content.write", "write", "writer", lambda **_: None),),
    )

    assert decision == AgentDecision("content.write", "write now", False)
