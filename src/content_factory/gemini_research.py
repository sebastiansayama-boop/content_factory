from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from .integrations import ExternalCallResult


@dataclass(frozen=True)
class GeminiResearchConfig:
    model: str = "gemini-3.5-flash-lite"
    endpoint_template: str = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "{model}:generateContent"
    )
    secret_env: str = "GEMINI_API_KEY"


class GeminiGoogleSearchResearchAdapter:
    """Gemini research adapter using Google Search grounding."""

    def __init__(self, config: GeminiResearchConfig | None = None) -> None:
        self.config = config or GeminiResearchConfig()
        key = os.environ.get(self.config.secret_env, "").strip()
        if not key:
            raise ValueError(f"missing integration secret: {self.config.secret_env}")
        self._key = key

    def research(self, prompt: str) -> ExternalCallResult:
        if not prompt.strip():
            raise ValueError("research prompt must not be empty")

        endpoint = self.config.endpoint_template.format(model=self.config.model)
        body = {
            "contents": [
                {
                    "parts": [{"text": prompt}],
                }
            ],
            "tools": [{"google_search": {}}],
        }
        request = urllib.request.Request(
            endpoint,
            data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "x-goog-api-key": self._key,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=60.0) as response:
                raw = response.read().decode("utf-8")
                payload = json.loads(raw) if raw else {}
                status = int(response.status)
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            raise ValueError(
                f"Gemini research provider returned HTTP {exc.code}: {raw[:1000]}"
            ) from exc
        except urllib.error.URLError as exc:
            raise ValueError(
                f"Gemini research provider connection failed: {exc.reason}"
            ) from exc
        if not isinstance(payload, dict):
            raise ValueError("Gemini research provider returned a non-object response")
        return ExternalCallResult(
            integration_id="gemini.google-search-research",
            status_code=status,
            response_id=str(payload.get("responseId") or "") or None,
            payload=payload,
        )

    @staticmethod
    def _text_and_grounding(result: ExternalCallResult) -> tuple[str, list[dict[str, str]], list[str]]:
        body = result.payload
        if not isinstance(body, dict):
            raise ValueError("Gemini response payload must be an object")

        candidates = body.get("candidates")
        if not isinstance(candidates, list) or not candidates:
            raise ValueError("Gemini response contains no candidates")

        candidate = candidates[0]
        if not isinstance(candidate, dict):
            raise ValueError("Gemini candidate is invalid")

        parts = ((candidate.get("content") or {}).get("parts") or [])
        chunks: list[str] = []
        for part in parts:
            if isinstance(part, dict) and isinstance(part.get("text"), str):
                chunks.append(part["text"])
        text = "".join(chunks).strip()
        if not text:
            raise ValueError("Gemini response contains no text output")

        metadata = candidate.get("groundingMetadata") or {}
        grounding_chunks = metadata.get("groundingChunks") or []
        sources: list[dict[str, str]] = []
        seen_urls: set[str] = set()
        for item in grounding_chunks:
            if not isinstance(item, dict):
                continue
            web = item.get("web")
            if not isinstance(web, dict):
                continue
            uri = web.get("uri")
            title = web.get("title")
            if not isinstance(uri, str) or not uri.startswith(("http://", "https://")):
                continue
            if uri in seen_urls:
                continue
            sources.append(
                {
                    "url": uri,
                    "title": title.strip() if isinstance(title, str) and title.strip() else uri,
                }
            )
            seen_urls.add(uri)

        queries = metadata.get("webSearchQueries")
        search_queries = [q for q in queries if isinstance(q, str) and q.strip()] if isinstance(queries, list) else []
        return text, sources, search_queries

    @staticmethod
    def text(result: ExternalCallResult) -> str:
        text, _, _ = GeminiGoogleSearchResearchAdapter._text_and_grounding(result)
        return text

    @staticmethod
    def sources(result: ExternalCallResult) -> list[dict[str, str]]:
        _, sources, _ = GeminiGoogleSearchResearchAdapter._text_and_grounding(result)
        return sources

    @staticmethod
    def search_queries(result: ExternalCallResult) -> list[str]:
        _, _, queries = GeminiGoogleSearchResearchAdapter._text_and_grounding(result)
        return queries
