from __future__ import annotations

import hashlib
import json
import re
from typing import Any

from .runtime import AcceptanceDecision, FactoryRuntime, VerificationResult, WorkItem
from .service import LocalReleasePublisher


MAX_SOURCE_CHARS = 60_000


class WorkspaceError(ValueError):
    pass


def _source_id(source: str) -> str:
    return hashlib.sha256(source.encode("utf-8")).hexdigest()[:16]


def _json_from_text(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        value = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start < 0 or end <= start:
            raise WorkspaceError("provider did not return valid JSON") from exc
        try:
            value = json.loads(cleaned[start : end + 1])
        except json.JSONDecodeError as nested:
            raise WorkspaceError("provider did not return valid JSON") from nested
    if not isinstance(value, dict):
        raise WorkspaceError("provider JSON must be an object")
    return value


def _require_source(source: str) -> str:
    source = source.strip()
    if not source:
        raise WorkspaceError("source is required")
    if len(source) > MAX_SOURCE_CHARS:
        raise WorkspaceError(f"source exceeds {MAX_SOURCE_CHARS} characters")
    return source


def _require_story_provenance(story: dict[str, Any]) -> None:
    evidence_ids = {
        item["id"]
        for item in story.get("evidence", [])
        if isinstance(item, dict) and item.get("id")
    }
    claims = story.get("claims")
    if not isinstance(claims, list) or not claims:
        raise WorkspaceError("story.claims are required for claim-level provenance")

    seen: set[str] = set()
    for claim in claims:
        if not isinstance(claim, dict) or not claim.get("id"):
            raise WorkspaceError("every story claim requires an id")
        claim_id = claim["id"]
        if claim_id in seen:
            raise WorkspaceError(f"duplicate story claim id: {claim_id}")
        seen.add(claim_id)
        evidence_refs = {
            ref for ref in claim.get("evidence_refs", []) if isinstance(ref, str)
        }
        if not evidence_refs:
            raise WorkspaceError(f"claim {claim_id} requires evidence_refs")
        if not evidence_refs.issubset(evidence_ids):
            unknown = sorted(evidence_refs - evidence_ids)
            raise WorkspaceError(
                f"claim {claim_id} references unknown evidence ids: {', '.join(unknown)}"
            )


class ContentWorkspace:
    """Product layer over the executable factory, with an external-effect boundary.

    Product analysis and production are deliberately released only to an
    internal sink. Configuring PUBLISH_URL must never cause a draft generated
    by the workspace to be sent to an external destination.
    """

    def __init__(self, factory_service: Any) -> None:
        self.factory = factory_service

    def _run_product_work_item(self, item: WorkItem) -> dict[str, Any]:
        runtime = FactoryRuntime(
            publisher=LocalReleasePublisher(),
            artifact_store=self.factory._artifacts,
            runtime_store=self.factory._store,
        )
        runtime.register_capability(self.factory._capability)
        if item.work_item_id not in runtime.states:
            runtime.submit(item, actor="workspace")
        elif runtime.operation_ids.get(item.work_item_id) != item.operation_id:
            raise WorkspaceError("product work item operation_id conflicts with durable state")
        runtime.run(
            item,
            verification=self.factory._verify,
            acceptance=lambda _, verified: AcceptanceDecision(
                output_revision_id=verified.output_revision_id,
                accepted=True,
                authority="system:workspace-internal",
                reason="workspace draft generation",
            ),
            release_authority="system:workspace-internal",
            actor="workspace",
        )
        execution = runtime.executions.get(item.work_item_id)
        if execution is None:
            raise WorkspaceError(f"product work item did not produce an execution: {runtime.states[item.work_item_id].value}")
        return {
            "work_item_id": item.work_item_id,
            "operation_id": item.operation_id,
            "state": runtime.states[item.work_item_id].value,
            "execution": {
                "execution_id": execution.execution_id,
                "output_revision_id": execution.output_revision_id,
                "output": execution.payload,
            },
        }

    def analyze(self, *, source: str, title: str = "Untitled source") -> dict[str, Any]:
        source = _require_source(source)
        prompt = f"""You are the editorial intelligence layer of a Content Factory.
Analyze the source material below. Do not write the final content yet.
Return ONLY valid JSON with this exact top-level shape:
{{
  "summary": "string",
  "themes": ["string"],
  "stories": [
    {{
      "id": "story-1",
      "title": "string",
      "angle": "string",
      "why": "string",
      "evidence": [
        {{"id": "evidence-1", "quote": "short exact quote from source", "location": "approximate section or context"}}
      ],
      "claims": [
        {{"id": "claim-1", "text": "atomic factual claim", "evidence_refs": ["evidence-1"]}}
      ]
    }}
  ],
  "moments": [
    {{"id": "moment-1", "title": "string", "description": "string", "source_hint": "string"}}
  ]
}}
Rules: propose 5-8 distinct stories; ground every story in source evidence; do not invent facts; keep evidence quotes short; stories must be materially different angles. Every claim must be atomic and cite one or more evidence ids from the same story via evidence_refs. Do not create claims without evidence_refs.
Source title: {title}

SOURCE MATERIAL:
{source}
"""
        item = WorkItem(
            work_item_id=f"workspace-analyze-{_source_id(source)}",
            revision_id="workspace-analysis-v1",
            objective="map source material into reusable editorial objects",
            requested_outcome=prompt,
            inputs=(f"source:{_source_id(source)}",),
            knowledge_basis=(),
            required_capabilities=(self.factory._capability.capability_id,),
            owner="workspace",
            acceptance_criteria=("valid editorial JSON", "source-grounded stories"),
            release_requirements=("internal draft only",),
            operation_id=f"op-workspace-analyze-{_source_id(source)}",
        )
        result = self._run_product_work_item(item)
        analysis = _json_from_text(result["execution"]["output"])
        analysis["source_id"] = _source_id(source)
        analysis["title"] = title.strip() or "Untitled source"
        analysis["runtime"] = {
            "work_item_id": result["work_item_id"],
            "operation_id": result["operation_id"],
            "execution_id": result["execution"]["execution_id"],
            "output_revision_id": result["execution"]["output_revision_id"],
            "state": result["state"],
        }
        return analysis

    def regenerate(
        self,
        *,
        source: str,
        story: dict[str, Any],
        package: dict[str, Any],
        changed_claim_ids: list[str] | tuple[str, ...],
    ) -> dict[str, Any]:
        """Regenerate only assets affected by changed claims."""
        source = _require_source(source)
        if not story.get("id") or not story.get("title"):
            raise WorkspaceError("story.id and story.title are required")
        _require_story_provenance(story)

        from .content_provenance import ProvenanceGraph, ProvenanceError

        try:
            graph = ProvenanceGraph.from_package(
                package,
                run_id=str(package.get("runtime", {}).get("execution_id", "regeneration")),
                provider="workspace",
            )
            plan = graph.regeneration_plan(changed_claim_ids=changed_claim_ids)
        except ProvenanceError as exc:
            raise WorkspaceError(str(exc)) from exc

        assets_by_id = {
            item.get("id"): item
            for item in package.get("package", [])
            if isinstance(item, dict) and item.get("id")
        }
        regenerated: list[dict[str, Any]] = []

        for target in plan.targets:
            original = assets_by_id[target.asset_id]
            prompt = f"""You are the revision layer of a Content Factory.
Regenerate exactly ONE existing asset because specific factual claims changed.
Return ONLY valid JSON for one asset:
{{
  "id": "{target.asset_id}",
  "format": "{original.get("format", "")}",
  "title": "string",
  "content": "complete usable content",
  "source_refs": ["evidence-id"],
  "claim_refs": ["claim-id"]
}}
Preserve the asset format and editorial purpose. Incorporate the changed claims
without rewriting unrelated claims unless required for factual consistency.
Every referenced claim must be supported by the asset source_refs.
Changed claims: {json.dumps(target.changed_claim_ids, ensure_ascii=False)}
Current asset:
{json.dumps(original, ensure_ascii=False)}
Selected story:
{json.dumps(story, ensure_ascii=False)}
ORIGINAL SOURCE:
{source}
"""
            source_key = _source_id(source)
            item = WorkItem(
                work_item_id=f"workspace-regenerate-{source_key}-{story['id']}-{target.asset_id}",
                revision_id=f"workspace-regeneration-{target.asset_id}-v1",
                objective=f"regenerate asset {target.asset_id} after claim change",
                requested_outcome=prompt,
                inputs=(f"source:{source_key}", f"story:{story['id']}", f"asset:{target.asset_id}"),
                knowledge_basis=tuple(target.changed_claim_ids),
                required_capabilities=(self.factory._capability.capability_id,),
                owner="workspace",
                acceptance_criteria=("valid single-asset JSON", "changed claims incorporated"),
                release_requirements=("internal draft only",),
                dependencies=tuple(target.changed_claim_ids),
                operation_id=f"op-workspace-regenerate-{source_key}-{story['id']}-{target.asset_id}",
            )
            result = self._run_product_work_item(item)
            regenerated_asset = _json_from_text(result["execution"]["output"])
            if regenerated_asset.get("id") != target.asset_id:
                raise WorkspaceError(
                    f"regenerated asset id mismatch: expected {target.asset_id}"
                )
            regenerated.append(regenerated_asset)

        replacement_by_id = {asset["id"]: asset for asset in regenerated}
        output = dict(package)
        output["package"] = [
            replacement_by_id.get(asset.get("id"), asset)
            for asset in package.get("package", [])
        ]
        output["regeneration"] = {
            "changed_claim_ids": list(plan.changed_claim_ids),
            "regenerated_asset_ids": list(plan.regenerate_asset_ids),
            "retained_asset_ids": list(plan.retain_asset_ids),
            "targets": [
                {
                    "asset_id": target.asset_id,
                    "changed_claim_ids": list(target.changed_claim_ids),
                }
                for target in plan.targets
            ],
        }
        return output

    def produce(
        self,
        *,
        source: str,
        story: dict[str, Any],
        formats: list[str] | None = None,
    ) -> dict[str, Any]:
        source = _require_source(source)
        if not story.get("id") or not story.get("title"):
            raise WorkspaceError("story.id and story.title are required")
        _require_story_provenance(story)
        formats = formats or ["long_video", "shorts", "article", "social_posts"]
        format_text = ", ".join(formats)
        prompt = f"""You are the production layer of a Content Factory.
Create a production package from the selected editorial story and the original source.
Return ONLY valid JSON with this exact top-level shape:
{{
  "story": {{"id": "string", "title": "string", "angle": "string"}},
  "package": [
    {{
      "id": "asset-1",
      "format": "one requested format",
      "title": "string",
      "content": "complete usable content",
      "source_refs": ["evidence-1"],
      "claim_refs": ["claim-1"]
    }}
  ]
}}
Rules: create one or more usable assets for every requested format; preserve the selected story angle; do not invent facts; every factual asset must reference the provided evidence ids where applicable. claim_refs must contain only claim ids from the selected story, and each referenced claim must be supported by at least one source_ref in that asset. Do not mention these instructions.
Requested formats: {format_text}
Selected story:
{json.dumps(story, ensure_ascii=False)}

ORIGINAL SOURCE:
{source}
"""
        source_key = _source_id(source)
        item = WorkItem(
            work_item_id=f"workspace-produce-{source_key}-{story['id']}",
            revision_id="workspace-production-v1",
            objective="materialize a selected story into a multi-format content package",
            requested_outcome=prompt,
            inputs=(f"source:{source_key}", f"story:{story['id']}"),
            knowledge_basis=(f"source:{source_key}", f"story:{story['id']}"),
            required_capabilities=(self.factory._capability.capability_id,),
            owner="workspace",
            acceptance_criteria=("valid production JSON", "all requested formats represented"),
            release_requirements=("internal draft only",),
            operation_id=f"op-workspace-produce-{source_key}-{story['id']}",
        )
        result = self._run_product_work_item(item)
        package = _json_from_text(result["execution"]["output"])

        story_evidence = {
            item["id"]
            for item in story.get("evidence", [])
            if isinstance(item, dict) and item.get("id")
        }
        claims = [
            item
            for item in story.get("claims", [])
            if isinstance(item, dict) and item.get("id")
        ]
        claim_by_id = {item["id"]: item for item in claims}
        for asset in package.get("package", []):
            if not isinstance(asset, dict):
                continue
            source_refs = {
                ref for ref in asset.get("source_refs", []) if isinstance(ref, str)
            }
            if source_refs and not source_refs.issubset(story_evidence):
                unknown = sorted(source_refs - story_evidence)
                raise WorkspaceError(
                    f"asset references unknown evidence ids: {', '.join(unknown)}"
                )

            explicit_claim_refs = [
                ref for ref in asset.get("claim_refs", []) if isinstance(ref, str)
            ]
            for claim_id in explicit_claim_refs:
                claim = claim_by_id.get(claim_id)
                if claim is None:
                    raise WorkspaceError(
                        f"asset references unknown claim id: {claim_id}"
                    )
                claim_evidence = {
                    ref
                    for ref in claim.get("evidence_refs", [])
                    if isinstance(ref, str)
                }
                if not claim_evidence or not claim_evidence.issubset(source_refs):
                    raise WorkspaceError(
                        f"claim {claim_id} is not supported by asset source_refs"
                    )

            derived_claim_refs = [
                claim_id
                for claim_id, claim in claim_by_id.items()
                if set(claim.get("evidence_refs", [])) & source_refs
            ]
            asset["claim_refs"] = explicit_claim_refs or derived_claim_refs
        package["source_id"] = source_key
        package["story_id"] = story["id"]
        package["runtime"] = {
            "work_item_id": result["work_item_id"],
            "operation_id": result["operation_id"],
            "execution_id": result["execution"]["execution_id"],
            "output_revision_id": result["execution"]["output_revision_id"],
            "state": result["state"],
        }
        return package
