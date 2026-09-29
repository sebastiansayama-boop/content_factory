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


class GeminiResearchError(ValueError):
    """Structured Gemini provider failure suitable for deterministic fallback."""

    def __init__(self, message: str, *, http_status: int | None = None, kind: str = "provider_error") -> None:
        super().__init__(message)
        self.http_status = http_status
        self.kind = kind


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
            kind = "provider_error"
            try:
                error_body = json.loads(raw) if raw else {}
            except json.JSONDecodeError:
                error_body = {}
            error = error_body.get("error") if isinstance(error_body, dict) else None
            status_name = error.get("status") if isinstance(error, dict) else None
            provider_code = error.get("code") if isinstance(error, dict) else None
            message = error.get("message") if isinstance(error, dict) else None
            if exc.code == 429:
                resource_exhausted = str(status_name).upper() == "RESOURCE_EXHAUSTED"
                message_lower = str(message or raw).lower()
                quota_markers = ("quota", "exceeded your current", "resource_exhausted")
                kind = "quota_exhausted" if resource_exhausted or any(marker in message_lower for marker in quota_markers) else "rate_limited"
            details = f"Gemini research provider returned HTTP {exc.code}"
            if status_name:
                details += f" ({status_name})"
            if provider_code and str(provider_code) != str(exc.code):
                details += f" code={provider_code}"
            if message:
                details += f": {message}"
            elif raw:
                details += f": {raw[:1000]}"
            raise GeminiResearchError(details, http_status=exc.code, kind=kind) from exc
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
    def normalize_research(
        research: dict[str, Any],
        grounded_sources: list[dict[str, str]],
    ) -> dict[str, Any]:
        """Normalize model JSON against URLs actually returned by Google Search grounding."""
        allowed = {
            source["url"]: source
            for source in grounded_sources
            if isinstance(source, dict) and isinstance(source.get("url"), str)
        }
        raw_claims = research.get("claims")
        if not isinstance(raw_claims, list) or not raw_claims:
            raise ValueError("Gemini grounded research must contain claims")

        normalized_sources: list[dict[str, str]] = []
        source_ids: dict[str, str] = {}
        evidence_items: list[dict[str, str]] = []
        normalized_claims: list[dict[str, Any]] = []

        for index, claim in enumerate(raw_claims, start=1):
            if not isinstance(claim, dict):
                continue
            urls = claim.get("source_urls", [])
            if not isinstance(urls, list):
                raise ValueError(f"Gemini claim {claim.get('id', index)} source_urls must be an array")
            valid_urls = [url for url in urls if isinstance(url, str) and url in allowed]
            if not valid_urls:
                raise ValueError(
                    f"Gemini claim {claim.get('id', index)} has no source URL returned by grounding"
                )

            normalized_source_refs: list[str] = []
            for url in valid_urls:
                if url not in source_ids:
                    source_ids[url] = f"source-{len(source_ids) + 1}"
                    normalized_sources.append(
                        {
                            "id": source_ids[url],
                            "title": allowed[url]["title"],
                            "url": url,
                        }
                    )
                normalized_source_refs.append(source_ids[url])

            raw_evidence = claim.get("evidence", [])
            if not isinstance(raw_evidence, list):
                raw_evidence = []
            claim_evidence_refs: list[str] = []
            for item in raw_evidence:
                if not isinstance(item, dict):
                    continue
                url = item.get("source_url")
                excerpt = str(item.get("excerpt") or "").strip()
                if url not in allowed or not excerpt or url not in valid_urls:
                    continue
                evidence_id = f"evidence-{len(evidence_items) + 1}"
                evidence_items.append(
                    {
                        "id": evidence_id,
                        "source_id": source_ids[url],
                        "excerpt": excerpt[:1200],
                        "locator": "Gemini Google Search grounding",
                        "provenance": "gemini-google-search-grounding",
                    }
                )
                claim_evidence_refs.append(evidence_id)

            if not claim_evidence_refs:
                raise ValueError(
                    f"Gemini claim {claim.get('id', index)} has no valid evidence excerpt"
                )

            normalized_claims.append(
                {
                    "id": str(claim.get("id") or f"claim-{index}"),
                    "text": str(claim.get("text") or "").strip(),
                    "confidence": str(claim.get("confidence") or "medium").lower(),
                    "source_ids": normalized_source_refs,
                    "evidence_ids": claim_evidence_refs,
                    "scope": str(claim.get("scope") or "grounded web research").strip(),
                    "known_unknowns": (
                        claim.get("known_unknowns", [])
                        if isinstance(claim.get("known_unknowns", []), list)
                        else []
                    ),
                }
            )

        if not normalized_claims:
            raise ValueError("Gemini grounded research produced no usable claims")

        normalized = dict(research)
        normalized["claims"] = normalized_claims
        normalized["sources"] = normalized_sources
        normalized["evidence"] = evidence_items
        return normalized

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
