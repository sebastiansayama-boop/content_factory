from __future__ import annotations

import hashlib
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from .integrations import ExternalCallResult
from .research_quality import is_relevant_source


class LocalResearchAdapter:
    """Credential-free research adapter backed by public Wikipedia APIs.

    Set FACTORY_LOCAL_RESEARCH_MODE=fixture only for deterministic smoke tests.
    """

    def __init__(self, *, fixture: bool | None = None) -> None:
        if fixture is None:
            fixture = os.environ.get("FACTORY_LOCAL_RESEARCH_MODE", "web").strip().lower() == "fixture"
        self.fixture = fixture

    @staticmethod
    def _request_json(url: str) -> dict[str, Any]:
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": (
                    "ContentFactory/1.0 "
                    "(+https://github.com/sebastiansayama-boop/content_factory)"
                )
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=20.0) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raise ValueError(f"public research provider returned HTTP {exc.code}") from exc
        except urllib.error.URLError as exc:
            raise ValueError(f"public research provider connection failed: {exc.reason}") from exc
        if not isinstance(payload, dict):
            raise ValueError("public research provider returned a non-object response")
        return payload

    @staticmethod
    def _is_future_history_brief(brief: str) -> bool:
        lowered = brief.lower()
        future_terms = ("будущ", "future", "прогноз", "prediction", "prophecy", "пророч")
        history_terms = ("истори", "past", "древ", "ancient", "эпох", "centur", "врем")
        return any(token in lowered for token in future_terms) and any(
            token in lowered for token in history_terms
        )

    @classmethod
    def _queries(cls, brief: str) -> list[str]:
        compact = re.sub(r"\s+", " ", brief).strip()
        lowered = compact.lower()
        queries: list[str] = []

        if cls._is_future_history_brief(compact):
            queries.extend(
                [
                    "history of ideas about the future",
                    "ancient conceptions of the future prophecy time",
                    "eschatology history concept of future",
                    "utopia history future society",
                    "history of science fiction future",
                    "Jules Verne future technology",
                    "H. G. Wells Anticipations future",
                    "Albert Robida future Paris",
                    "John Elfreth Watkins predictions 2000",
                    "history of futurism",
                ]
            )

        queries.append(compact[:240])

        if any(token in lowered for token in ("верн", "verne")):
            queries.append("Jules Verne From the Earth to the Moon")
        if any(token in lowered for token in ("уэллс", "wells")):
            queries.append("H. G. Wells Anticipations")
        if any(token in lowered for token in ("робида", "robida")):
            queries.append("Albert Robida future Paris")
        if any(token in lowered for token in ("уоткинс", "watkins")):
            queries.append("John Elfreth Watkins predictions 2000")

        return list(dict.fromkeys(q for q in queries if q))

    @classmethod
    def _preferred_titles(cls, brief: str) -> list[str]:
        if not cls._is_future_history_brief(brief):
            return []
        return [
            "History of science fiction",
            "Utopia",
            "Eschatology",
            "Prophecy",
            "Jules Verne",
            "H. G. Wells",
            "Albert Robida",
            "John Elfreth Watkins",
            "Futurism",
            "Epic of Gilgamesh",
            "Augustine of Hippo",
            "Joachim of Fiore",
        ]

    def _search(self, api_root: str, query: str) -> list[dict[str, Any]]:
        url = f"{api_root}/w/api.php?" + urllib.parse.urlencode(
            {
                "action": "query",
                "list": "search",
                "srsearch": query,
                "format": "json",
                "utf8": "1",
                "srlimit": "6",
                "srprop": "snippet",
            }
        )
        payload = self._request_json(url)
        query_block = payload.get("query")
        if not isinstance(query_block, dict):
            return []
        results = query_block.get("search")
        return [item for item in results if isinstance(item, dict)] if isinstance(results, list) else []

    def _summary(self, api_root: str, title: str) -> dict[str, Any] | None:
        encoded_title = urllib.parse.quote(title.replace(" ", "_"), safe="_()'!-")
        payload = self._request_json(f"{api_root}/api/rest_v1/page/summary/{encoded_title}")
        if not isinstance(payload.get("extract"), str) or not payload["extract"].strip():
            return None
        return payload

    def _collect_titles(self, root: str, brief: str) -> list[tuple[str, str, dict[str, Any]]]:
        language = "ru" if root.startswith("https://ru.") else "en"
        collected: list[tuple[str, str, dict[str, Any]]] = []
        seen: set[str] = set()

        for title in self._preferred_titles(brief):
            try:
                summary = self._summary(root, title)
            except ValueError:
                continue
            if summary is not None:
                key = title.lower()
                if key not in seen:
                    seen.add(key)
                    collected.append((language, title, summary))

        for query in self._queries(brief):
            for result in self._search(root, query):
                title = result.get("title")
                if not isinstance(title, str) or not title.strip():
                    continue
                key = title.lower()
                if key in seen:
                    continue
                try:
                    summary = self._summary(root, title)
                except ValueError:
                    continue
                if summary is None:
                    continue
                seen.add(key)
                collected.append((language, title, summary))
                if len(collected) >= 14:
                    break
            if len(collected) >= 14:
                break

        return collected

    @staticmethod
    def _abstract_from_inverted_index(value: Any) -> str:
        if not isinstance(value, dict):
            return ""
        words: dict[int, str] = {}
        for token, positions in value.items():
            if not isinstance(token, str) or not isinstance(positions, list):
                continue
            for position in positions:
                if isinstance(position, int):
                    words[position] = token
        return " ".join(words[index] for index in sorted(words))

    def _openalex_works(self, brief: str) -> list[dict[str, str]]:
        query = "history future prophecy eschatology science fiction futurism" if self._is_future_history_brief(brief) else brief[:180]
        url = "https://api.openalex.org/works?" + urllib.parse.urlencode({"search": query, "per-page": "8"})
        try:
            payload = self._request_json(url)
        except ValueError:
            return []
        results = payload.get("results")
        if not isinstance(results, list):
            return []
        works: list[dict[str, str]] = []
        for item in results:
            if not isinstance(item, dict):
                continue
            title = item.get("display_name")
            if not isinstance(title, str) or not title.strip():
                continue
            abstract = self._abstract_from_inverted_index(item.get("abstract_inverted_index"))
            if not abstract.strip():
                continue
            location = item.get("primary_location")
            landing = location.get("landing_page_url") if isinstance(location, dict) else None
            openalex_url = item.get("id")
            source_url = landing if isinstance(landing, str) and landing.startswith("http") else openalex_url
            if not isinstance(source_url, str) or not source_url.startswith("http"):
                continue
            works.append({"title": title.strip(), "url": source_url, "abstract": abstract.strip(), "year": str(item.get("publication_year") or "")})
        return works
    def _web_research(self, brief: str) -> ExternalCallResult:
        roots = ["https://en.wikipedia.org"]
        if not self._is_future_history_brief(brief):
            roots = ["https://en.wikipedia.org", "https://ru.wikipedia.org"]

        ranked: list[tuple[str, str, dict[str, Any]]] = []
        seen_titles: set[tuple[str, str]] = set()
        for root in roots:
            for language, title, summary in self._collect_titles(root, brief):
                key = (language, title.lower())
                if key in seen_titles:
                    continue
                seen_titles.add(key)
                ranked.append((language, title, summary))
                if len(ranked) >= 10:
                    break
            if len(ranked) >= 10:
                break

        ranked = [
            item for item in ranked
            if is_relevant_source(
                brief=brief,
                title=item[1],
                extract=str(item[2].get("extract", "")),
            )
        ]
        if not ranked:
            raise ValueError("research relevance gate found no relevant public sources")

        sources: list[dict[str, str]] = []
        evidence: list[dict[str, str]] = []
        claims: list[dict[str, Any]] = []
        seen_urls: set[str] = set()

        for index, (language, title, summary) in enumerate(ranked[:8], start=1):
            extract = str(summary.get("extract", "")).strip()
            if not extract:
                continue
            page_url = (
                f"https://{'ru' if language == 'ru' else 'en'}.wikipedia.org/wiki/"
                f"{urllib.parse.quote(title.replace(' ', '_'))}"
            )
            if page_url in seen_urls:
                continue

            source_id = f"source-{index}"
            evidence_id = f"evidence-{index}"
            claim_id = f"claim-{index}"
            sources.append({"id": source_id, "title": title, "url": page_url})
            evidence.append(
                {
                    "id": evidence_id,
                    "source_id": source_id,
                    "excerpt": extract[:800],
                    "locator": "Wikipedia article lead",
                    "provenance": "wikipedia-public-api",
                }
            )
            claims.append(
                {
                    "id": claim_id,
                    "text": extract.split("\n", 1)[0].strip(),
                    "confidence": "medium",
                    "source_ids": [source_id],
                    "evidence_ids": [evidence_id],
                    "scope": "public Wikipedia source; discovery-grade evidence",
                    "known_unknowns": [
                        "Wikipedia is a secondary source and should be rechecked against primary or institutional sources before publication."
                    ],
                }
            )
            seen_urls.add(page_url)

        for item in self._openalex_works(brief):
            if not is_relevant_source(brief=brief, title=item["title"], extract=item["abstract"]):
                continue
            source_id = f"source-{len(sources) + 1}"
            evidence_id = f"evidence-{len(evidence) + 1}"
            claim_id = f"claim-{len(claims) + 1}"
            if item["url"] in seen_urls:
                continue
            abstract = item["abstract"]
            first_sentence = re.split(r"(?<=[.!?])\\s+", abstract, maxsplit=1)[0].strip() or abstract[:500]
            sources.append({"id": source_id, "title": item["title"], "url": item["url"]})
            evidence.append({"id": evidence_id, "source_id": source_id, "excerpt": abstract[:1000], "locator": f"OpenAlex-indexed abstract ({item['year'] or 'year unknown'})", "provenance": "openalex-public-api"})
            claims.append({"id": claim_id, "text": first_sentence, "confidence": "medium", "source_ids": [source_id], "evidence_ids": [evidence_id], "scope": "scholarly work indexed by OpenAlex", "known_unknowns": ["The indexed abstract supports the paper's stated argument; it is not independent verification of every historical claim."]})
            seen_urls.add(item["url"])
            if len(claims) >= 10:
                break

        if not claims:
            raise ValueError("public research provider produced no claims")

        if self._is_future_history_brief(brief):
            angles = [
                "Future as prophecy versus future as possibility",
                "From cyclical and theological futures to open historical futures",
                "From utopian speculation to technological extrapolation",
                "Why predicted functions can outlive predicted machines",
            ]
        else:
            angles = ["Evidence-led source synthesis"]

        topic = brief.split(". ", 1)[0].strip() or brief[:180]
        summary_text = (
            "Research discovered from public Wikipedia sources: "
            + "; ".join(s["title"] for s in sources[:6])
        )
        body = {
            "topic": topic,
            "summary": summary_text,
            "claims": claims,
            "sources": sources,
            "evidence": evidence,
            "editorial_angles": angles,
        }
        digest = hashlib.sha256(brief.encode("utf-8")).hexdigest()[:16]
        return ExternalCallResult(
            integration_id="public-research-wikipedia-openalex",
            status_code=200,
            response_id=f"wikipedia-{digest}",
            payload={"output_text": json.dumps(body, ensure_ascii=False)},
        )

    def _fixture_research(self, brief: str) -> ExternalCallResult:
        body = {
            "topic": brief,
            "summary": f"Development fixture for: {brief}",
            "claims": [{
                "id": "claim-local-1",
                "text": f"Development fixture claim for {brief}.",
                "confidence": "low",
                "source_ids": ["source-local-1"],
                "evidence_ids": ["evidence-local-1"],
                "scope": "local smoke test only",
                "known_unknowns": ["Not live-web research."],
            }],
            "sources": [{
                "id": "source-local-1",
                "title": "Local development fixture",
                "url": "https://example.invalid/content-factory/local",
            }],
            "evidence": [{
                "id": "evidence-local-1",
                "source_id": "source-local-1",
                "excerpt": f"Fixture evidence for {brief}.",
                "locator": "fixture",
                "provenance": "local-research-fixture",
            }],
            "editorial_angles": ["Development fixture"],
        }
        digest = hashlib.sha256(brief.encode("utf-8")).hexdigest()[:16]
        return ExternalCallResult(
            integration_id="local-research-fixture",
            status_code=200,
            response_id=f"local-{digest}",
            payload={"output_text": json.dumps(body, ensure_ascii=False)},
        )

    def _production(self, prompt: str) -> ExternalCallResult:
        topic_match = re.search(r"Topic:\s*(.+)", prompt)
        topic = topic_match.group(1).strip() if topic_match else "Content Factory"
        claims_match = re.search(r"Claims:\n(.+?)(?:\nSources:|$)", prompt, flags=re.S)
        claims_text = claims_match.group(1).strip() if claims_match else ""
        claim_rows = [line.strip()[2:] for line in claims_text.splitlines() if line.strip().startswith("- ")]
        claim_ids = [row.split(":", 1)[0].strip() for row in claim_rows if ":" in row]
        source_match = re.search(r"Sources:\n(.+)$", prompt, flags=re.S)
        source_rows = (
            [line.strip()[2:] for line in source_match.group(1).splitlines() if line.strip().startswith("- ")]
            if source_match
            else []
        )
        source_ids = [row.split(":", 1)[0].strip() for row in source_rows if ":" in row]

        if "one article" in prompt:
            paragraphs = [row.split(":", 1)[1].strip() for row in claim_rows if ":" in row]
            content = f"{topic}\n\n" + "\n\n".join(paragraphs[:6])
            title = topic
        else:
            content = f"{topic}: " + " ".join(
                row.split(":", 1)[1].strip() for row in claim_rows[:3] if ":" in row
            )
            title = topic

        body = {
            "title": title,
            "content": content.strip(),
            "claim_refs": claim_ids,
            "source_refs": source_ids,
        }
        digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16]
        return ExternalCallResult(
            integration_id="local-research-production",
            status_code=200,
            response_id=f"local-production-{digest}",
            payload={"output_text": json.dumps(body, ensure_ascii=False)},
        )

    def research(self, prompt: str) -> ExternalCallResult:
        if not prompt.strip():
            raise ValueError("research prompt must not be empty")
        brief = prompt.split("USER BRIEF:", 1)[-1].strip()
        if "Research the user's brief" in prompt:
            return self._fixture_research(brief) if self.fixture else self._web_research(brief)
        return self._production(prompt)

    @staticmethod
    def text(result: ExternalCallResult) -> str:
        payload = result.payload
        if not isinstance(payload, dict) or not isinstance(payload.get("output_text"), str):
            raise ValueError("local research response contains no text output")
        return payload["output_text"]

    @staticmethod
    def sources(result: ExternalCallResult) -> list[dict[str, str]]:
        return []
