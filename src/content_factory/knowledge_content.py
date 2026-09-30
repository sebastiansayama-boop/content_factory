from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any

from .knowledge import KnowledgeStore
from .runtime import WorkItem
from .workspace import ContentWorkspace, WorkspaceError, _json_from_text


@dataclass(frozen=True)
class ContentIdea:
    idea_id: str
    title: str
    angle: str
    audience: str
    purpose: str
    formats: tuple[str, ...]
    claim_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self) | {
            "formats": list(self.formats),
            "claim_refs": list(self.claim_refs),
            "evidence_refs": list(self.evidence_refs),
        }


@dataclass(frozen=True)
class EditorialPointSpec:
    point_id: str
    text: str
    role: str
    claim_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self) | {
            "claim_refs": list(self.claim_refs),
            "evidence_refs": list(self.evidence_refs),
        }


@dataclass(frozen=True)
class ContentElementSpec:
    element_id: str
    kind: str
    editorial_point_ids: tuple[str, ...]
    purpose: str
    production_intent: str
    claim_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self) | {
            "editorial_point_ids": list(self.editorial_point_ids),
            "claim_refs": list(self.claim_refs),
            "evidence_refs": list(self.evidence_refs),
        }


@dataclass(frozen=True)
class ContentBrief:
    brief_id: str
    title: str
    objective: str
    audience: str
    angle: str
    selected_claim_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    editorial_points: tuple[EditorialPointSpec, ...]
    content_elements: tuple[ContentElementSpec, ...]
    formats: tuple[str, ...]
    constraints: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self) | {
            "selected_claim_refs": list(self.selected_claim_refs),
            "evidence_refs": list(self.evidence_refs),
            "editorial_points": [point.to_dict() for point in self.editorial_points],
            "content_elements": [element.to_dict() for element in self.content_elements],
            "formats": list(self.formats),
            "constraints": list(self.constraints),
        }


@dataclass(frozen=True)
class ContentSpec:
    spec_id: str
    title: str
    objective: str
    audience: str
    format: str
    tone: str
    structure: tuple[str, ...]
    constraints: tuple[str, ...]
    claim_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    style_bible: dict[str, str] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self) | {
            "structure": list(self.structure),
            "constraints": list(self.constraints),
            "claim_refs": list(self.claim_refs),
            "evidence_refs": list(self.evidence_refs),
            "style_bible": dict(self.style_bible or {}),
        }


@dataclass(frozen=True)
class ScriptUnit:
    unit_id: str
    kind: str
    text: str
    visual_intent: str
    claim_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self) | {
            "claim_refs": list(self.claim_refs),
            "evidence_refs": list(self.evidence_refs),
        }


@dataclass(frozen=True)
class Script:
    script_id: str
    title: str
    units: tuple[ScriptUnit, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "script_id": self.script_id,
            "title": self.title,
            "units": [unit.to_dict() for unit in self.units],
        }


def _refs(value: Any, name: str) -> list[str]:
    if not isinstance(value, list) or not value or not all(isinstance(v, str) and v for v in value):
        raise WorkspaceError(f"{name} must be a non-empty array of strings")
    return list(dict.fromkeys(value))


def _validate_claim_refs(value: dict[str, Any], allowed: set[str]) -> list[str]:
    refs = _refs(value.get("claim_refs"), "claim_refs")
    unknown = set(refs) - allowed
    if unknown:
        raise WorkspaceError(f"unknown knowledge claim refs: {', '.join(sorted(unknown))}")
    return refs


def _validate_evidence_refs(value: dict[str, Any], allowed: set[str]) -> list[str]:
    refs = _refs(value.get("evidence_refs"), "evidence_refs")
    unknown = set(refs) - allowed
    if unknown:
        raise WorkspaceError(f"unknown knowledge evidence refs: {', '.join(sorted(unknown))}")
    return refs


