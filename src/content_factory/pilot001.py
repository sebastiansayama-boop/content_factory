from __future__ import annotations

import json
import os
import textwrap
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from PIL import Image, ImageDraw, ImageFont


@dataclass(frozen=True)
class ResearchItem:
    title: str
    link: str
    source: str
    published: str
    summary: str


@dataclass
class Draft:
    draft_id: str
    direction: str
    angle: str
    why_now: str
    post_text: str
    carousel_slides: list[str]
    research_used: list[int]
    created_at: str
    revision: int = 1
    status: str = "READY_FOR_REVIEW"


class ResearchEngine:
    """Free research layer using public Google News RSS results."""

    def __init__(self, *, timeout: float = 15.0) -> None:
        self.timeout = timeout

    def search(self, query: str, limit: int = 8) -> list[ResearchItem]:
        url = "https://news.google.com/rss/search?" + urllib.parse.urlencode(
            {"q": query, "hl": "en-US", "gl": "US", "ceid": "US:en"}
        )
        request = urllib.request.Request(url, headers={"User-Agent": "ContentFactory-Pilot001/1.0"})
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                root = ET.fromstring(response.read())
        except (urllib.error.URLError, ET.ParseError) as exc:
            raise RuntimeError(f"research source unavailable: {exc}") from exc

        items: list[ResearchItem] = []
        for entry in root.findall("./channel/item")[:limit]:
            title = (entry.findtext("title") or "").strip()
            link = (entry.findtext("link") or "").strip()
            source_node = entry.find("source")
            source = (source_node.text or "").strip() if source_node is not None else ""
            published = (entry.findtext("pubDate") or "").strip()
            summary = (entry.findtext("description") or "").strip()
            if title and link:
                items.append(ResearchItem(title, link, source, published, summary))
        return items

    def collect(self, direction: str) -> list[ResearchItem]:
        queries = [
            f"{direction} news",
            f"{direction} trends",
            f"{direction} audience",
        ]
        merged: dict[str, ResearchItem] = {}
        for query in queries:
            for item in self.search(query, limit=6):
                merged.setdefault(item.link, item)
        return list(merged.values())[:12]


class OllamaClient:
    """Local model client. Defaults to the current Ollama qwen3:8b model family."""

    def __init__(self, base_url: str | None = None, model: str | None = None, timeout: float = 180.0) -> None:
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")).rstrip("/")
        self.model = model or os.getenv("OLLAMA_MODEL", "qwen3:8b")
        self.timeout = timeout

    def check_available(self) -> None:
        """Fail early with an actionable message when Ollama is not reachable."""
        request = urllib.request.Request(f"{self.base_url}/api/tags", headers={"Accept": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise RuntimeError(
                "Ollama is not reachable. Install/start Ollama for Windows and make sure "
                f"its local API is available at {self.base_url}. Original error: {exc}"
            ) from exc
        except json.JSONDecodeError as exc:
            raise RuntimeError("Ollama returned an invalid /api/tags response") from exc

        models = {str(item.get("name")) for item in body.get("models", []) if isinstance(item, dict)}
        if self.model not in models:
            raise RuntimeError(
                f"Ollama model {self.model!r} is not installed. Run: ollama pull {self.model}"
            )

    def generate(self, *, direction: str, research: list[ResearchItem], revision: int = 1, edit_instruction: str = "") -> Draft:
        research_text = "\n".join(
            f"[{i}] {item.title} | {item.source} | {item.published}\n{item.summary}\nURL: {item.link}"
            for i, item in enumerate(research)
        )
        prompt = f"""
You are the production brain for Content Factory Pilot001.

Direction: {direction}
Revision: {revision}
Edit instruction: {edit_instruction or 'none'}

Research material:
{research_text}

Produce one strong content opportunity for Instagram + Threads.
Do not invent facts that are not supported by the research material. Prefer useful
insight, synthesis, comparison, implications, or a clearly labeled opinion over
fake certainty. The result must be useful to a general audience and readable in
Russian unless the direction explicitly asks for another language.

Return ONLY valid JSON with this exact shape:
{{
  "angle": "...",
  "why_now": "...",
  "post_text": "...",
  "carousel_slides": ["slide 1", "slide 2", "slide 3", "slide 4", "slide 5"],
  "research_used": [0, 1]
}}

Constraints:
- post_text: 500-1200 characters.
- carousel_slides: 4-7 concise slides, each understandable alone.
- First slide is a hook; final slide is a conclusion or useful takeaway.
- research_used contains only valid integer indexes from the supplied research.
- Do not include markdown fences.
""".strip()
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a disciplined content production agent. Return JSON only."},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "format": "json",
            "options": {"temperature": 0.7},
        }
        request = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Ollama unavailable: {exc}") from exc

        content = (((body.get("message") or {}).get("content")) or "").strip()
        if not content:
            raise RuntimeError("Ollama returned no content")
        try:
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Ollama returned non-JSON content: {content[:200]}") from exc

        slides = [str(x).strip() for x in data.get("carousel_slides", []) if str(x).strip()]
        if not data.get("angle") or not data.get("post_text") or len(slides) < 4:
            raise RuntimeError("model output is incomplete: expected angle, post_text and at least 4 carousel slides")
        used = [int(x) for x in data.get("research_used", [])]
        return Draft(
            draft_id=uuid4().hex[:12],
            direction=direction,
            angle=str(data["angle"]).strip(),
            why_now=str(data.get("why_now", "")).strip(),
            post_text=str(data["post_text"]).strip(),
            carousel_slides=slides,
            research_used=used,
            created_at=datetime.now(timezone.utc).isoformat(),
            revision=revision,
        )


def render_carousel(draft: Draft, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for index, slide in enumerate(draft.carousel_slides, start=1):
        image = Image.new("RGB", (1080, 1350), (18, 18, 22))
        draw = ImageDraw.Draw(image)
        title_font = ImageFont.load_default(size=64)
        body_font = ImageFont.load_default(size=42)
        small_font = ImageFont.load_default(size=28)
        draw.text((70, 70), f"{index:02d}", fill=(130, 170, 255), font=title_font)
        draw.text((70, 180), "CONTENT FACTORY", fill=(235, 235, 240), font=small_font)
        wrapped = textwrap.wrap(slide, width=30)
        y = 330
        for line in wrapped[:12]:
            draw.text((70, y), line, fill=(250, 250, 250), font=body_font)
            y += 62
        draw.text((70, 1230), f"{draft.angle}", fill=(170, 170, 180), font=small_font)
        path = out_dir / f"{draft.draft_id}-slide-{index}.png"
        image.save(path, format="PNG")
        paths.append(path)
    return paths


def save_draft(root: Path, draft: Draft, research: list[ResearchItem]) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"{draft.draft_id}.json"
    payload = {"draft": asdict(draft), "research": [asdict(x) for x in research]}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load_draft(root: Path, draft_id: str) -> tuple[Draft, list[ResearchItem]]:
    path = root / f"{draft_id}.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    return Draft(**payload["draft"]), [ResearchItem(**x) for x in payload["research"]]
