from __future__ import annotations

import hashlib

from .integrations import ExternalCallResult


class LocalTextAdapter:
    """Deterministic development provider used when no external LLM key is configured."""

    def generate(self, prompt: str) -> ExternalCallResult:
        if not prompt.strip():
            raise ValueError("prompt must not be empty")
        digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16]
        return ExternalCallResult(
            status_code=200,
            response_id=f"local-{digest}",
            payload={"text": "LOCAL_PROVIDER_PLACEHOLDER"},
        )

    @staticmethod
    def response_text(result: ExternalCallResult) -> str:
        payload = result.payload
        if not isinstance(payload, dict):
            raise ValueError("local provider payload must be an object")
        text = payload.get("text")
        if not isinstance(text, str) or not text.strip():
            raise ValueError("local provider contains no text output")
        return text
