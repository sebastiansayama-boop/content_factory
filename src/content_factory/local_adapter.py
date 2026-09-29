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
        if '"research_questions":' in prompt:
            formats_match = re.search(r"Requested formats:\s*(\[[^\n]*\])", prompt)
            try:
                requested_formats = json.loads(formats_match.group(1)) if formats_match else ["article"]
            except json.JSONDecodeError:
                requested_formats = ["article"]
            value = {
                "objective": "Turn the user brief into an evidence-grounded content plan",
                "research_questions": ["What evidence is needed to answer the user's brief?"],
                "source_requirements": ["reliable primary or authoritative sources relevant to the brief"],
                "deliverables": [{"format": str(fmt), "purpose": "provide the requested content"} for fmt in requested_formats],
                "editorial_constraints": [],
                "quality_checks": ["all factual claims must be supported by accepted evidence"],
            }
        elif '"status": "PASS | REVISE | FAIL"' in prompt:
            claim_ids = re.findall(r"kc-[A-Za-z0-9_-]+", prompt)
            value = {
                "status": "PASS",
                "issues": [],
                "required_changes": [],
                "checked_claims": list(dict.fromkeys(claim_ids)) or ["kc-local"],
                "confidence": 0.9,
            }
        elif '"ideas":' in prompt:
            value = {
                "ideas": [
                    {"idea_id": "idea-local-1", "title": "Evidence-grounded story", "angle": "Explain the supplied evidence clearly", "audience": "general audience", "purpose": "inform", "formats": ["short_video"], "claim_refs": [claim], "evidence_refs": [evidence]},
                    {"idea_id": "idea-local-2", "title": "What the evidence shows", "angle": "Turn the supplied evidence into a concise narrative", "audience": "general audience", "purpose": "educate", "formats": ["short_video"], "claim_refs": [claim], "evidence_refs": [evidence]},
                    {"idea_id": "idea-local-3", "title": "One claim, one story", "angle": "Build a focused content piece around the supplied claim", "audience": "general audience", "purpose": "inform", "formats": ["short_video"], "claim_refs": [claim], "evidence_refs": [evidence]},
                ]
            }
        elif '"units":' in prompt:
            # Script provenance must come from the ContentSpec, not from the
            # first identifier encountered anywhere in the prompt. The prompt
            # also contains metadata and accepted knowledge.
            spec_match = re.search(
                r'CONTENT SPEC:\s*(\{.*?\})\s*ACCEPTED KNOWLEDGE:',
                prompt,
                flags=re.DOTALL,
            )
            spec_value = {}
            if spec_match:
                try:
                    spec_value = json.loads(spec_match.group(1))
                except json.JSONDecodeError:
                    spec_value = {}
            spec_claims = [
                str(value) for value in (spec_value.get("claim_refs") or [])
                if isinstance(value, str) and value
            ]
            spec_evidence = [
                str(value) for value in (spec_value.get("evidence_refs") or [])
                if isinstance(value, str) and value
            ]

            matches = re.findall(
                r'"claim_id"\s*:\s*"([^"]+)"\s*,\s*"text"\s*:\s*"((?:\\.|[^"\\])*)"',
                prompt,
            )
            claim_rows_by_id = {}
            for claim_id, claim_text in matches:
                try:
                    claim_rows_by_id[claim_id] = json.loads(f'"{claim_text}"')
                except json.JSONDecodeError:
                    claim_rows_by_id[claim_id] = claim_text

            claim_rows = [
                (claim_id, claim_rows_by_id[claim_id])
                for claim_id in spec_claims
                if claim_id in claim_rows_by_id
            ]
            if not claim_rows:
                raise ValueError(
                    "script generation received no claim text matching the ContentSpec claim_refs"
                )
            evidence_id = spec_evidence[0] if spec_evidence else evidence
            units = [{
                "unit_id": "unit-1",
                "kind": "hook",
                "text": f"What does the evidence show? {claim_rows[0][1]}",
                "visual_intent": "establish the topic and central claim",
                "claim_refs": [claim_rows[0][0]],
                "evidence_refs": [evidence_id],
            }]
            for index, (claim_id, claim_text) in enumerate(claim_rows[:3], start=2):
                units.append({
                    "unit_id": f"unit-{index}",
                    "kind": "narration",
                    "text": claim_text,
                    "visual_intent": "show the evidence behind the claim",
                    "claim_refs": [claim_id],
                    "evidence_refs": [evidence_id],
                })
            units.append({
                "unit_id": f"unit-{len(units)+1}",
                "kind": "cta",
                "text": "The evidence also defines what remains uncertain.",
                "visual_intent": "close with evidence boundary",
                "claim_refs": [claim_rows[0][0]],
                "evidence_refs": [evidence_id],
            })
            value = {"script_id": "script-local-grounded", "title": "Evidence-grounded story", "units": units}
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
