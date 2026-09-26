from __future__ import annotations

import json
from typing import Any

from .workspace import ContentWorkspace, WorkspaceError, _json_from_text, _require_source
from .runtime import WorkItem


class ContentRunPlanner:
    """Build a runtime-backed plan from a product-level ContentRun."""

    def __init__(self, workspace: ContentWorkspace) -> None:
        self.workspace = workspace

    def plan(
        self,
        *,
        run_id: str,
        title: str,
        brief: str,
        audience: str = "",
        goal: str = "",
        formats: list[str] | None = None,
        constraints: list[str] | None = None,
    ) -> dict[str, Any]:
        brief = _require_source(brief)
        formats = formats or []
        constraints = constraints or []
        prompt = f"""You are the planning layer of a personal Content Factory.
Create a concrete research and production plan from the user's content brief.
Do not research the topic and do not invent facts or sources.
Return ONLY valid JSON with this exact top-level shape:
{{
  "objective": "one sentence",
  "research_questions": ["question"],
  "source_requirements": ["specific source type or evidence needed"],
  "deliverables": [
    {{"format": "requested format", "purpose": "what this deliverable must accomplish"}}
  ],
  "editorial_constraints": ["constraint"],
  "quality_checks": ["check that must pass before review"]
}}
Rules:
- research_questions must be answerable by later evidence gathering;
- source_requirements must describe evidence needs, not fabricated citations;
- include every requested format in deliverables;
- preserve the user's constraints;
- do not claim that any research has already been completed.

Run id: {run_id}
Title: {title}
Audience: {audience}
Goal: {goal}
Requested formats: {json.dumps(formats, ensure_ascii=False)}
User constraints: {json.dumps(constraints, ensure_ascii=False)}

BRIEF:
{brief}
"""
        item = WorkItem(
            work_item_id=f"content-run-plan-{run_id}",
            revision_id="content-run-planning-v1",
            objective="turn a ContentRun brief into a research and production plan",
            requested_outcome=prompt,
            inputs=(f"content-run:{run_id}",),
            knowledge_basis=(),
            required_capabilities=(self.workspace.factory._capability.capability_id,),
            owner="content-run",
            acceptance_criteria=(
                "valid planning JSON",
                "no fabricated research claims",
                "all requested formats represented",
            ),
            release_requirements=("internal draft only",),
            operation_id=f"op-content-run-plan-{run_id}",
        )
        result = self.workspace._run_product_work_item(item)
        plan = _json_from_text(result["execution"]["output"])
        requested_formats = set(formats)
        deliverables = plan.get("deliverables")
        if not isinstance(deliverables, list):
            raise WorkspaceError("planning output must contain a deliverables array")
        delivered_formats = {
            entry.get("format")
            for entry in deliverables
            if isinstance(entry, dict) and isinstance(entry.get("format"), str)
        }
        if not requested_formats.issubset(delivered_formats):
            raise WorkspaceError("planning output omitted one or more requested formats")
        plan["runtime"] = {
            "work_item_id": result["work_item_id"],
            "operation_id": result["operation_id"],
            "execution_id": result["execution"]["execution_id"],
            "output_revision_id": result["execution"]["output_revision_id"],
            "state": result["state"],
        }
        return plan
