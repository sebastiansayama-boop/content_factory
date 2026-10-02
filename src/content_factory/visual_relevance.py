from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from .gemini_adapter import GeminiOpenAICompatibleAdapter
from .openverse_adapter import OpenverseImage

@dataclass(frozen=True)
class VisualVerification:
    candidate_id: str
    decision: str
    score: float
    subject_present: bool
    scene_present: bool
    forbidden_present: bool
    image_type_match: bool
    reason: str

    @property
    def accepted(self) -> bool:
        return self.decision == "ACCEPT" and self.subject_present and not self.forbidden_present

class GeminiVisualRelevanceVerifier:
    def __init__(self, adapter: GeminiOpenAICompatibleAdapter | None = None) -> None:
        self.adapter = adapter or GeminiOpenAICompatibleAdapter()

    def verify_candidates(self, query: str, candidates: list[OpenverseImage], images: list[tuple[str, bytes, str]]) -> list[VisualVerification]:
        if not query.strip():
            raise ValueError("visual query must not be empty")
        by_id = {candidate_id: (data, mime) for candidate_id, data, mime in images}
        usable = [c for c in candidates if c.id in by_id]
        if not usable:
            return []
        prompt = f'''You are a strict visual relevance verifier.
Visual intent: {query.strip()}
Judge ONLY visible pixels. Ignore candidate titles, filenames, URLs and metadata.
Identify the primary subject and verify it is visibly present. Reject substitutions.
An image of a cruise ship on the Nile is NOT a match for Nile crocodile.
Return JSON: {{"candidates":[{{"candidate_id":"string","decision":"ACCEPT|REJECT","score":0.0,"subject_present":true,"scene_present":true,"forbidden_present":false,"image_type_match":true,"reason":"brief factual explanation"}}]}}
ACCEPT only when the requested primary subject is visibly present and no contradictory subject is present.'''
        parts = [(c.id, by_id[c.id][0], by_id[c.id][1]) for c in usable]
        result = self.adapter.generate_multimodal(prompt, parts)
        raw = GeminiOpenAICompatibleAdapter.response_text(result)
        payload = self._parse_json(raw)
        rows = payload.get("candidates")
        if not isinstance(rows, list):
            raise ValueError("Gemini visual verifier response must contain candidates")
        allowed = {c.id for c in usable}
        out: list[VisualVerification] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            candidate_id = str(row.get("candidate_id") or "").strip()
            if candidate_id not in allowed:
                continue
            try:
                score = max(0.0, min(1.0, float(row.get("score", 0.0))))
            except (TypeError, ValueError):
                score = 0.0
            decision = str(row.get("decision") or "REJECT").upper()
            out.append(VisualVerification(candidate_id, decision if decision in {"ACCEPT", "REJECT"} else "REJECT", score, bool(row.get("subject_present")), bool(row.get("scene_present")), bool(row.get("forbidden_present")), bool(row.get("image_type_match")), str(row.get("reason") or "").strip()))
        return out

    @staticmethod
    def _parse_json(text: str) -> dict[str, Any]:
        cleaned = re.sub(r"^```json\s*", "", text.strip(), flags=re.I)
        cleaned = re.sub(r"^```\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        try:
            value = json.loads(cleaned)
        except json.JSONDecodeError:
            start, end = cleaned.find("{"), cleaned.rfind("}")
            if start < 0 or end <= start:
                raise ValueError("Gemini visual verifier returned invalid JSON")
            value = json.loads(cleaned[start:end + 1])
        if not isinstance(value, dict):
            raise ValueError("Gemini visual verifier response must be an object")
        return value