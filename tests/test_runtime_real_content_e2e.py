from __future__ import annotations

import json
import os

import pytest

from content_factory.artifacts import ArtifactStore
from content_factory.free_research import FreeWebGeminiAdapter, FreeWebRetriever
from content_factory.ollama_adapter import OllamaAdapter
from content_factory.providers import LLMProvider
from content_factory.runtime import Capability, ExecutionResult, FactoryRuntime, WorkItem
from content_factory.runtime_store import RuntimeStore
from content_factory.vertical_slice import quality_check


pytestmark = [
    pytest.mark.external,
    pytest.mark.skipif(
        not os.environ.get("GEMINI_API_KEY"),
        reason="real provider credentials are required for this E2E",
    ),
]


def test_runtime_executes_real_research_production_qc_chain(tmp_path):
    topic = "Why can unrelated animals independently evolve similar traits?"
    research = FreeWebGeminiAdapter(retriever=FreeWebRetriever(wiki_limit=1, openalex_limit=2, news_limit=2))
    production = OllamaAdapter()
    assert isinstance(production, LLMProvider)

    with RuntimeStore(tmp_path / "runtime.sqlite3") as store:
        runtime = FactoryRuntime(
            runtime_store=store,
            artifact_store=ArtifactStore(tmp_path / "artifacts"),
        )

        def research_execute(item, execution_id):
            prompt = f"""Research this Content Factory brief using live web search.
Return ONLY JSON:
{{"topic":"string","summary":"string","claims":[{{"id":"claim-1","text":"atomic factual claim","confidence":"high|medium|low","source_ids":["source-1"],"evidence_ids":["evidence-1"],"scope":"string","known_unknowns":["string"]}}],"sources":[{{"id":"source-1","title":"string","url":"https://..."}}],"evidence":[{{"id":"evidence-1","source_id":"source-1","excerpt":"short supporting passage","locator":"string","provenance":"string"}}],"editorial_angles":["string"]}}
Every factual claim must have source_ids and evidence_ids. Use only real public source URLs.
USER BRIEF: {topic}"""
            result = research.research(prompt)
            if not 200 <= result.status_code < 300:
                raise RuntimeError(f"research HTTP {result.status_code}")
            from content_factory.research import parse_research_json
            payload = parse_research_json(research.text(result))
            if not payload.get("claims") or not payload.get("sources"):
                raise ValueError("research returned no claims or sources")
            return ExecutionResult(
                execution_id, "research.search", "research-r1", payload,
                tuple(str(x.get("id")) for x in payload.get("evidence", []) if isinstance(x, dict) and x.get("id")),
            )

        def production_execute(item, execution_id):
            research_payload = json.loads(
                next(x for x in item.inputs if x.startswith("capability_input:")).split(":", 1)[1]
            )
            prompt = f"""Create one article for the researched topic below.
Return ONLY JSON:
{{"content":"complete usable article","title":"string","claim_refs":["claim-id"],"source_refs":["source-id"]}}
Use only supplied claims. Do not introduce factual claims outside them. Copy claim_refs EXACTLY from the supplied claim ids and source_refs EXACTLY from the supplied source ids. Never output placeholder values such as "claim-id" or "source-id".
Topic: {research_payload.get("topic", topic)}
Summary: {research_payload.get("summary", "")}
Claims: {json.dumps(research_payload["claims"], ensure_ascii=False)}
Sources: {json.dumps(research_payload["sources"], ensure_ascii=False)}
"""
            result = production.generate(prompt)
            if not 200 <= result.status_code < 300:
                raise RuntimeError(f"production HTTP {result.status_code}")
            from content_factory.research import parse_research_json
            asset = parse_research_json(production.response_text(result))
            asset["id"] = "runtime-article-v1"
            asset["format"] = "article"
            return ExecutionResult(
                execution_id, "content.generate", "article-r1",
                {"topic": research_payload.get("topic", topic), "package": [asset], "research": research_payload},
                tuple(asset.get("source_refs", [])),
            )

        def qc_execute(item, execution_id):
            production_payload = json.loads(
                next(x for x in item.inputs if x.startswith("capability_input:")).split(":", 1)[1]
            )
            quality = quality_check(production_payload, production_payload["research"])
            if quality["status"] != "PASS":
                raise ValueError(f"QC failed: {quality}")
            return ExecutionResult(
                execution_id, "content.qc", "qc-r1",
                {"package": production_payload, "quality": quality},
                tuple(production_payload["package"][0].get("source_refs", [])),
            )

        runtime.register_capability(Capability("research.search", lambda item: None, research_execute))
        runtime.register_capability(Capability("content.generate", lambda item: None, production_execute))
        runtime.register_capability(Capability("content.qc", lambda item: None, qc_execute))

        item = WorkItem(
            work_item_id="runtime-real-content-e2e",
            revision_id="objective-r1",
            operation_id="runtime-real-content-e2e-op",
            objective=topic,
            requested_outcome="research-backed article with provenance and QC",
            inputs=(f"topic:{topic}",),
            knowledge_basis=(),
            required_capabilities=("research.search", "content.generate", "content.qc"),
            owner="intelligence",
            acceptance_criteria=("claims have evidence", "article has provenance", "QC PASS"),
            release_requirements=("internal",),
        )
        runtime.submit(item, actor="intelligence")
        result = runtime.run_capability_chain(item, initial_payload={"topic": topic})

        assert result.state == "PRODUCED"
        assert [x.capability_id for x in result.executions] == [
            "research.search", "content.generate", "content.qc"
        ]
        assert result.executions[0].payload["claims"]
        assert result.executions[0].payload["sources"]
        assert result.executions[1].payload["package"][0]["content"]
        assert result.executions[1].payload["package"][0]["claim_refs"]
        assert result.executions[1].payload["package"][0]["source_refs"]
        assert result.final_payload["quality"]["status"] == "PASS"

        persisted = store.load_record(item.work_item_id, "capability_chain")
        assert persisted is not None
        assert len(persisted["executions"]) == 3
        assert (tmp_path / "artifacts/06_production/runtime-real-content-e2e.json").exists()
