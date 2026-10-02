from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Callable

from .knowledge import KnowledgeStore
from .local_research import LocalResearchAdapter
from .research import OpenAIWebResearchAdapter, is_safe_source_url, parse_research_json
from .openai_adapter import OpenAIResponsesAdapter
from .ollama_adapter import OllamaAdapter
from .local_adapter import LocalTextAdapter
from .providers import LLMProvider


@dataclass(frozen=True)
class VerticalSliceResult:
    run_id: str
    brief: str
    research: dict[str, Any]
    package: dict[str, Any]
    quality: dict[str, Any]
    information_flow: dict[str, Any]


def _slug(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return value or "story"


def build_visual_card(*, title: str, subtitle: str, asset_id: str) -> dict[str, Any]:
    safe_title = title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    safe_subtitle = subtitle.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="675" viewBox="0 0 1200 675">'
        '<rect width="1200" height="675" fill="#f4f1e8"/>'
        f'<text x="80" y="190" font-family="Arial, sans-serif" font-size="54" font-weight="700" fill="#171717">{safe_title}</text>'
        f'<text x="80" y="275" font-family="Arial, sans-serif" font-size="30" fill="#555">{safe_subtitle}</text>'
        '<text x="80" y="585" font-family="Arial, sans-serif" font-size="20" fill="#777">CONTENT FACTORY · RESEARCH-GROUNDED VISUAL</text>'
        '</svg>'
    )
    return {
        "id": asset_id,
        "format": "visual_card",
        "title": title,
        "content": svg,
        "mime_type": "image/svg+xml",
        "source_refs": [],
        "claim_refs": [],
        "generator": "content_factory.deterministic_visual",
    }


def quality_check(package: dict[str, Any], research: dict[str, Any]) -> dict[str, Any]:
    assets = package.get("package")
    claims = research.get("claims")
    sources = research.get("sources")
    errors: list[str] = []
    if not isinstance(assets, list) or not assets:
        errors.append("package must contain at least one asset")
    if not isinstance(claims, list) or not claims:
        errors.append("research must contain claims")
    if not isinstance(sources, list) or not sources:
        errors.append("research must contain sources")
    claim_ids = {item.get("id") for item in claims or [] if isinstance(item, dict) and item.get("id")}
    source_ids = {item.get("id") for item in sources or [] if isinstance(item, dict) and item.get("id")}
    for asset in assets or []:
        if not isinstance(asset, dict):
            errors.append("asset must be an object")
            continue
        if not asset.get("content"):
            errors.append(f"asset {asset.get('id', '<unknown>')} has no content")
        for claim_id in asset.get("claim_refs", []):
            if claim_id not in claim_ids:
                errors.append(f"asset {asset.get('id')} references unknown claim {claim_id}")
        for source_id in asset.get("source_refs", []):
            if source_id not in source_ids:
                errors.append(f"asset {asset.get('id')} references unknown source {source_id}")
    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "asset_count": len(assets) if isinstance(assets, list) else 0,
        "claim_count": len(claims) if isinstance(claims, list) else 0,
        "source_count": len(sources) if isinstance(sources, list) else 0,
    }


