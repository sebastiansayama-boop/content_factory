from __future__ import annotations

import json
import os
import re
import urllib.parse
import urllib.request
from html import unescape
from defusedxml import ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Protocol

from .gemini_adapter import GeminiConfig, GeminiOpenAICompatibleAdapter
from .integrations import ExternalCallResult


@dataclass(frozen=True)
class RetrievalItem:
    source_id: str
    provider: str
    external_id: str
    title: str
    url: str
    excerpt: str

    @property
    def evidence_id(self) -> str:
        return f"evidence:{self.source_id}"

    def as_context(self) -> str:
        return (
            f"SOURCE ID: {self.source_id}\n"
            f"PROVIDER: {self.provider}\n"
            f"TITLE: {self.title}\n"
            f"URL: {self.url}\n"
            f"EVIDENCE ID: {self.evidence_id}\n"
            f"EVIDENCE EXCERPT: {self.excerpt[:3000]}"
        )


@dataclass(frozen=True)
class RetrievalPacket:
    query: str
    items: tuple[RetrievalItem, ...]
    retrieved_at: str

    def as_context(self) -> str:
        return "\n\n".join(item.as_context() for item in self.items)

    def sources(self) -> list[dict[str, str]]:
        return [{"id": item.source_id, "title": item.title, "url": item.url} for item in self.items]


class Retriever(Protocol):
    def retrieve(self, query: str) -> RetrievalPacket:
        ...


