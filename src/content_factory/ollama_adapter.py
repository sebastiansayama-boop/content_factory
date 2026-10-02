from __future__ import annotations

from dataclasses import dataclass
import hashlib
import os
from typing import Any

from .integrations import ExternalCallResult, HttpJsonAdapter, IntegrationConfig

@dataclass(frozen=True)
class OllamaConfig:
    model: str = "qwen3:4b"
    endpoint: str = "http://localhost:11434/api/generate"
    timeout: float = 120.0

    @classmethod
    def from_env(cls) -> "OllamaConfig":
        return cls(
            model=os.environ.get("OLLAMA_MODEL", cls.model).strip() or cls.model,
            endpoint=os.environ.get("OLLAMA_ENDPOINT", cls.endpoint).strip() or cls.endpoint,
            timeout=float(os.environ.get("OLLAMA_TIMEOUT", str(cls.timeout))),
        )

class OllamaAdapter:
    """Local Ollama implementation of the minimal LLMProvider boundary."""

    def __init__(self, config: OllamaConfig | None = None) -> None:
        self.config = config or OllamaConfig.from_env()
        self._http = HttpJsonAdapter(IntegrationConfig(integration_id="ollama.generate", endpoint=self.config.endpoint, timeout=self.config.timeout))

    def generate(self, prompt: str) -> ExternalCallResult:
        if not prompt.strip():
            raise ValueError("prompt must not be empty")
        result = self._http.call({"model": self.config.model, "prompt": prompt, "stream": False, "format": "json"})
        if result.response_id:
            return result
        digest = hashlib.sha256(
            f"{self.config.model}\n{prompt}\n{result.payload}".encode("utf-8")
        ).hexdigest()[:16]
        return ExternalCallResult(
            integration_id=result.integration_id,
            status_code=result.status_code,
            response_id=f"ollama-{digest}",
            payload=result.payload,
        )

    @staticmethod
    def response_text(result: ExternalCallResult) -> str:
        body: Any = result.payload
        if not isinstance(body, dict):
            raise ValueError("Ollama response payload must be an object")
        response = body.get("response")
        if isinstance(response, str) and response.strip():
            return response.strip()
        raise ValueError("Ollama response contains no text output")
