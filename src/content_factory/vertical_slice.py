from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from .knowledge import KnowledgeStore
from .research import OpenAIWebResearchAdapter, parse_research_json
from .gemini_research import GeminiGoogleSearchResearchAdapter
from .local_research import LocalResearchAdapter
from .research_quality import validate_research_relevance


@dataclass(frozen=True)
class VerticalSliceResult:
    run_id: str
    brief: str
    research: dict[str, Any]
    package: dict[str, Any]
    quality: dict[str, Any]


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
    ) -> None:
        if research_adapter is not None:
            self.research_adapter = research_adapter
        else:
            import os
            configured = os.environ.get("FACTORY_RESEARCH_PROVIDER", "").strip().lower()
            if configured == "gemini":
                self.research_adapter = GeminiGoogleSearchResearchAdapter()
            elif configured == "openai":
                self.research_adapter = OpenAIWebResearchAdapter()
            elif os.environ.get("OPENAI_API_KEY"):
                self.research_adapter = OpenAIWebResearchAdapter()
            else:
                self.research_adapter = LocalResearchAdapter()
        self.knowledge_store = knowledge_store

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
        result = self.research_adapter.research(research_prompt)
        if result.status_code < 200 or result.status_code >= 300:
            raise ValueError(f"research provider returned HTTP {result.status_code}")
        research_text = self.research_adapter.text(result)
        research = parse_research_json(research_text)
        provider_sources = self.research_adapter.sources(result)
        provider_search_queries = []
        if hasattr(self.research_adapter, "search_queries"):
            provider_search_queries = list(self.research_adapter.search_queries(result))
        declared = research.get("sources")
        if not isinstance(declared, list):
            declared = []
        known_urls = {item.get("url") for item in declared if isinstance(item, dict)}
        for source in provider_sources:
            if source["url"] not in known_urls:
                declared.append({"id": f"source-{len(declared) + 1}", "title": source["title"], "url": source["url"]})
                known_urls.add(source["url"])
        research["sources"] = declared
        if provider_search_queries:
            research["search_queries"] = provider_search_queries
        research_quality = validate_research_relevance(brief=brief, research=research)
        research["quality"] = research_quality
        if research_quality["status"] != "PASS":
            raise ValueError(
                "research relevance gate failed: "
                + str(research_quality.get("reason", "insufficient relevance"))
            )
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
            generated = self.research_adapter.research(production_prompt)
            if generated.status_code < 200 or generated.status_code >= 300:
                raise ValueError(f"production provider returned HTTP {generated.status_code}")
            asset = parse_research_json(self.research_adapter.text(generated))
            asset["id"] = f"{_slug(topic)}-{fmt}-v1"
            asset["format"] = fmt
            package["package"].append(asset)
        all_claim_ids = [c["id"] for c in claims if isinstance(c, dict)]
        all_source_ids = sorted({sid for c in claims if isinstance(c, dict) for sid in c.get("source_ids", [])})
        for asset in package["package"]:
            if asset.get("format") == "visual_card":
                asset["claim_refs"] = all_claim_ids
                asset["source_refs"] = all_source_ids
        quality = quality_check(package, research)
        if knowledge_capture is not None:
            research["knowledge"] = {
                "captured": True,
                "capture": knowledge_capture,
                "reusable_context_counts": {
                    key: len(value) for key, value in prior_knowledge.items()
                },
                "accepted_usage_count": knowledge_usage,
            }
        return VerticalSliceResult(run_id=run_id, brief=brief, research=research, package=package, quality=quality)

    @staticmethod
    def to_dict(result: VerticalSliceResult) -> dict[str, Any]:
        return {"run_id": result.run_id, "brief": result.brief, "research": result.research, "package": result.package, "quality": result.quality}