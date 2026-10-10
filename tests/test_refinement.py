from __future__ import annotations

import json

from content_factory.refinement import BreadthDepthRefiner


def test_breadth_depth_refiner_runs_candidates_refinements_and_synthesis() -> None:
    calls: list[str] = []

    def generate(prompt: str) -> str:
        calls.append(prompt)
        if "Synthesize the strongest" in prompt:
            return json.dumps({"content": "final", "title": "Final", "claim_refs": ["claim-1"], "source_refs": ["source-1"]})
        if "Critique and repair" in prompt:
            return json.dumps({"content": "repaired", "title": "Repaired", "claim_refs": ["claim-1"], "source_refs": ["source-1"], "critique": "repair"})
        return json.dumps({"content": "candidate", "title": "Candidate", "claim_refs": ["claim-1"], "source_refs": ["source-1"]})

    result = BreadthDepthRefiner(generate, breadth=3, depth=2).run(
        fmt="article", topic="Test", summary="Summary",
        claims="- claim-1: supported fact",
        sources="- source-1: Source",
    )

    assert len(result.candidates) == 3
    assert len(result.refinements) == 6
    assert result.content["content"] == "final"
    assert len(calls) == 10