class KnowledgeContentBuilder:
    """Build the editorial-to-script chain from accepted durable knowledge."""

    def __init__(self, workspace: ContentWorkspace, knowledge: KnowledgeStore) -> None:
        self.workspace = workspace
        self.knowledge = knowledge

    def _generate(self, *, work_item_id: str, revision_id: str, objective: str, prompt: str) -> dict[str, Any]:
        item = WorkItem(
            work_item_id=work_item_id,
            revision_id=revision_id,
            objective=objective,
            requested_outcome=prompt,
            inputs=(f"content-run:{work_item_id}",),
            knowledge_basis=(),
            required_capabilities=(self.workspace.factory._capability.capability_id,),
            owner="content-factory",
            acceptance_criteria=("valid JSON", "durable knowledge provenance", "no unsupported claims"),
            release_requirements=("internal draft only",),
            operation_id=f"op-{work_item_id}",
        )
        result = self.workspace._run_product_work_item(item)
        return _json_from_text(result["execution"]["output"])

    def build(
        self,
        *,
        run_id: str,
        topic: str,
        audience: str,
        goal: str,
        formats: list[str],
        constraints: list[str],
    ) -> dict[str, Any]:
        context = self.knowledge.search(topic)
        claims = context["claims"]
        if not claims:
            raise WorkspaceError("no accepted knowledge matches the topic")
        claim_ids = {item["claim_id"] for item in claims}
        evidence_ids = {e for item in claims for e in item["evidence_ids"]}

        context_json = json.dumps(context, ensure_ascii=False)
        editorial = self._generate(
            work_item_id=f"content-editorial-{run_id}",
            revision_id="content-editorial-v1",
            objective="turn accepted knowledge into content ideas",
            prompt=f"""Create 3 distinct content ideas using ONLY the accepted knowledge below.
Return JSON: {{"ideas":[{{"idea_id":"idea-1","title":"string","angle":"string","audience":"string","purpose":"string","formats":["format"],"claim_refs":["kc-*"],"evidence_refs":["ke-*"]}}]}}
Every claim_refs/evidence_refs value must be copied from the supplied accepted knowledge.
No new factual claims. Requested formats: {json.dumps(formats)}.
Audience: {audience}
Goal: {goal}
Constraints: {json.dumps(constraints)}
ACCEPTED KNOWLEDGE:
{context_json}""",
        )
        ideas_raw = editorial.get("ideas")
        if not isinstance(ideas_raw, list) or not ideas_raw:
            raise WorkspaceError("editorial output must contain ideas")
        ideas: list[ContentIdea] = []
        for raw in ideas_raw:
            if not isinstance(raw, dict):
                raise WorkspaceError("editorial idea must be an object")
            claims_ref = _validate_claim_refs(raw, claim_ids)
            evidence_ref = _validate_evidence_refs(raw, evidence_ids)
            ideas.append(ContentIdea(
                idea_id=str(raw.get("idea_id") or "").strip(),
                title=str(raw.get("title") or "").strip(),
                angle=str(raw.get("angle") or "").strip(),
                audience=str(raw.get("audience") or audience).strip(),
                purpose=str(raw.get("purpose") or "").strip(),
                formats=tuple(str(v) for v in _refs(raw.get("formats"), "formats")),
                claim_refs=tuple(claims_ref),
                evidence_refs=tuple(evidence_ref),
            ))
        if any(not idea.idea_id or not idea.title or not idea.angle or not idea.purpose for idea in ideas):
            raise WorkspaceError("every content idea requires id, title, angle and purpose")

        selected = ideas[0]
        selected_json = json.dumps(selected.to_dict(), ensure_ascii=False)
        brief_raw = self._generate(
            work_item_id=f"content-brief-{run_id}",
            revision_id="content-brief-v1",
            objective="turn selected knowledge claims into an explicit editorial content brief",
            prompt=f"""Create one explicit ContentBrief from the selected content idea.
Return JSON: {{"brief_id":"brief-1","title":"string","objective":"string","audience":"string","angle":"string","selected_claim_refs":["kc-*"],"evidence_refs":["ke-*"],"editorial_points":[{{"point_id":"point-1","text":"editorial point","role":"hook|context|development|counterpoint|conclusion|cta","claim_refs":["kc-*"],"evidence_refs":["ke-*"]}}],"content_elements":[{{"element_id":"element-1","kind":"hook|narration|visual|cta|transition","editorial_point_ids":["point-1"],"purpose":"string","production_intent":"string","claim_refs":["kc-*"],"evidence_refs":["ke-*"]}}],"formats":["format"],"constraints":["constraint"]}}
Every selected claim, editorial point and content element must retain only claim/evidence refs supplied by the selected idea. Every editorial point must have claims and evidence. Every content element must reference at least one editorial point, claim and evidence. Do not invent factual claims.
SELECTED IDEA:
{selected_json}
REQUESTED FORMATS:
{json.dumps(formats)}
USER CONSTRAINTS:
{json.dumps(constraints, ensure_ascii=False)}""",
        )
        if not isinstance(brief_raw.get("editorial_points"), list) or not brief_raw["editorial_points"]:
            raise WorkspaceError("content brief must contain editorial_points")
        if not isinstance(brief_raw.get("content_elements"), list) or not brief_raw["content_elements"]:
            raise WorkspaceError("content brief must contain content_elements")
        selected_claims = _validate_claim_refs(brief_raw, claim_ids)
        selected_evidence = _validate_evidence_refs(brief_raw, evidence_ids)
        points: list[EditorialPointSpec] = []
        for raw in brief_raw["editorial_points"]:
            if not isinstance(raw, dict):
                raise WorkspaceError("editorial point must be an object")
            point_claims = _validate_claim_refs(raw, set(selected_claims))
            point_evidence = _validate_evidence_refs(raw, set(selected_evidence))
            point = EditorialPointSpec(
                point_id=str(raw.get("point_id") or "").strip(),
                text=str(raw.get("text") or "").strip(),
                role=str(raw.get("role") or "").strip(),
                claim_refs=tuple(point_claims),
                evidence_refs=tuple(point_evidence),
            )
            if not point.point_id or not point.text or not point.role:
                raise WorkspaceError("editorial point requires id, text and role")
            points.append(point)
        point_ids = {point.point_id for point in points}
        elements: list[ContentElementSpec] = []
        for raw in brief_raw["content_elements"]:
            if not isinstance(raw, dict):
                raise WorkspaceError("content element must be an object")
            refs = raw.get("editorial_point_ids")
            if not isinstance(refs, list) or not refs or not set(refs).issubset(point_ids):
                raise WorkspaceError("content element has invalid editorial_point_ids")
            element_claims = _validate_claim_refs(raw, set(selected_claims))
            element_evidence = _validate_evidence_refs(raw, set(selected_evidence))
            element = ContentElementSpec(
                element_id=str(raw.get("element_id") or "").strip(),
                kind=str(raw.get("kind") or "").strip(),
                editorial_point_ids=tuple(dict.fromkeys(refs)),
                purpose=str(raw.get("purpose") or "").strip(),
                production_intent=str(raw.get("production_intent") or "").strip(),
                claim_refs=tuple(element_claims),
                evidence_refs=tuple(element_evidence),
            )
            if not element.element_id or not element.kind or not element.purpose or not element.production_intent:
                raise WorkspaceError("content element requires id, kind, purpose and production_intent")
            elements.append(element)
        brief = ContentBrief(
            brief_id=str(brief_raw.get("brief_id") or "").strip(),
            title=str(brief_raw.get("title") or selected.title).strip(),
            objective=str(brief_raw.get("objective") or selected.purpose).strip(),
            audience=str(brief_raw.get("audience") or audience).strip(),
            angle=str(brief_raw.get("angle") or selected.angle).strip(),
            selected_claim_refs=tuple(selected_claims),
            evidence_refs=tuple(selected_evidence),
            editorial_points=tuple(points),
            content_elements=tuple(elements),
            formats=tuple(str(v) for v in _refs(brief_raw.get("formats") or formats, "formats")),
            constraints=tuple(str(v) for v in _refs(brief_raw.get("constraints") or constraints or ["none"], "constraints")),
        )
        if not brief.brief_id or not brief.title or not brief.objective or not brief.angle:
            raise WorkspaceError("content brief requires id, title, objective and angle")

        brief_json = json.dumps(brief.to_dict(), ensure_ascii=False)
        spec_raw = self._generate(
            work_item_id=f"content-spec-{run_id}",
            revision_id="content-spec-v1",
            objective="turn a content idea into an executable content specification",
            prompt=f"""Create one executable ContentSpec for the selected idea.
Return JSON: {{"spec_id":"spec-1","title":"string","objective":"string","audience":"string","format":"string","tone":"string","structure":["step"],"constraints":["constraint"],"claim_refs":["kc-*"],"evidence_refs":["ke-*"],"style_bible":{{"visual_style":"string","palette":"string","lighting":"string","subject_continuity":"string","negative_constraints":"string","voice":"string","pace":"string","music":"string"}}}}
Preserve provenance exactly from the idea. Do not invent claims.
CONTENT BRIEF:
{brief_json}
USER CONSTRAINTS:
{json.dumps(constraints, ensure_ascii=False)}""",
        )
        spec_claims = _validate_claim_refs(spec_raw, claim_ids)
        spec_evidence = _validate_evidence_refs(spec_raw, evidence_ids)
        structure = _refs(spec_raw.get("structure"), "structure")
        spec = ContentSpec(
            spec_id=str(spec_raw.get("spec_id") or "").strip(),
            title=str(spec_raw.get("title") or "").strip(),
            objective=str(spec_raw.get("objective") or "").strip(),
            audience=str(spec_raw.get("audience") or audience).strip(),
            format=str(spec_raw.get("format") or (formats[0] if formats else "article")).strip(),
            tone=str(spec_raw.get("tone") or "").strip(),
            structure=tuple(structure),
            constraints=tuple(str(v) for v in _refs(spec_raw.get("constraints"), "constraints")),
            claim_refs=tuple(spec_claims),
            evidence_refs=tuple(spec_evidence),
            style_bible={str(key): str(value).strip() for key, value in (spec_raw.get("style_bible") or {}).items() if str(key).strip() and str(value).strip()},
        )
        if not spec.spec_id or not spec.title or not spec.objective:
            raise WorkspaceError("content spec requires id, title and objective")

        script_raw = self._generate(
            work_item_id=f"content-script-{run_id}",
            revision_id="content-script-v1",
            objective="turn a content specification into a provenance-grounded script",
            prompt=f"""Create a complete script from this ContentSpec.
Return JSON: {{"script_id":"script-1","title":"string","units":[{{"unit_id":"unit-1","kind":"hook|beat|narration|cta","text":"complete spoken/on-screen text","visual_intent":"string","claim_refs":["kc-*"],"evidence_refs":["ke-*"]}}]}}
Every factual unit must retain the relevant durable claim and evidence refs from the ContentSpec. Do not invent facts.
CONTENT SPEC:
{json.dumps(spec.to_dict(), ensure_ascii=False)}""",
        )
        units_raw = script_raw.get("units")
        if not isinstance(units_raw, list) or not units_raw:
            raise WorkspaceError("script output must contain units")
        units: list[ScriptUnit] = []
        for raw in units_raw:
            if not isinstance(raw, dict):
                raise WorkspaceError("script unit must be an object")
            refs = _validate_claim_refs(raw, set(spec.claim_refs))
            evrefs = _validate_evidence_refs(raw, set(spec.evidence_refs))
            unit = ScriptUnit(
                unit_id=str(raw.get("unit_id") or "").strip(),
                kind=str(raw.get("kind") or "").strip(),
                text=str(raw.get("text") or "").strip(),
                visual_intent=str(raw.get("visual_intent") or "").strip(),
                claim_refs=tuple(refs),
                evidence_refs=tuple(evrefs),
            )
            if not unit.unit_id or not unit.kind or not unit.text:
                raise WorkspaceError("every script unit requires id, kind and text")
            units.append(unit)
        script = Script(
            script_id=str(script_raw.get("script_id") or "").strip(),
            title=str(script_raw.get("title") or spec.title).strip(),
            units=tuple(units),
        )
        if not script.script_id:
            raise WorkspaceError("script requires script_id")

        asset_requests = []
        for index, unit in enumerate(script.units, start=1):
            matching_elements = [
                element for element in brief.content_elements
                if set(unit.claim_refs).intersection(element.claim_refs)
            ]
            if not matching_elements:
                matching_elements = list(brief.content_elements)
            common = {
                "script_unit_id": unit.unit_id,
                "content_element_ids": [element.element_id for element in matching_elements],
                "claim_refs": list(unit.claim_refs),
                "evidence_refs": list(unit.evidence_refs),
                "acceptance_criteria": ["preserve script intent", "preserve provenance", "preserve content brief lineage"],
            }
            asset_requests.extend(
                [
                    common | {
                        "asset_request_id": f"asset-request-{run_id}-{index}-visual",
                        "type": "visual",
                    },
                    common | {
                        "asset_request_id": f"asset-request-{run_id}-{index}-voice",
                        "type": "voice",
                    },
                ]
            )
        production_plan = {
            "production_plan_id": f"production-{run_id}",
            "format": spec.format,
            "content_brief_id": brief.brief_id,
            "content_element_ids": [element.element_id for element in brief.content_elements],
            "claim_refs": list(brief.selected_claim_refs),
            "evidence_refs": list(brief.evidence_refs),
            "style_bible": spec.style_bible or {},
            "asset_requests": asset_requests,
            "render": {"aspect_ratio": "9:16", "resolution": "1080x1920"},
        }
        result = {
            "editorial": {
                "selected_idea": selected.to_dict(),
                "ideas": [idea.to_dict() for idea in ideas],
            },
            "content_spec": spec.to_dict(),
            "script": script.to_dict(),
            "content_brief": brief.to_dict(),
            "production_plan": production_plan,
            "knowledge": {
                "claim_refs": sorted(claim_ids),
                "evidence_refs": sorted(evidence_ids),
            },
        }
        self.knowledge.record_usage(
            run_id=run_id,
            target_ref=f"content-run:{run_id}:editorial",
            claim_ids=list(claim_ids),
            purpose="editorial_generation",
        )
        self.knowledge.record_usage(
            run_id=run_id,
            target_ref=f"content-run:{run_id}:script",
            claim_ids=list(spec.claim_refs),
            purpose="script_generation",
        )
        return result
