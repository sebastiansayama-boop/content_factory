from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class OpenverseImage:
    id: str
    url: str
    preview_url: str
    title: str
    creator: str
    license: str
    source: str = "openverse"

    def to_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "url": self.url,
            "preview_url": self.preview_url,
            "title": self.title,
            "creator": self.creator,
            "license": self.license,
            "source": self.source,
        }


class OpenverseImageProvider:
    """Minimal Openverse consumer adapter; no changes to existing production code."""

    provider = "openverse"
    endpoint = "https://api.openverse.org/v1/images/"

    def __init__(self, *, opener=urllib.request.urlopen, timeout: float = 20.0) -> None:
        self._opener = opener
        self.timeout = timeout

    def _search_once(self, query: str, limit: int) -> list[OpenverseImage]:
        url = self.endpoint + "?" + urllib.parse.urlencode({
            "q": query,
            "page_size": str(limit),
        })
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": "content-factory/1.0",
            },
        )
        with self._opener(request, timeout=self.timeout) as response:
            payload: Any = json.loads(response.read().decode("utf-8"))
        results = payload.get("results", []) if isinstance(payload, dict) else []
        images: list[OpenverseImage] = []
        for item in results:
            if not isinstance(item, dict):
                continue
            image_url = str(item.get("url") or "").strip()
            preview_url = str(item.get("thumbnail") or item.get("thumbnail_url") or image_url).strip()
            if not image_url:
                continue
            images.append(OpenverseImage(
                id=str(item.get("id") or image_url),
                url=image_url,
                preview_url=preview_url,
                title=str(item.get("title") or "").strip(),
                creator=str(item.get("creator") or "").strip(),
                license=str(item.get("license") or "").strip(),
            ))
        return images

    def search(self, query: str, limit: int = 8) -> list[OpenverseImage]:
        query = str(query or "").strip()
        if not query:
            raise ValueError("image query must not be empty")
        limit = max(1, min(int(limit), 20))
        queries = [query]
        tokens = re.findall(r"[A-Za-z0-9]+", query)
        if len(tokens) > 2:
            queries.append(" ".join(tokens[:2]))
        if tokens:
            queries.append(tokens[0])
        seen: set[str] = set()
        for candidate_query in dict.fromkeys(queries):
            images = self._search_once(candidate_query, limit)
            unique = [image for image in images if image.url not in seen]
            if unique:
                return unique
        return []