class ContentFactoryVerticalSlice:
    """First product slice: live research -> production -> visual -> QC."""

    def __init__(
        self,
        research_adapter: OpenAIWebResearchAdapter | None = None,
        knowledge_store: KnowledgeStore | None = None,
        trace_event: Callable[..., None] | None = None,
        llm_provider: LLMProvider | None = None,
    ) -> None:
        if research_adapter is not None:
            self.research_adapter = research_adapter
        else:
            configured = os.environ.get("FACTORY_PROVIDER", "").strip().lower()
            provider = configured or ("openai" if os.environ.get("OPENAI_API_KEY", "").strip() else "local")
            if provider == "gemini":
                raise ValueError("Gemini provider is disabled; use 'openai' or 'local'")
            if provider == "openai":
                self.research_adapter = OpenAIWebResearchAdapter()
            elif provider == "local":
                self.research_adapter = LocalResearchAdapter()
            else:
                raise ValueError("FACTORY_PROVIDER must be 'gemini', 'openai', or 'local'")
        self.knowledge_store = knowledge_store
        self.trace_event = trace_event
        if llm_provider is not None:
            self.llm_provider = llm_provider
        else:
            configured_llm = os.environ.get("FACTORY_LLM_PROVIDER", "").strip().lower()
            configured_factory = os.environ.get("FACTORY_PROVIDER", "").strip().lower()
            llm_name = configured_llm or configured_factory or ("openai" if os.environ.get("OPENAI_API_KEY", "").strip() else "local")
            if llm_name == "gemini":
                raise ValueError("Gemini LLM provider is disabled; use 'openai', 'ollama', or 'local'")
            if llm_name == "openai":
                self.llm_provider = OpenAIResponsesAdapter()
            elif llm_name == "ollama":
                self.llm_provider = OllamaAdapter()
            elif llm_name == "local":
                self.llm_provider = LocalTextAdapter()
            else:
                raise ValueError("FACTORY_LLM_PROVIDER must be 'openai', 'ollama', or 'local'; Gemini is disabled")

    def run(self, *, run_id: str, brief: str, formats: list[str] | None = None) -> VerticalSliceResult:
        if not brief.strip():
            raise ValueError("brief must not be empty")
        requested_formats = formats or ["article", "social_post", "visual_card"]
        prior_knowledge = self.knowledge_store.search(brief, include_candidates=True) if self.knowledge_store else {
            "claims": [], "sources": [], "editorial_angles": []
        }
        prior_json = json.dumps(prior_knowledge, ensure_ascii=False)
        research_prompt = f"""You are the research stage of a content production system.
Research the user's brief using live web search. Return ONLY JSON:
{{"topic":"string","summary":"string","claims":[{{"id":"claim-1","text":"atomic factual claim","confidence":"high|medium|low","source_ids":["source-1"],"evidence_ids":["evidence-1"],"scope":"string","known_unknowns":["string"]}}],"sources":[{{"id":"source-1","title":"string","url":"https://..."}}],"evidence":[{{"id":"evidence-1","source_id":"source-1","excerpt":"short supporting passage","locator":"string","provenance":"string"}}],"editorial_angles":["string"]}}
Rules: search the web; use current reputable sources; every factual claim must cite source_ids and evidence_ids; every evidence item must identify its source and a concrete supporting excerpt; never invent URLs; keep claims atomic; state scope and meaningful known_unknowns; return source metadata for sources actually used.
Prior reusable knowledge is context, not proof. Re-check it against current sources before relying on it, and do not cite prior knowledge IDs as source_ids:
{prior_json}
USER BRIEF:
{brief}
"""
        if self.trace_event is not None:
            self.trace_event(stage="RESEARCH", task="research_brief", tool=type(self.research_adapter).__name__, action="provider_call", result={"status": "started"})
        try:
            result = self.research_adapter.research(research_prompt)
        except Exception as exc:
            if self.trace_event is not None:
                self.trace_event(stage="RESEARCH", task="research_brief", tool=type(self.research_adapter).__name__, action="provider_call", result={"status": "failed", "error_type": type(exc).__name__}, decision="FAILED")
            raise
        if self.trace_event is not None:
            self.trace_event(stage="RESEARCH", task="research_brief", tool=type(self.research_adapter).__name__, action="provider_call", result={"status": "completed", "http_status": result.status_code}, decision="ACCEPT" if 200 <= result.status_code < 300 else "FAIL")
        if result.status_code < 200 or result.status_code >= 300:
            raise ValueError(f"research provider returned HTTP {result.status_code}")
        research = parse_research_json(self.research_adapter.text(result))
        provider_sources = self.research_adapter.sources(result)
        declared = research.get("sources")
        if not isinstance(declared, list):
            declared = []
        known_urls = {
            item.get("url")
            for item in declared
            if isinstance(item, dict) and is_safe_source_url(str(item.get("url") or ""))
        }
        for source in provider_sources:
            url = str(source.get("url") or "").strip()
            if not is_safe_source_url(url):
                continue
            if url not in known_urls:
                declared.append({"id": f"source-{len(declared) + 1}", "title": source["title"], "url": url})
                known_urls.add(url)
        declared = [
            item for item in declared
            if isinstance(item, dict) and is_safe_source_url(str(item.get("url") or ""))
        ]
        if not declared:
            raise ValueError("research returned no safe public sources")
        research["sources"] = declared
        claims = research.get("claims")
        if not isinstance(claims, list) or not claims:
            raise ValueError("research claims must be a non-empty array")
        source_ids = {item.get("id") for item in declared if isinstance(item, dict)}
        for claim in claims:
            if not isinstance(claim, dict) or not claim.get("id") or not claim.get("text"):
                raise ValueError("every research claim requires id and text")
            refs = claim.get("source_ids")
            if not isinstance(refs, list) or not refs or not set(refs).issubset(source_ids):
                raise ValueError(f"claim {claim.get('id')} has invalid source_ids")
        knowledge_capture = None
        knowledge_refs = None
        knowledge_usage = 0
        if self.knowledge_store is not None:
            knowledge_capture = self.knowledge_store.capture(run_id=run_id, research=research)
            knowledge_refs = self.knowledge_store.resolve_research_refs(research)
            research["knowledge_refs"] = knowledge_refs
            accepted_claim_ids = [
                str(item["claim_id"])
                for item in prior_knowledge.get("claims", [])
                if isinstance(item, dict) and item.get("status") == KnowledgeStore.ACCEPTED
            ]
            if accepted_claim_ids:
                knowledge_usage = self.knowledge_store.record_usage(
                    run_id=run_id,
                    target_ref=f"content-run:{run_id}",
                    claim_ids=accepted_claim_ids,
                )

        topic = str(research.get("topic") or brief).strip()
        summary = str(research.get("summary") or "").strip()
        claim_lines = "\n".join(f"- {c['id']}: {c['text']}" for c in claims if isinstance(c, dict))
        source_lines = "\n".join(f"- {s['id']}: {s.get('title', '')} — {s.get('url', '')}" for s in declared if isinstance(s, dict))
        package: dict[str, Any] = {"topic": topic, "package": []}
        for fmt in requested_formats:
            if fmt == "visual_card":
                package["package"].append(build_visual_card(title=topic, subtitle=summary[:140], asset_id=f"{_slug(topic)}-visual-card-v1"))
                continue
            production_prompt = f"""Create one {fmt} for this researched topic.
Return ONLY JSON: {{"content":"complete usable content","title":"string","claim_refs":["claim-id"],"source_refs":["source-id"]}}
Do not add factual claims absent from the research.
Topic: {topic}
Summary: {summary}
Claims:
{claim_lines}
Sources:
{source_lines}
"""
            if self.trace_event is not None:
                self.trace_event(stage="PRODUCTION", task=f"produce_{fmt}", tool=type(self.llm_provider).__name__, action="provider_call", result={"status": "started", "format": fmt})
            try:
                generated = self.llm_provider.generate(production_prompt)
            except Exception as exc:
                if self.trace_event is not None:
                    self.trace_event(stage="PRODUCTION", task=f"produce_{fmt}", tool=type(self.llm_provider).__name__, action="provider_call", result={"status": "failed", "format": fmt, "error_type": type(exc).__name__}, decision="FAILED")
                raise
            if self.trace_event is not None:
                self.trace_event(stage="PRODUCTION", task=f"produce_{fmt}", tool=type(self.llm_provider).__name__, action="provider_call", result={"status": "completed", "format": fmt, "http_status": generated.status_code}, decision="ACCEPT" if 200 <= generated.status_code < 300 else "FAIL")
            if generated.status_code < 200 or generated.status_code >= 300:
                raise ValueError(f"production provider returned HTTP {generated.status_code}")
            asset = parse_research_json(self.llm_provider.response_text(generated))
            asset["id"] = f"{_slug(topic)}-{fmt}-v1"
            asset["format"] = fmt
            package["package"].append(asset)
        all_claim_ids = [c["id"] for c in claims if isinstance(c, dict)]
        all_source_ids = sorted({sid for c in claims if isinstance(c, dict) for sid in c.get("source_ids", [])})
        claim_by_id = {
            str(claim.get("id")): claim
            for claim in claims
            if isinstance(claim, dict) and claim.get("id")
        }
        for asset in package["package"]:
            if asset.get("format") == "visual_card":
                asset["claim_refs"] = all_claim_ids
                asset["source_refs"] = all_source_ids
            claim_refs = [
                ref for ref in asset.get("claim_refs", [])
                if isinstance(ref, str) and ref.strip()
            ]
            evidence_refs = []
            for claim_id in claim_refs:
                claim = claim_by_id.get(claim_id)
                if claim is None:
                    continue
                for evidence_id in claim.get("evidence_ids", []):
                    if isinstance(evidence_id, str) and evidence_id not in evidence_refs:
                        evidence_refs.append(evidence_id)
            asset["evidence_refs"] = evidence_refs
        quality = quality_check(package, research)
        quality["information_flow"] = {
            "status": "DEFERRED",
            "reason": "explicit ContentBrief is created by the editorial stage after research review",
        }
        if knowledge_capture is not None:
            research["knowledge"] = {
                "captured": True,
                "capture": knowledge_capture,
                "reusable_context_counts": {
                    key: len(value) for key, value in prior_knowledge.items()
                },
                "accepted_usage_count": knowledge_usage,
            }
        return VerticalSliceResult(
            run_id=run_id,
            brief=brief,
            research=research,
            package=package,
            quality=quality,
            information_flow={"status": "DEFERRED", "reason": "awaiting editorial ContentBrief"},
        )

    @staticmethod
    def to_dict(result: VerticalSliceResult) -> dict[str, Any]:
        return {
            "run_id": result.run_id,
            "brief": result.brief,
            "research": result.research,
            "package": result.package,
            "quality": result.quality,
            "information_flow": result.information_flow,
        }
