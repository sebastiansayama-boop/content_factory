from __future__ import annotations

import hashlib
import json
import re

from .integrations import ExternalCallResult


class LocalTextAdapter:
    """Deterministic credential-free provider for development and smoke tests."""

    @staticmethod
    def _refs(prompt: str) -> tuple[str, str]:
        claims = re.findall(r"kc-[A-Za-z0-9_-]+", prompt)
        evidence = re.findall(r"ke-[A-Za-z0-9_-]+", prompt)
        return (claims[0] if claims else "kc-local"), (evidence[0] if evidence else "ke-local")

    def generate(self, prompt: str) -> ExternalCallResult:
        if not prompt.strip():
            raise ValueError("prompt must not be empty")
        claim, evidence = self._refs(prompt)
        if '"ideas":' in prompt:
            value = {
                "ideas": [
                    {"idea_id": "idea-local-1", "title": "Evidence-grounded story", "angle": "Explain the supplied evidence clearly", "audience": "general audience", "purpose": "inform", "formats": ["short_video"], "claim_refs": [claim], "evidence_refs": [evidence]},
                    {"idea_id": "idea-local-2", "title": "What the evidence shows", "angle": "Turn the supplied evidence into a concise narrative", "audience": "general audience", "purpose": "educate", "formats": ["short_video"], "claim_refs": [claim], "evidence_refs": [evidence]},
                    {"idea_id": "idea-local-3", "title": "One claim, one story", "angle": "Build a focused content piece around the supplied claim", "audience": "general audience", "purpose": "inform", "formats": ["short_video"], "claim_refs": [claim], "evidence_refs": [evidence]},
                ]
            }
        elif '"editorial_points":' in prompt and "Create one explicit ContentBrief" in prompt:
            value = {
                "brief_id": "brief-local-1",
                "title": "Evidence-grounded short",
                "objective": "Create a concise evidence-grounded short",
                "audience": "general audience",
                "angle": "Explain the supplied evidence clearly",
                "selected_claim_refs": [claim],
                "evidence_refs": [evidence],
                "editorial_points": [
                    {"point_id": "point-1", "text": "Explain the supplied evidence clearly", "role": "development", "claim_refs": [claim], "evidence_refs": [evidence]}
                ],
                "content_elements": [
                    {"element_id": "element-1", "kind": "narration", "editorial_point_ids": ["point-1"], "purpose": "explain the claim", "production_intent": "voice narration", "claim_refs": [claim], "evidence_refs": [evidence]}
                ],
                "formats": ["short_video"],
                "constraints": ["use only supplied knowledge"],
            }
        elif '"units":' in prompt:
            title = "Evidence-grounded story"
            claims_data = []
            marker = "ACCEPTED KNOWLEDGE:"
            if marker in prompt:
                try:
                    context = json.loads(prompt.split(marker, 1)[1].strip())
                    claims_data = context.get("claims", []) if isinstance(context, dict) else []
                except json.JSONDecodeError:
                    claims_data = []

            claim_item = next(
                (item for item in claims_data if isinstance(item, dict) and item.get("text")),
                {},
            )
            claim_text = str(claim_item.get("text") or "").strip() or (
                "The supplied evidence supports the selected claim."
            )
            claim_id = str(claim_item.get("claim_id") or "").strip() or claim
            evidence_ids = claim_item.get("evidence_ids", [])
            evidence_id = next(
                (str(item).strip() for item in evidence_ids if isinstance(item, str) and item.strip()),
                evidence,
            )
            scope = str(claim_item.get("scope") or "").strip()
            evidence_item = next(
                (
                    item for item in (claims_data and context.get("evidence", []) or [])
                    if isinstance(item, dict) and str(item.get("evidence_id") or item.get("id") or "").strip() == evidence_id
                ),
                {},
            )
            evidence_excerpt = str(evidence_item.get("excerpt") or "").strip()

            units = [
                {
                    "unit_id": "unit-1",
                    "kind": "hook",
                    "text": f"Вот что показывает доступное свидетельство по этой теме: {claim_text}",
                    "visual_intent": "establish topic",
                    "claim_refs": [claim_id],
                    "evidence_refs": [evidence_id],
                },
                {
                    "unit_id": "unit-2",
                    "kind": "narration",
                    "text": f"Само утверждение сформулировано так: {claim_text}",
                    "visual_intent": "show claim",
                    "claim_refs": [claim_id],
                    "evidence_refs": [evidence_id],
                },
                {
                    "unit_id": "unit-3",
                    "kind": "narration",
                    "text": f"В источнике зафиксировано следующее: {evidence_excerpt or claim_text}",
                    "visual_intent": "show evidence",
                    "claim_refs": [claim_id],
                    "evidence_refs": [evidence_id],
                },
            ]
            if scope:
                units.append(
                    {
                        "unit_id": f"unit-{len(units) + 1}",
                        "kind": "narration",
                        "text": f"При этом область утверждения ограничена: {scope}.",
                        "visual_intent": "show scope",
                        "claim_refs": [claim_id],
                        "evidence_refs": [evidence_id],
                    }
                )
            units.append(
                {
                    "unit_id": f"unit-{len(units) + 1}",
                    "kind": "narration",
                    "text": f"Итог следует читать только в пределах приведенного свидетельства и его контекста: {claim_text}",
                    "visual_intent": "close with grounded takeaway",
                    "claim_refs": [claim_id],
                    "evidence_refs": [evidence_id],
                }
            )
            value = {"script_id": "script-local-1", "title": title, "units": units}
        elif '"style_bible":' in prompt:
            value = {
                "spec_id": "spec-local-1", "title": "Evidence-grounded short", "objective": "Create a concise evidence-grounded short",
                "audience": "general audience", "format": "short_video", "tone": "clear",
                "structure": ["hook", "context", "claim", "conclusion"], "constraints": ["use only supplied knowledge"],
                "claim_refs": [claim], "evidence_refs": [evidence],
                "style_bible": {"visual_style": "documentary", "palette": "natural", "lighting": "soft", "subject_continuity": "consistent", "negative_constraints": "no unsupported details", "voice": "calm", "pace": "measured", "music": "subtle"}
            }
        else:
            value = {"result": "local development output"}
        digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16]
        return ExternalCallResult(integration_id="local-text", status_code=200, response_id=f"local-{digest}", payload={"text": json.dumps(value, ensure_ascii=False)})

    @staticmethod
    def response_text(result: ExternalCallResult) -> str:
        payload = result.payload
        if not isinstance(payload, dict):
            raise ValueError("local provider payload must be an object")
        text = payload.get("text")
        if not isinstance(text, str) or not text.strip():
            raise ValueError("local provider contains no text output")
        return text
