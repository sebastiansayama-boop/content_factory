from __future__ import annotations

import json
from typing import Any

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