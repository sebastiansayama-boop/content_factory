from __future__ import annotations

import ipaddress
import json
from typing import Any
from urllib.parse import urlparse

from .gemini_adapter import GeminiConfig

from .integrations import ExternalCallResult, HttpJsonAdapter, IntegrationConfig


class OpenAIWebResearchAdapter:
    def __init__(self, model: str = "gpt-5.5") -> None:
        self.model = model
        self._http = HttpJsonAdapter(IntegrationConfig(
            integration_id="openai.responses.web_search",
            endpoint="https://api.openai.com/v1/responses",
            secret_env="OPENAI_API_KEY",
        ))

    def research(self, prompt: str) -> ExternalCallResult:
        if not prompt.strip():
            raise ValueError("research prompt must not be empty")
        return self._http.call({"model": self.model, "tools": [{"type": "web_search"}], "include": ["web_search_call.action.sources"], "input": prompt})

    @staticmethod
    def text(result: ExternalCallResult) -> str:
        body: Any = result.payload
        if not isinstance(body, dict):
            raise ValueError("research response payload must be an object")
        chunks: list[str] = []
        for item in body.get("output", []):
            if not isinstance(item, dict) or item.get("type") != "message":
                continue
            for content in item.get("content", []):
                if isinstance(content, dict) and isinstance(content.get("text"), str):
                    chunks.append(content["text"])
        if not chunks:
            raise ValueError("research response contains no text output")
        return "".join(chunks)

    @staticmethod
    def sources(result: ExternalCallResult) -> list[dict[str, str]]:
        body: Any = result.payload
        if not isinstance(body, dict):
            return []
        found: list[dict[str, str]] = []
        seen: set[str] = set()
        for item in body.get("output", []):
            if not isinstance(item, dict) or item.get("type") != "web_search_call":
                continue
            action = item.get("action")
            if not isinstance(action, dict):
                continue
            for source in action.get("sources", []):
                if not isinstance(source, dict):
                    continue
                url = source.get("url")
                if isinstance(url, str) and url and url not in seen:
                    title = source.get("title")
                    found.append({"url": url, "title": title if isinstance(title, str) else ""})
                    seen.add(url)
        return found


class GeminiWebResearchAdapter:
    """Gemini research adapter using the native Gemini Interactions API."""

    def __init__(self, config: GeminiConfig | None = None) -> None:
        self.config = config or GeminiConfig.from_env()
        self.model = self.config.research_model
        self._http = HttpJsonAdapter(
            IntegrationConfig(
                integration_id="gemini.interactions.google_search",
                endpoint="https://generativelanguage.googleapis.com/v1beta/interactions",
                secret_env=self.config.secret_env,
                secret_header="x-goog-api-key",
                secret_prefix="",
            )
        )

    def research(self, prompt: str) -> ExternalCallResult:
        if not prompt.strip():
            raise ValueError("research prompt must not be empty")
        return self._http.call(
            {
                "model": self.model,
                "input": prompt,
                "tools": [{"type": "google_search"}],
            }
        )

    @staticmethod
    def text(result: ExternalCallResult) -> str:
        body: Any = result.payload
        if not isinstance(body, dict):
            raise ValueError("Gemini research response payload must be an object")

        output_text = body.get("output_text")
        if isinstance(output_text, str) and output_text.strip():
            return output_text.strip()

        chunks: list[str] = []
        for step in body.get("steps", []):
            if not isinstance(step, dict) or step.get("type") != "model_output":
                continue
            for content in step.get("content", []):
                if isinstance(content, dict) and isinstance(content.get("text"), str):
                    chunks.append(content["text"])
        if not chunks:
            raise ValueError("Gemini research response contains no text output")
        return "".join(chunks).strip()

    @staticmethod
    def sources(result: ExternalCallResult) -> list[dict[str, str]]:
        body: Any = result.payload
        if not isinstance(body, dict):
            return []

        found: list[dict[str, str]] = []
        seen: set[str] = set()
        for step in body.get("steps", []):
            if not isinstance(step, dict) or step.get("type") != "model_output":
                continue
            for content in step.get("content", []):
                if not isinstance(content, dict):
                    continue
                for annotation in content.get("annotations", []):
                    if not isinstance(annotation, dict):
                        continue
                    if annotation.get("type") != "url_citation":
                        continue
                    url = annotation.get("url") or annotation.get("uri")
                    if not isinstance(url, str) or not url or url in seen:
                        continue
                    title = annotation.get("title")
                    found.append({
                        "url": url,
                        "title": title if isinstance(title, str) else "",
                    })
                    seen.add(url)
        return found


def is_safe_source_url(url: str) -> bool:
    """Accept normal web URLs and reject obvious local/private targets."""
    value = str(url or "").strip()
    if not value:
        return False
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return False
    if parsed.username or parsed.password:
        return False
    hostname = parsed.hostname.rstrip(".").lower()
    if hostname == "localhost" or hostname.endswith(".local"):
        return False
    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        return True
    return not (
        address.is_private
        or address.is_loopback
        or address.is_link_local
        or address.is_reserved
        or address.is_multicast
    )


def parse_research_json(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        lines = lines[1:] if lines and lines[0].startswith("```") else lines
        lines = lines[:-1] if lines and lines[-1].strip() == "```" else lines
        cleaned = "\n".join(lines).strip()
    try:
        value = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start < 0 or end <= start:
            raise ValueError("research provider did not return valid JSON") from exc
        value = json.loads(cleaned[start:end + 1])
    if not isinstance(value, dict):
        raise ValueError("research result must be a JSON object")
    return value