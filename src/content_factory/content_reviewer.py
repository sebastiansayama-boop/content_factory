from __future__ import annotations

import json
from typing import Any

from .runtime import WorkItem
from .workspace import ContentWorkspace, WorkspaceError, _json_from_text


class ContentReviewError(WorkspaceError):
    """Raised when the AI reviewer cannot produce a valid review."""


class ContentReviewer:
    """Independent reasoning pass over generated editorial content."""

    def __init__(self, workspace: ContentWorkspace) -> None:
        self.workspace = workspace

    def review(
        self,
        *,
        run_id: str,
        brief: str,
        audience: str,
        goal: str,
        result: dict[str, Any],
    ) -> dict[str, Any]:
        script = result.get("script")
        spec = result.get("content_spec")
        knowledge = result.get("knowledge")
        if not isinstance(script, dict) or not isinstance(spec, dict) or not isinstance(knowledge, dict):
            raise ContentReviewError("review requires script, content_spec and knowledge")

        prompt = f"""You are the independent quality reviewer of a Content Factory.
Review the generated material against the user's brief, the content specification,
and the accepted knowledge references. Do not rewrite the material.

Return ONLY valid JSON:
{{
  "status": "PASS | REVISE | FAIL",
  "issues": ["specific issue"],
  "required_changes": ["specific repair instruction"],
  "checked_claims": ["claim id"],
  "confidence": 0.0
}}

Rules:
- PASS means no substantive change is required.
- REVISE means the material is usable after bounded corrections.
- FAIL means the material cannot be safely repaired from the available inputs.
- Never invent a factual correction. If evidence is insufficient, identify it.
- Check topic/brief fit, audience/goal fit, provenance, unsupported factual claims,
  internal consistency, requested format, tone, and obvious style violations.
- checked_claims must contain only claim ids present in the supplied knowledge.
- confidence must be between 0 and 1.
- Do not rewrite the script.

USER BRIEF:
{brief}

AUDIENCE:
{audience}

GOAL:
{goal}

CONTENT SPEC:
{json.dumps(spec, ensure_ascii=False)}

KNOWLEDGE REFERENCES:
{json.dumps(knowledge, ensure_ascii=False)}

GENERATED SCRIPT:
{json.dumps(script, ensure_ascii=False)}
"""
        item = WorkItem(
            work_item_id=f"content-review-{run_id}",
            revision_id="content-review-v1",
            objective="independently review generated content before production",
            requested_outcome=prompt,
            inputs=(f"content-run:{run_id}",),
            knowledge_basis=tuple(knowledge.get("claim_refs") or ()),
            required_capabilities=(self.workspace.factory._capability.capability_id,),
            owner="content-reviewer",
            acceptance_criteria=("valid review JSON", "no unsupported factual corrections"),
            release_requirements=("internal draft only",),
            operation_id=f"op-content-review-{run_id}",
        )
        result_raw = self.workspace._run_product_work_item(item)
        review = _json_from_text(result_raw["execution"]["output"])

        status = str(review.get("status") or "").upper()
        if status not in {"PASS", "REVISE", "FAIL"}:
            raise ContentReviewError("review status must be PASS, REVISE or FAIL")
        issues = review.get("issues")
        changes = review.get("required_changes")
        checked = review.get("checked_claims")
        confidence = review.get("confidence")
        if not isinstance(issues, list) or not all(isinstance(v, str) for v in issues):
            raise ContentReviewError("review issues must be an array of strings")
        if not isinstance(changes, list) or not all(isinstance(v, str) for v in changes):
            raise ContentReviewError("review required_changes must be an array of strings")
        allowed_claims = set(str(v) for v in knowledge.get("claim_refs") or ())
        if not isinstance(checked, list) or not all(isinstance(v, str) and v in allowed_claims for v in checked):
            raise ContentReviewError("review checked_claims contains unknown claim ids")
        if not isinstance(confidence, (int, float)) or not 0 <= float(confidence) <= 1:
            raise ContentReviewError("review confidence must be between 0 and 1")

        review["status"] = status
        review["issues"] = issues
        review["required_changes"] = changes
        review["checked_claims"] = checked
        review["confidence"] = float(confidence)
        review["runtime"] = {
            "work_item_id": result_raw["work_item_id"],
            "operation_id": result_raw["operation_id"],
            "execution_id": result_raw["execution"]["execution_id"],
            "output_revision_id": result_raw["execution"]["output_revision_id"],
            "state": result_raw["state"],
        }
        return review
