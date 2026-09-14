from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .integrations import ExternalCallResult, HttpJsonAdapter, IntegrationConfig


@dataclass(frozen=True)
class GeminiConfig:
    model: str = "gemini-3.5-flash-lite"
    endpoint: str = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
    secret_env: str = "GEMINI_API_KEY"


class GeminiOpenAICompatibleAdapter:
    """Provider adapter for Gemini's OpenAI-compatible Chat Completions API."""

    def __init__(self, config: GeminiConfig | None = None) -> None:
        self.config = config or GeminiConfig()
        self._http = HttpJsonAdapter(
            IntegrationConfig(
                integration_id="gemini.chat.completions",
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
                "messages": [
                    {"role": "user", "content": prompt},
                ],
            }
        )

    @staticmethod
    def response_text(result: ExternalCallResult) -> str:
        body: Any = result.payload
        if not isinstance(body, dict):
            raise ValueError("Gemini response payload must be an object")
        choices = body.get("choices", [])
        for choice in choices:
            if not isinstance(choice, dict):
                continue
            message = choice.get("message")
            if not isinstance(message, dict):
                continue
            content = message.get("content")
            if isinstance(content, str) and content.strip():
                return content.strip()
        raise ValueError("Gemini response contains no text output")
