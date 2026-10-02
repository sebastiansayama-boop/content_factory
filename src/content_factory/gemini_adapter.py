from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Any

from .integrations import ExternalCallResult, HttpJsonAdapter, IntegrationConfig


@dataclass(frozen=True)
class GeminiConfig:
    model: str = "gemini-3.5-flash-lite"
    endpoint: str = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
    secret_env: str = "GEMINI_API_KEY"
    research_model: str = "gemini-3.8-flash"

    @classmethod
    def from_env(cls) -> "GeminiConfig":
        return cls(
            model=os.environ.get("GEMINI_MODEL", cls.model).strip() or cls.model,
            endpoint=os.environ.get("GEMINI_ENDPOINT", cls.endpoint).strip() or cls.endpoint,
            secret_env=os.environ.get("GEMINI_API_KEY_ENV", cls.secret_env).strip() or cls.secret_env,
            research_model=os.environ.get("GEMINI_RESEARCH_MODEL", cls.research_model).strip() or cls.research_model,
        )


class GeminiOpenAICompatibleAdapter:
    """Provider adapter for Gemini's OpenAI-compatible Chat Completions API."""

    def __init__(self, config: GeminiConfig | None = None) -> None:
        self.config = config or GeminiConfig.from_env()
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
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "content_factory_output",
                        "strict": True,
                        "schema": {
                            "type": "object",
                            "additionalProperties": True,
                        },
                    },
                },
            }
        )

    def generate_multimodal(
        self,
        prompt: str,
        images: list[tuple[str, bytes, str]],
    ) -> ExternalCallResult:
        if not prompt.strip():
            raise ValueError("prompt must not be empty")
        if not images:
            raise ValueError("at least one image is required")
        content: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
        import base64
        for candidate_id, image_bytes, mime_type in images:
            if not candidate_id.strip():
                raise ValueError("candidate id must not be empty")
            if not image_bytes:
                raise ValueError(f"image bytes missing for candidate {candidate_id}")
            encoded = base64.b64encode(image_bytes).decode("ascii")
            content.append(
                {
                    "type": "text",
                    "text": f"Candidate ID: {candidate_id}",
                }
            )
            content.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{encoded}",
                    },
                }
            )
        return self._http.call(
            {
                "model": os.environ.get("GEMINI_VISION_MODEL", self.config.research_model).strip()
                or self.config.research_model,
                "messages": [
                    {"role": "user", "content": content},
                ],
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "visual_relevance_output",
                        "strict": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "candidates": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "additionalProperties": True,
                                    },
                                },
                            },
                            "required": ["candidates"],
                            "additionalProperties": False,
                        },
                    },
                },
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
