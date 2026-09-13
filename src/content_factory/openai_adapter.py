from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .integrations import ExternalCallResult, HttpJsonAdapter, IntegrationConfig


@dataclass(frozen=True)
class OpenAIResponsesConfig:
    model: str = "gpt-5.6-luna"
    endpoint: str = "https://api.openai.com/v1/responses"
    secret_env: str = "OPENAI_API_KEY"


class OpenAIResponsesAdapter:
    """Minimal real-provider adapter for OpenAI's Responses API."""

    def __init__(self, config: OpenAIResponsesConfig | None = None) -> None:
        self.config = config or OpenAIResponsesConfig()
        self._http = HttpJsonAdapter(
            IntegrationConfig(
                integration_id="openai.responses",
                endpoint=self.config.endpoint,
                secret_env=self.config.secret_env,
            )
        )

    def generate(self, prompt: str) -> ExternalCallResult:
        if not prompt.strip():
            raise ValueError("prompt must not be empty")
        return self._http.call(
            {
                "model": self.config.model,
                "input": prompt,
            }
        )

    @staticmethod
    def response_text(result: ExternalCallResult) -> str:
        body: Any = result.payload
        if not isinstance(body, dict):
            raise ValueError("OpenAI response payload must be an object")
        output = body.get("output", [])
        chunks: list[str] = []
        for item in output:
            if not isinstance(item, dict):
                continue
            for content in item.get("content", []):
                if not isinstance(content, dict):
                    continue
                text = content.get("text")
                if isinstance(text, str):
                    chunks.append(text)
        if not chunks:
            raise ValueError("OpenAI response contains no text output")
        return "".join(chunks)
