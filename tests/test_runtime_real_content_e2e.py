from __future__ import annotations

import os
from pathlib import Path

import pytest

from content_factory.agent_tool_capability import (
    AgentToolCapabilitySpec,
    register_agent_tool_capabilities,
)
from content_factory.agent_tools import AgentToolRegistry, register_content_tools
from content_factory.artifacts import ArtifactStore
from content_factory.content_run import ContentRunStore
from content_factory.factory_control import FactoryControlStore
from content_factory.knowledge import KnowledgeStore
from content_factory.ollama_adapter import OllamaAdapter
from content_factory.runtime import Capability, FactoryRuntime, ExecutionResult, WorkItem
from content_factory.runtime_store import RuntimeStore
from content_factory.service import FactoryService
from content_factory.text_capability import text_generation_capability
from content_factory.workspace import ContentWorkspace


pytestmark = [
    pytest.mark.external,
    pytest.mark.skipif(
        not os.environ.get("OLLAMA_MODEL"),
        reason="real Ollama provider configuration is required for this E2E",
    ),
]


class DeterministicReviewer:
    def review(self, *, run_id, brief, audience, goal, result):
        if not isinstance(result, dict) or not result.get("script"):
            raise ValueError("content review requires a generated script")
        script = result["script"]
        units = script.get("units") if isinstance(script, dict) else None
        if not isinstance(units, list) or not units:
            raise ValueError("content review requires script units")
        return {
            "review": "PASS",
            "run_id": run_id,
            "claim_refs": result["knowledge"]["claim_refs"],
            "evidence_refs": result["knowledge"]["evidence_refs"],
            "unit_count": len(units),
        }


class OllamaWorkspaceFactory:
    def __init__(self, service: FactoryService, capability: Capability) -> None:
        self._store = service.runtime_store
        self._artifacts = service._artifacts
        self._capability = capability


def _seed_accepted_knowledge(knowledge: KnowledgeStore) -> tuple[str, str]:
    research = {
        "topic": "Why can unrelated animals independently evolve similar traits?",
        "summary": "Similar environmental pressures can be associated with independently evolved traits.",
        "claims": [{
            "id": "claim-1",
            "text": "Similar environmental pressures can be associated with independently evolved traits in unrelated lineages.",
            "confidence": "high",
            "source_ids": ["source-1"],
            "evidence_ids": ["evidence-1"],
            "scope": "This is a bounded statement about recurring evolutionary outcomes, not identical mechanisms.",
            "known_unknowns": ["The same phenotype does not imply the same underlying genetic or developmental mechanism."],
        }],
        "sources": [{
            "id": "source-1",
            "title": "Convergent evolution",
            "url": "https://www.ncbi.nlm.nih.gov/books/NBK22584/",
        }],
        "evidence": [{
            "id": "evidence-1",
            "source_id": "source-1",
            "excerpt": "Convergent evolution occurs when similar traits evolve independently in unrelated organisms.",
            "locator": "NCBI Bookshelf",
            "provenance": "public reference used as the source basis for this test knowledge",
        }],
        "editorial_angles": ["Why does evolution sometimes arrive at similar solutions?"],
    }
    knowledge.capture(run_id="seed-run", research=research)
    captured = knowledge.search("similar environmental pressures independently evolved traits", include_candidates=True)
    claim_id = captured["claims"][0]["claim_id"]
    evidence_id = captured["claims"][0]["evidence_ids"][0]
    knowledge.promote_claim(claim_id, decision_ref="e2e-test-accepted-knowledge")
    return claim_id, evidence_id