class FreeWebRetriever:
    """API-key-free retrieval from Wikimedia, OpenAlex and Google News RSS.

    Retrieval is deliberately separate from model generation. The model never
    receives a search tool; it receives only this normalized source/evidence pack.
    """

    def __init__(
        self,
        *,
        opener=urllib.request.urlopen,
        wiki_limit: int = 1,
        openalex_limit: int = 2,
        news_limit: int = 3,
        timeout: float = 10.0,
    ) -> None:
        self._opener = opener
        self.wiki_limit = max(0, wiki_limit)
        self.openalex_limit = max(0, openalex_limit)
        self.news_limit = max(0, news_limit)
        self.timeout = timeout

    def _json_get(self, url: str) -> Any:
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": "content-factory-free-retrieval/1.0",
            },
        )
        with self._opener(request, timeout=self.timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    def _wikipedia(self, query: str) -> list[RetrievalItem]:
        if self.wiki_limit <= 0:
            return []
        params = urllib.parse.urlencode({
            "action": "opensearch",
            "search": query,
            "namespace": "0",
            "limit": str(self.wiki_limit),
            "format": "json",
        })
        search_payload = self._json_get(f"https://en.wikipedia.org/w/api.php?{params}")
        if not isinstance(search_payload, list) or len(search_payload) < 4:
            return []
        titles = search_payload[1]
        urls = search_payload[3]
        items: list[RetrievalItem] = []
        for title, url in zip(titles, urls):
            if not isinstance(title, str) or not title.strip() or not isinstance(url, str) or not url:
                continue
            detail_params = urllib.parse.urlencode({
                "action": "query",
                "prop": "extracts",
                "exintro": "1",
                "explaintext": "1",
                "redirects": "1",
                "titles": title,
                "format": "json",
                "formatversion": "2",
            })
            detail = self._json_get(f"https://en.wikipedia.org/w/api.php?{detail_params}")
            pages = detail.get("query", {}).get("pages", []) if isinstance(detail, dict) else []
            excerpt = ""
            if isinstance(pages, list) and pages and isinstance(pages[0], dict):
                excerpt = str(pages[0].get("extract") or "").strip()
            if not excerpt:
                continue
            source_key = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "page"
            items.append(RetrievalItem(
                source_id=f"source:wikipedia:{source_key}",
                provider="wikipedia",
                external_id=title,
                title=title,
                url=url,
                excerpt=excerpt,
            ))
        return items

    def _abstract_from_inverted_index(self, value: Any) -> str:
        if not isinstance(value, dict):
            return ""
        tokens: list[tuple[int, str]] = []
        for word, positions in value.items():
            if not isinstance(word, str) or not isinstance(positions, list):
                continue
            for position in positions:
                if isinstance(position, int):
                    tokens.append((position, word))
        return " ".join(word for _, word in sorted(tokens))

    def _google_news(self, query: str) -> list[RetrievalItem]:
        if self.news_limit <= 0:
            return []
        params = urllib.parse.urlencode({
            "q": query,
            "hl": "en-US",
            "gl": "US",
            "ceid": "US:en",
        })
        request = urllib.request.Request(
            f"https://news.google.com/rss/search?{params}",
            headers={
                "Accept": "application/rss+xml, application/xml, text/xml",
                "User-Agent": "content-factory-free-retrieval/1.0",
            },
        )
        with self._opener(request, timeout=self.timeout) as response:
            root = ET.fromstring(response.read())
        items: list[RetrievalItem] = []
        for entry in root.findall("./channel/item")[: self.news_limit]:
            title = (entry.findtext("title") or "").strip()
            url = (entry.findtext("link") or "").strip()
            description = unescape(entry.findtext("description") or "").strip()
            description = re.sub(r"<[^>]+>", " ", description)
            description = re.sub(r"\s+", " ", description).strip()
            if not title or not url or not description:
                continue
            external_id = url
            key = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "story"
            items.append(RetrievalItem(
                source_id=f"source:google-news:{key}",
                provider="google_news",
                external_id=external_id,
                title=title,
                url=url,
                excerpt=description,
            ))
        return items

    def _openalex(self, query: str) -> list[RetrievalItem]:
        if self.openalex_limit <= 0:
            return []
        params = urllib.parse.urlencode({
            "search": query,
            "per_page": str(self.openalex_limit),
        })
        payload = self._json_get(f"https://api.openalex.org/works?{params}")
        if not isinstance(payload, dict):
            return []
        results = payload.get("results")
        if not isinstance(results, list):
            return []
        items: list[RetrievalItem] = []
        for item in results[: self.openalex_limit]:
            if not isinstance(item, dict):
                continue
            external_id = str(item.get("id") or "").strip()
            if not external_id:
                continue
            title = str(item.get("display_name") or item.get("title") or "").strip()
            locator = str(item.get("doi") or external_id).strip()
            excerpt = self._abstract_from_inverted_index(item.get("abstract_inverted_index"))
            if not excerpt:
                excerpt = title
            if not excerpt:
                continue
            external_key = external_id.rsplit("/", 1)[-1]
            items.append(RetrievalItem(
                source_id=f"source:openalex:{external_key}",
                provider="openalex",
                external_id=external_id,
                title=title,
                url=locator,
                excerpt=excerpt,
            ))
        return items

    def retrieve(self, query: str) -> RetrievalPacket:
        normalized = str(query or "").strip()
        if not normalized:
            raise ValueError("retrieval query must not be empty")
        items: list[RetrievalItem] = []
        seen_urls: set[str] = set()
        failures: list[str] = []
        for name, retriever in (
            ("wikipedia", self._wikipedia),
            ("openalex", self._openalex),
            ("google_news", self._google_news),
        ):
            try:
                candidates = retriever(normalized)
            except Exception as exc:
                detail = str(exc).strip().replace("\n", " ")[:240]
                failures.append(f"{name}:{type(exc).__name__}:{detail}")
                candidates = []
            for item in candidates:
                if item.url in seen_urls:
                    continue
                seen_urls.add(item.url)
                items.append(item)
        if not items:
            detail = " | ".join(failures) if failures else "all sources returned empty results"
            raise RuntimeError(f"free retrieval returned no usable public sources ({detail})")
        return RetrievalPacket(
            query=normalized,
            items=tuple(items),
            retrieved_at=datetime.now(timezone.utc).isoformat(),
        )


class FreeWebGeminiAdapter:
    """Gemini generation backed by a separate API-key-free retrieval layer."""

    provider = "gemini_free_retrieval"

    def __init__(
        self,
        config: GeminiConfig | None = None,
        *,
        retriever: Retriever | None = None,
        gemini: GeminiOpenAICompatibleAdapter | None = None,
    ) -> None:
        self.config = config or GeminiConfig.from_env()
        self.retriever = retriever or FreeWebRetriever()
        self.gemini = gemini or GeminiOpenAICompatibleAdapter(self.config)
        self._packet: RetrievalPacket | None = None
        self._last_sources: list[dict[str, str]] = []

    def _brief_from_prompt(self, prompt: str) -> str:
        marker = "USER BRIEF:"
        if marker in prompt:
            return prompt.split(marker, 1)[1].strip()
        return ""

    def _research_prompt(self, prompt: str, packet: RetrievalPacket) -> str:
        return (
            prompt.replace(
                "Research the user's brief using live web search.",
                "Use the supplied retrieval pack as the complete web-retrieval result. "
                "Do not perform or claim additional web search."
            )
            + "\n\nSUPPLIED RETRIEVAL PACK:\n"
            + packet.as_context()
            + "\n\nRETRIEVAL RULES:\n"
            "Use only the supplied SOURCE IDs and EVIDENCE IDs. "
            "Do not invent URLs, citations, source IDs, evidence IDs, or evidence excerpts. "
            "Every factual claim must reference the exact source/evidence IDs that support it."
        )

    def _production_prompt(self, prompt: str) -> str:
        if self._packet is None:
            raise RuntimeError("production requested before retrieval-backed research")
        return (
            prompt
            + "\n\nRETRIEVAL PACK USED FOR THIS RUN:\n"
            + self._packet.as_context()
            + "\n\nPROVENANCE RULE: Do not introduce factual claims that are absent from the supplied retrieval pack."
        )

    def research(self, prompt: str) -> ExternalCallResult:
        brief = self._brief_from_prompt(prompt)
        if brief:
            self._packet = self.retriever.retrieve(brief)
            self._last_sources = self._packet.sources()
            prompt = self._research_prompt(prompt, self._packet)
        else:
            prompt = self._production_prompt(prompt)

        result = self.gemini.generate(prompt)
        return ExternalCallResult(
            integration_id=self.provider,
            status_code=result.status_code,
            response_id=result.response_id,
            payload={
                "provider_payload": result.payload,
                "retrieval_sources": list(self._last_sources),
            },
        )

    @staticmethod
    def text(result: ExternalCallResult) -> str:
        body = result.payload.get("provider_payload") if isinstance(result.payload, dict) else result.payload
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

    @staticmethod
    def sources(result: ExternalCallResult) -> list[dict[str, str]]:
        if not isinstance(result.payload, dict):
            return []
        value = result.payload.get("retrieval_sources")
        return value if isinstance(value, list) else []
