from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Mapping, Protocol
from urllib.parse import quote
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class Source:
    source_id: str
    provider: str
    external_id: str
    title: str
    locator: str
    retrieved_at: str
    revision: str | None = None
    license: str | None = None


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    source_id: str
    locator: str
    excerpt: str
    provenance: str


@dataclass(frozen=True)
class Claim:
    claim_id: str
    statement: str
    evidence_refs: tuple[str, ...]


class ExternalSourceAdapter(Protocol):
    provider: str

    def search(self, query: str) -> list[Source]:
        ...

    def evidence(self, source: Source) -> Evidence:
        ...

    def claims(self, source: Source, evidence: Evidence) -> tuple[Claim, ...]:
        ...


def _abstract_from_inverted_index(value: Mapping[str, list[int]] | None) -> str:
    if not value:
        return ""
    tokens: list[tuple[int, str]] = []
    for word, positions in value.items():
        tokens.extend((position, word) for position in positions)
    return " ".join(word for _, word in sorted(tokens))


class OpenAlexAdapter:
    """Minimal read-only adapter from OpenAlex into Factory evidence objects."""

    provider = "openalex"
    base_url = "https://api.openalex.org"

    def __init__(self, *, opener=urlopen, retrieved_at: str = "") -> None:
        self._opener = opener
        self._retrieved_at = retrieved_at

    def _get(self, path: str) -> dict[str, Any]:
        request = Request(
            f"{self.base_url}{path}",
            headers={"Accept": "application/json", "User-Agent": "content-factory/0"},
        )
        with self._opener(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))

    def search(self, query: str) -> list[Source]:
        if not query.strip():
            raise ValueError("query must not be empty")
        payload = self._get(f"/works?search={quote(query)}&per_page=5")
        return [self._source(item) for item in payload.get("results", [])]

    def _source(self, item: Mapping[str, Any]) -> Source:
        external_id = str(item["id"])
        return Source(
            source_id=f"source:{self.provider}:{external_id.rsplit('/', 1)[-1]}",
            provider=self.provider,
            external_id=external_id,
            title=str(item.get("display_name") or item.get("title") or ""),
            locator=str(item.get("doi") or item.get("id")),
            retrieved_at=self._retrieved_at,
            revision=str(item.get("updated_date") or item.get("publication_date") or ""),
            license=(item.get("primary_location") or {}).get("license"),
        )

    def evidence(self, source: Source) -> Evidence:
        work_id = source.external_id.rsplit("/", 1)[-1]
        item = self._get(f"/works/{quote(work_id)}")
        excerpt = _abstract_from_inverted_index(item.get("abstract_inverted_index"))
        if not excerpt:
            excerpt = str(item.get("display_name") or item.get("title") or "")
        return Evidence(
            evidence_id=f"evidence:{source.source_id}",
            source_id=source.source_id,
            locator=source.locator,
            excerpt=excerpt,
            provenance=f"{source.provider}:{source.external_id}",
        )

    def claims(self, source: Source, evidence: Evidence) -> tuple[Claim, ...]:
        if not evidence.excerpt.strip():
            return ()
        return (
            Claim(
                claim_id=f"claim:{source.source_id}",
                statement=evidence.excerpt,
                evidence_refs=(evidence.evidence_id,),
            ),
        )
