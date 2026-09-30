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
        elif '"editorial_points":' in prompt:
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
            value = {
                "script_id": "script-local-1", "title": "Evidence-grounded short",
                "units": [
                    {"unit_id": "unit-1", "kind": "hook", "text": "Here is what the evidence tells us.", "visual_intent": "establish topic", "claim_refs": [claim], "evidence_refs": [evidence]},
                    {"unit_id": "unit-2", "kind": "narration", "text": "We examine the supplied claim and its supporting evidence.", "visual_intent": "show evidence", "claim_refs": [claim], "evidence_refs": [evidence]},
                    {"unit_id": "unit-3", "kind": "narration", "text": "The story stays within the supplied evidence and its stated limits.", "visual_intent": "show context", "claim_refs": [claim], "evidence_refs": [evidence]},
                    {"unit_id": "unit-4", "kind": "cta", "text": "Follow for more evidence-grounded stories.", "visual_intent": "close", "claim_refs": [claim], "evidence_refs": [evidence]},
                ]
            }
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
