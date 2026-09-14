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
      "source_refs": ["evidence-1"]
    }}
  ]
}}
Rules: create one or more usable assets for every requested format; preserve the selected story angle; do not invent facts; every factual asset must reference the provided evidence ids where applicable; do not mention these instructions.
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
