from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .integrations import ExternalCallResult, HttpJsonAdapter, IntegrationConfig
from .runtime import ExecutionResult, WorkItem


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

    def execute(self, work_item: WorkItem, execution_id: str) -> ExecutionResult:
        result = self.generate(work_item.requested_outcome)
        if result.status_code < 200 or result.status_code >= 300:
            raise RuntimeError(f"OpenAI execution failed with HTTP {result.status_code}")
        if not result.response_id:
            raise RuntimeError("OpenAI execution returned no response id")
        text = self.response_text(result)
        return ExecutionResult(
            execution_id=execution_id,
            capability_id="openai.responses.text_generation",
            output_revision_id=f"{result.response_id}:output",
            payload=text,
            evidence_refs=(f"provider:{result.response_id}",),
        )
