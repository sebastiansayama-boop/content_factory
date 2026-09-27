from __future__ import annotations

import hashlib
import json

from .integrations import ExternalCallResult


class LocalResearchAdapter:
    """Deterministic fixture for deployment smoke tests; not live-web research."""

    def research(self, prompt: str) -> ExternalCallResult:
        if not prompt.strip():
            raise ValueError("research prompt must not be empty")
        digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16]
        brief = prompt.split("USER BRIEF:", 1)[-1].strip()
        if "Research the user's brief" in prompt:
            body = {
                "topic": brief,
                "summary": f"Development fixture for: {brief}",
                "claims": [{
                    "id": "claim-local-1",
                    "text": f"Development fixture claim for {brief}.",
                    "confidence": "low",
                    "source_ids": ["source-local-1"],
                    "evidence_ids": ["evidence-local-1"],
                    "scope": "local smoke test only",
                    "known_unknowns": ["Not live-web research."],
                }],
                "sources": [{
                    "id": "source-local-1",
                    "title": "Local development fixture",
                    "url": "https://example.invalid/content-factory/local",
                }],
                "evidence": [{
                    "id": "evidence-local-1",
                    "source_id": "source-local-1",
                    "excerpt": f"Fixture evidence for {brief}.",
                    "locator": "fixture",
                    "provenance": "local-research",
                }],
                "editorial_angles": ["Development fixture"],
            }
        else:
            body = {
                "title": brief,
                "content": f"Development fixture content for {brief}.",
                "claim_refs": ["claim-local-1"],
                "source_refs": ["source-local-1"],
            }
        return ExternalCallResult(
            integration_id="local-research",
            status_code=200,
            response_id=f"local-{digest}",
            payload={"output_text": json.dumps(body, ensure_ascii=False)},
        )

    @staticmethod
    def text(result: ExternalCallResult) -> str:
        payload = result.payload
        if not isinstance(payload, dict) or not isinstance(payload.get("output_text"), str):
            raise ValueError("local research response contains no text output")
        return payload["output_text"]

    @staticmethod
    def sources(result: ExternalCallResult) -> list[dict[str, str]]:
        return []
