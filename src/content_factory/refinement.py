from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class RefinementResult:
    content: dict[str, Any]
    candidates: tuple[dict[str, Any], ...]
    refinements: tuple[dict[str, Any], ...]
    breadth: int
    depth: int


def _parse_json(text: str) -> dict[str, Any]:
    value = json.loads(text.strip())
    if not isinstance(value, dict):
        raise ValueError("refinement provider response must be a JSON object")
    return value


class BreadthDepthRefiner:
    """Breadth/depth refinement adapted for open-ended content."""

    def __init__(self, generate: Callable[[str], str], *, breadth: int = 3, depth: int = 1) -> None:
        if breadth < 1:
            raise ValueError("breadth must be >= 1")
        if depth < 1:
            raise ValueError("depth must be >= 1")
        self.generate = generate
        self.breadth = breadth
        self.depth = depth

    def run(self, *, fmt: str, topic: str, summary: str, claims: str, sources: str) -> RefinementResult:
        candidates: list[dict[str, Any]] = []
        refinements: list[dict[str, Any]] = []
        for index in range(1, self.breadth + 1):
            prompt = f"""Create one {fmt} for this researched topic.
You are candidate {index} of {self.breadth}. Use a distinct editorial approach.
Return ONLY JSON: {{"content":"complete usable content","title":"string","claim_refs":["claim-id"],"source_refs":["source-id"]}}
Do not add factual claims absent from the research.
Topic: {topic}
Summary: {summary}
Claims:
{claims}
Sources:
{sources}
"""
            candidate = _parse_json(self.generate(prompt))
            candidate["candidate_id"] = f"candidate-{index}"
            candidates.append(candidate)

        current = list(candidates)
        for round_no in range(1, self.depth + 1):
            next_round: list[dict[str, Any]] = []
            for candidate in current:
                prompt = f"""Critique and repair this {fmt} candidate against the supplied research.
Refinement round {round_no} of {self.depth}. Identify factual overreach, unsupported
claims, weak sourcing, contradictions, and editorial weaknesses. Return the corrected
complete artifact and concise critique as JSON:
{{"content":"corrected complete usable content","title":"string","claim_refs":["claim-id"],"source_refs":["source-id"],"critique":"string"}}
Do not invent facts, sources, or claim IDs.
Topic: {topic}
Summary: {summary}
Claims:
{claims}
Sources:
{sources}
Candidate:
{json.dumps(candidate, ensure_ascii=False)}
"""
                repaired = _parse_json(self.generate(prompt))
                repaired["candidate_id"] = candidate["candidate_id"]
                repaired["refinement_round"] = round_no
                next_round.append(repaired)
                refinements.append(repaired)
            current = next_round

        synthesis_prompt = f"""Synthesize the strongest final {fmt} from the refined candidates.
Use only claims and sources supplied in the research. Prefer factual precision,
clear provenance, and a coherent editorial line. If candidates disagree, use the
narrower supported formulation. Return ONLY JSON:
{{"content":"complete usable content","title":"string","claim_refs":["claim-id"],"source_refs":["source-id"]}}
Topic: {topic}
Summary: {summary}
Claims:
{claims}
Sources:
{sources}
Refined candidates:
{json.dumps(current, ensure_ascii=False)}
"""
        final = _parse_json(self.generate(synthesis_prompt))
        return RefinementResult(
            content=final,
            candidates=tuple(candidates),
            refinements=tuple(refinements),
            breadth=self.breadth,
            depth=self.depth,
        )
