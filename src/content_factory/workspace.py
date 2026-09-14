from __future__ import annotations

import hashlib
import json
import re
from typing import Any


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
    """Thin product layer over the existing executable factory runtime.

    The product deliberately keeps the first vertical slice narrow:
    source material -> content map -> selected story -> production package.
    Provider output is parsed into explicit JSON so the UI never depends on
    prose formatting or model-specific markup.
    """

    def __init__(self, factory_service: Any) -> None:
        self.factory = factory_service

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
        result = self.factory.run(
            {
                "work_item_id": f"workspace-analyze-{_source_id(source)}",
                "revision_id": "workspace-analysis-v1",
                "objective": "map source material into reusable editorial objects",
                "requested_outcome": prompt,
                "owner": "workspace",
                "acceptance_authority": "system:workspace-analysis",
                "release_authority": "system:workspace-analysis",
                "acceptance_criteria": ["valid editorial JSON", "source-grounded stories"],
            }
        )
        payload = result.get("execution", {}).get("output", "")
        analysis = _json_from_text(payload)
        analysis["source_id"] = _source_id(source)
        analysis["title"] = title.strip() or "Untitled source"
        analysis["runtime"] = {
            "work_item_id": result.get("work_item_id"),
            "operation_id": result.get("operation_id"),
            "execution_id": result.get("execution", {}).get("execution_id"),
            "output_revision_id": result.get("execution", {}).get("output_revision_id"),
            "state": result.get("state"),
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
        result = self.factory.run(
            {
                "work_item_id": f"workspace-produce-{_source_id(source)}-{story['id']}",
                "revision_id": "workspace-production-v1",
                "objective": "materialize a selected story into a multi-format content package",
                "requested_outcome": prompt,
                "owner": "workspace",
                "knowledge_basis": [f"source:{_source_id(source)}", f"story:{story['id']}"],
                "acceptance_authority": "system:workspace-production",
                "release_authority": "system:workspace-production",
                "acceptance_criteria": ["valid production JSON", "all requested formats represented"],
            }
        )
        payload = result.get("execution", {}).get("output", "")
        package = _json_from_text(payload)
        package["source_id"] = _source_id(source)
        package["story_id"] = story["id"]
        package["runtime"] = {
            "work_item_id": result.get("work_item_id"),
            "operation_id": result.get("operation_id"),
            "execution_id": result.get("execution", {}).get("execution_id"),
            "output_revision_id": result.get("execution", {}).get("output_revision_id"),
            "state": result.get("state"),
        }
        return package