def test_runtime_executes_real_registered_content_tools_with_real_ollama(tmp_path, monkeypatch):
    monkeypatch.setenv("FACTORY_DATA_DIR", str(tmp_path / "service-data"))
    service = FactoryService()
    try:
        claim_id, evidence_id = _seed_accepted_knowledge(service.knowledge)
        run = service.content_runs.create(
            title="Runtime real content",
            brief="Why can unrelated animals independently evolve similar traits?",
            audience="general",
            goal="explain the phenomenon clearly",
            formats=("article",),
            constraints=("Russian",),
        )

        ollama = OllamaAdapter()
        ollama_capability = text_generation_capability(
            capability_id="ollama.text.generate",
            provider=ollama,
            generate=ollama.generate,
            response_text=ollama.response_text,
        )
        workspace = ContentWorkspace(service)
        workspace.factory = OllamaWorkspaceFactory(service, ollama_capability)

        registry = AgentToolRegistry()
        register_content_tools(
            registry,
            service=service,
            workspace=workspace,
            reviewer=DeterministicReviewer(),
        )

        control = service.control
        with RuntimeStore(tmp_path / "runtime.sqlite3") as runtime_store:
            runtime = FactoryRuntime(
                runtime_store=runtime_store,
                artifact_store=ArtifactStore(tmp_path / "artifacts"),
            )
            register_agent_tool_capabilities(
                runtime,
                registry,
                run_loader=service.content_runs.get,
                control=control,
                specs=(
                    AgentToolCapabilitySpec(
                        capability_id="knowledge.search",
                        tool_name="knowledge.search",
                        actor="researcher",
                        build_kwargs=lambda item, current_run: {"run": current_run},
                    ),
                    AgentToolCapabilitySpec(
                        capability_id="content.write",
                        tool_name="content.write",
                        actor="writer",
                        build_kwargs=lambda item, current_run: {
                            "run": current_run,
                            "review_feedback": [],
                            "knowledge": _previous_payload(item),
                        },
                    ),
                    AgentToolCapabilitySpec(
                        capability_id="content.review",
                        tool_name="content.review",
                        actor="reviewer",
                        build_kwargs=lambda item, current_run: {
                            "run": current_run,
                            "result": _previous_payload(item),
                        },
                    ),
                ),
            )

            item = WorkItem(
                work_item_id=run.run_id,
                revision_id="runtime-real-content-r1",
                objective=run.brief,
                requested_outcome="verified Russian article from accepted knowledge",
                inputs=(f"brief:{run.brief}",),
                knowledge_basis=(claim_id, evidence_id),
                required_capabilities=("knowledge.search", "content.write", "content.review"),
                owner="intelligence",
                acceptance_criteria=("accepted knowledge consumed", "content generated from that knowledge", "review PASS"),
                release_requirements=("internal",),
            )
            runtime.submit(item, actor="intelligence")
            result = runtime.run_capability_chain(item)

            assert result.state == "PRODUCED"
            assert [x.capability_id for x in result.executions] == [
                "knowledge.search",
                "content.write",
                "content.review",
            ]

            knowledge_payload = result.executions[0].payload
            content_payload = result.executions[1].payload
            review_payload = result.final_payload

            assert knowledge_payload["claims"]
            assert knowledge_payload["claims"][0]["claim_id"] == claim_id
            assert evidence_id in knowledge_payload["claims"][0]["evidence_ids"]

            assert content_payload["knowledge"]["claim_refs"] == [claim_id]
            assert content_payload["knowledge"]["evidence_refs"] == [evidence_id]
            assert content_payload["script"]["units"]
            assert all(claim_id in unit["claim_refs"] for unit in content_payload["script"]["units"])
            assert all(evidence_id in unit["evidence_refs"] for unit in content_payload["script"]["units"])

            assert review_payload["review"] == "PASS"
            assert review_payload["claim_refs"] == [claim_id]
            assert review_payload["evidence_refs"] == [evidence_id]

            persisted = runtime_store.load_record(run.run_id, "capability_chain")
            assert persisted is not None
            assert len(persisted["executions"]) == 3
            assert (tmp_path / "artifacts/06_production" / f"{run.run_id}.json").exists()

            events = control.timeline(run.run_id)
            assert [event.event_type for event in events] == [
                "agent.tool.started",
                "agent.tool.completed",
                "agent.tool.started",
                "agent.tool.completed",
                "agent.tool.started",
                "agent.tool.completed",
            ]
    finally:
        service.close()


def _previous_payload(item: WorkItem) -> dict:
    import json

    for value in reversed(item.inputs):
        if value.startswith("capability_input:"):
            payload = json.loads(value[len("capability_input:"):])
            if isinstance(payload, dict):
                return payload
            return {"input": payload}
    return {}
