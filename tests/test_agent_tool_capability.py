from __future__ import annotations

import json

from content_factory.agent_tool_capability import (
    AgentToolCapabilitySpec,
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
        return {
            "claims": [{"claim_id": "kc-1", "evidence_ids": ["ke-1"]}],
            "evidence": [{"evidence_id": "ke-1"}],
            "brief": brief,
        }

    def accepted_for_run(self, run_id: str):
        return self.search(run_id)

    def record_usage(self, **kwargs):
        return None


class FakeService:
    def __init__(self):
        self.knowledge = FakeKnowledge()


class FakeFactory:
    _capability = type("Capability", (), {"capability_id": "fake.llm"})()


class FakeWorkspace:
    factory = FakeFactory()

    def _run_product_work_item(self, item):
        objective = item.objective
        if objective == "turn accepted knowledge into content ideas":
            payload = {
                "ideas": [{
                    "idea_id": "idea-1",
                    "title": "A verified idea",
                    "angle": "Why the evidence matters",
                    "audience": "general",
                    "purpose": "explain the finding",
                    "formats": ["article"],
                    "claim_refs": ["kc-1"],
                    "evidence_refs": ["ke-1"],
                }]
            }
        elif objective == "turn selected knowledge claims into an explicit editorial content brief":
            payload = {
                "brief_id": "brief-1",
                "title": "A verified idea",
                "objective": "explain the finding",
                "audience": "general",
                "angle": "Why the evidence matters",
                "selected_claim_refs": ["kc-1"],
                "evidence_refs": ["ke-1"],
                "editorial_points": [{
                    "point_id": "point-1",
                    "text": "The evidence and its meaning.",
                    "role": "development",
                    "claim_refs": ["kc-1"],
                    "evidence_refs": ["ke-1"],
                }],
                "content_elements": [{
                    "element_id": "element-1",
                    "kind": "narration",
                    "editorial_point_ids": ["point-1"],
                    "purpose": "explain",
                    "production_intent": "clear explanation",
                    "claim_refs": ["kc-1"],
                    "evidence_refs": ["ke-1"],
                }],
                "formats": ["article"],
                "constraints": ["Russian"],
            }
        elif objective == "turn a content idea into an executable content specification":
            payload = {
                "spec_id": "spec-1",
                "title": "A verified idea",
                "objective": "explain the finding",
                "audience": "general",
                "format": "article",
                "tone": "clear",
                "structure": ["hook", "context", "development", "conclusion"],
                "constraints": ["Russian"],
                "claim_refs": ["kc-1"],
                "evidence_refs": ["ke-1"],
                "style_bible": {},
            }
        else:
            payload = {
                "script_id": "script-1",
                "title": "A verified idea",
                "units": [
                    {"unit_id": "unit-1", "kind": "hook", "text": "Here is the question.", "visual_intent": "", "claim_refs": ["kc-1"], "evidence_refs": ["ke-1"]},
                    {"unit_id": "unit-2", "kind": "context", "text": "Here is the context.", "visual_intent": "", "claim_refs": ["kc-1"], "evidence_refs": ["ke-1"]},
                    {"unit_id": "unit-3", "kind": "development", "text": "Here is what the evidence shows.", "visual_intent": "", "claim_refs": ["kc-1"], "evidence_refs": ["ke-1"]},
                    {"unit_id": "unit-4", "kind": "conclusion", "text": "Here is the bounded takeaway.", "visual_intent": "", "claim_refs": ["kc-1"], "evidence_refs": ["ke-1"]},
                ],
            }
        return {"execution": {"output": json.dumps(payload, ensure_ascii=False)}}


class FakeReviewer:
    def review(self, *, run_id, brief, audience, goal, result):
        return {
            "review": "PASS",
            "run_id": run_id,
            "claim_refs": result["knowledge"]["claim_refs"],
            "evidence_refs": result["knowledge"]["evidence_refs"],
        }


def test_runtime_executes_registered_agent_tool_chain_with_result_handoff(tmp_path):
    service = FakeService()
    registry = AgentToolRegistry()
    register_content_tools(
        registry,
        service=service,
        workspace=FakeWorkspace(),
        reviewer=FakeReviewer(),
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
            specs=(
                AgentToolCapabilitySpec(
                    capability_id="knowledge.search",
                    tool_name="knowledge.search",
                    actor="researcher",
                    build_kwargs=lambda item, run: {"run": run},
                ),
                AgentToolCapabilitySpec(
                    capability_id="content.write",
                    tool_name="content.write",
                    actor="writer",
                    build_kwargs=lambda item, run: {
                        "run": run,
                        "review_feedback": [],
                        "knowledge": json.loads(
                            next(value[len("capability_input:"):] for value in reversed(item.inputs) if value.startswith("capability_input:"))
                        ),
                    },
                ),
                AgentToolCapabilitySpec(
                    capability_id="content.review",
                    tool_name="content.review",
                    actor="reviewer",
                    build_kwargs=lambda item, run: {
                        "run": run,
                        "result": json.loads(
                            next(value[len("capability_input:"):] for value in reversed(item.inputs) if value.startswith("capability_input:"))
                        ),
                    },
                ),
            ),
        )

        item = WorkItem(
            work_item_id=run.run_id,
            revision_id="runtime-bridge-r1",
            objective=run.brief,
            requested_outcome="verified content package",
            inputs=(f"brief:{run.brief}",),
            knowledge_basis=(),
            required_capabilities=("knowledge.search", "content.write", "content.review"),
            owner="intelligence",
            acceptance_criteria=("registered tools executed in order", "previous result consumed by next tool"),
            release_requirements=("internal",),
        )
        runtime.submit(item, actor="intelligence")
        result = runtime.run_capability_chain(item)

    assert result.state == "PRODUCED"
    assert [execution.capability_id for execution in result.executions] == [
        "knowledge.search",
        "content.write",
        "content.review",
    ]
    assert result.final_payload["review"] == "PASS"
    assert result.final_payload["claim_refs"] == ["kc-1"]
    assert result.final_payload["evidence_refs"] == ["ke-1"]

    events = control.timeline(run.run_id)
    assert [event.event_type for event in events] == [
        "agent.tool.started",
        "agent.tool.completed",
        "agent.tool.started",
        "agent.tool.completed",
        "agent.tool.started",
        "agent.tool.completed",
    ]
    assert events[2].actor == "writer"
    assert events[4].actor == "reviewer"

    control.close()
    runs.close()
