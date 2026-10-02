from __future__ import annotations

import base64
import json
import re
from dataclasses import dataclass
from typing import Any

from .openai_adapter import OpenAIResponsesAdapter
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

class OpenAIVisualRelevanceVerifier:
    def __init__(self, adapter: OpenAIResponsesAdapter | None = None) -> None:
        self.adapter = adapter or OpenAIResponsesAdapter()

    def verify_candidates(
        self,
        query: str,
        candidates: list[OpenverseImage],
        images: list[tuple[str, bytes, str]],
    ) -> list[VisualVerification]:
        if not query.strip():
            raise ValueError("visual query must not be empty")
        by_id = {candidate_id: (data, mime) for candidate_id, data, mime in images}
        usable = [c for c in candidates if c.id in by_id]
        if not usable:
            return []

        prompt = (
            "You are a strict visual relevance verifier.\n"
            f"Visual intent: {query.strip()}\n"
            "Judge ONLY visible pixels. Ignore candidate titles, filenames, URLs and metadata.\n"
            "Identify the primary subject and verify it is visibly present. Reject substitutions.\n"
            "An image of a cruise ship on the Nile is NOT a match for Nile crocodile.\n"
            "ACCEPT only when the requested primary subject is visibly present and no contradictory subject is present.\n"
            'Return ONLY JSON: {"candidates":[{"candidate_id":"string","decision":"ACCEPT|REJECT",' 
            '"score":0.0,"subject_present":true,"scene_present":true,"forbidden_present":false,',
            '"image_type_match":true,"reason":"brief factual explanation"}]}'
        )
        content: list[dict[str, Any]] = [{"type": "input_text", "text": prompt}]

        for candidate in usable:
            image_bytes, mime_type = by_id[candidate.id]
            if not image_bytes:
                raise ValueError(f"image bytes missing for candidate {candidate.id}")
            encoded = base64.b64encode(image_bytes).decode("ascii")
            content.append({"type": "input_text", "text": f"Candidate ID: {candidate.id}"})
            content.append({
                "type": "input_image",
                "image_url": f"data:{mime_type};base64,{encoded}",
                "detail": "auto",
            })

        result = self.adapter.generate_multimodal(content)
        if result.status_code < 200 or result.status_code >= 300:
            raise ValueError(f"OpenAI visual verifier returned HTTP {result.status_code}")
        raw = self.adapter.response_text(result)
        payload = self._parse_json(raw)
        rows = payload.get("candidates")
        if not isinstance(rows, list):
            raise ValueError("OpenAI visual verifier response must contain candidates")

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
            out.append(VisualVerification(
                candidate_id,
                decision if decision in {"ACCEPT", "REJECT"} else "REJECT",
                score,
                bool(row.get("subject_present")),
                bool(row.get("scene_present")),
                bool(row.get("forbidden_present")),
                bool(row.get("image_type_match")),
                str(row.get("reason") or "").strip(),
            ))
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
                raise ValueError("OpenAI visual verifier returned invalid JSON")
            value = json.loads(cleaned[start : end + 1])
        if not isinstance(value, dict):
            raise ValueError("OpenAI visual verifier response must be an object")
        return value
