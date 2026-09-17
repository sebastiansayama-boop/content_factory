from __future__ import annotations

import hashlib
import json
import re
from typing import Any

from .runtime import AcceptanceDecision, FactoryRuntime, VerificationResult, WorkItem
from .service import LocalReleasePublisher


MAX_SOURCE_CHARS = 60_000
FIRST_SECTOR_FORMATS = ("article", "social_posts")


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


class ContentWorkspace:
    """Product layer for the first end-to-end user sector.

    Analysis and production are released only to the internal draft sink.
    External publishing is outside this sector.
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
        source_id = _source_id(source)
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
      ]
    }}
  ],
  "moments": [
    {{"id": "moment-1", "title": "string", "description": "string", "source_hint": "string"}}
  ]
}}
Rules: propose 5-8 distinct stories; ground every story in source evidence; do not invent facts; keep evidence quotes short; stories must be materially different angles.
Source title: {title}

SOURCE MATERIAL:
{source}
"""
        item = WorkItem(
            work_item_id=f"workspace-analyze-{source_id}",
            revision_id="workspace-analysis-v1",
            objective="map source material into reusable editorial objects",
            requested_outcome=prompt,
            inputs=(f"source:{source_id}",),
            knowledge_basis=(),
            required_capabilities=(self.factory._capability.capability_id,),
            owner="workspace",
            acceptance_criteria=("valid editorial JSON", "source-grounded stories"),
            release_requirements=("internal draft only",),
            operation_id=f"op-workspace-analyze-{source_id}",
        )
        result = self._run_product_work_item(item)
        analysis = _json_from_text(result["execution"]["output"])
        stories = analysis.get("stories")
        if not isinstance(stories, list) or not stories:
            raise WorkspaceError("analysis produced no stories")
        normalized_stories: list[dict[str, Any]] = []
        for story in stories:
            if not isinstance(story, dict) or not story.get("id") or not story.get("title"):
                continue
            evidence = story.get("evidence")
            if not isinstance(evidence, list) or not evidence:
                continue
            normalized = dict(story)
            normalized["source_id"] = source_id
            normalized_stories.append(normalized)
        if not normalized_stories:
            raise WorkspaceError("analysis produced no stories with source evidence")
        analysis["stories"] = normalized_stories
        analysis["source_id"] = source_id
        analysis["title"] = title.strip() or "Untitled source"
        analysis["runtime"] = {
            "work_item_id": result["work_item_id"],
            "operation_id": result["operation_id"],
            "execution_id": result["execution"]["execution_id"],
            "output_revision_id": result["execution"]["output_revision_id"],
            "state": result["state"],
        }
        return analysis

    def produce(
        self,
        *,
        source: str,
        story: dict[str, Any],
        formats: list[str] | None = None,
    ) -> dict[str, Any]:
        source = _require_source(source)
        source_id = _source_id(source)
        if not story.get("id") or not story.get("title"):
            raise WorkspaceError("story.id and story.title are required")
        if story.get("source_id") != source_id:
            raise WorkspaceError("selected story does not belong to this source")
        evidence = story.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            raise WorkspaceError("selected story must contain source evidence")
        evidence_ids = [str(item.get("id")) for item in evidence if isinstance(item, dict) and item.get("id")]
        if not evidence_ids:
            raise WorkspaceError("selected story contains no usable evidence references")
        formats = formats or list(FIRST_SECTOR_FORMATS)
        invalid = [value for value in formats if value not in FIRST_SECTOR_FORMATS]
        if invalid:
            raise WorkspaceError(f"unsupported first-sector format(s): {', '.join(sorted(set(invalid)))}")
        formats = list(dict.fromkeys(formats))
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
      "source_refs": ["evidence-1"]
    }}
  ]
}}
Rules: create one usable asset for every requested format; preserve the selected story angle; do not invent facts; every factual asset must reference one or more provided evidence ids; do not mention these instructions.
Requested formats: {format_text}
Allowed formats for this product sector: article, social_posts
Selected story:
{json.dumps(story, ensure_ascii=False)}

ORIGINAL SOURCE:
{source}
"""
        item = WorkItem(
            work_item_id=f"workspace-produce-{source_id}-{story['id']}",
            revision_id="workspace-production-v1",
            objective="materialize a selected story into an article and social posts",
            requested_outcome=prompt,
            inputs=(f"source:{source_id}", f"story:{story['id']}"),
            knowledge_basis=(f"source:{source_id}", f"story:{story['id']}", *evidence_ids),
            required_capabilities=(self.factory._capability.capability_id,),
            owner="workspace",
            acceptance_criteria=("valid production JSON", "all requested formats represented", "source references present"),
            release_requirements=("internal draft only",),
            operation_id=f"op-workspace-produce-{source_id}-{story['id']}",
        )
        result = self._run_product_work_item(item)
        package = _json_from_text(result["execution"]["output"])
        assets = package.get("package")
        if not isinstance(assets, list):
            raise WorkspaceError("provider returned no package")
        returned_formats = {asset.get("format") for asset in assets if isinstance(asset, dict)}
        missing_formats = set(formats) - returned_formats
        if missing_formats:
            raise WorkspaceError(f"provider omitted requested format(s): {', '.join(sorted(missing_formats))}")
        missing_refs = [
            str(asset.get("format"))
            for asset in assets
            if isinstance(asset, dict)
            and asset.get("format") in formats
            and not isinstance(asset.get("source_refs"), list)
        ]
        if missing_refs:
            raise WorkspaceError(f"asset source references missing for: {', '.join(missing_refs)}")
        package["package"] = assets
        package["source_id"] = source_id
        package["story_id"] = story["id"]
        package["runtime"] = {
            "work_item_id": result["work_item_id"],
            "operation_id": result["operation_id"],
            "execution_id": result["execution"]["execution_id"],
            "output_revision_id": result["execution"]["output_revision_id"],
            "state": result["state"],
        }
        return package
