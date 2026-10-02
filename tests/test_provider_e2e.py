import json
import os
import urllib.request

import pytest

from content_factory.free_research import FreeWebGeminiAdapter
from content_factory.openverse_adapter import OpenverseImageProvider
from content_factory.providers import ImageProvider, ResearchProvider
from content_factory.research import parse_research_json


pytestmark = pytest.mark.integration


@pytest.mark.skipif(
    not os.environ.get("GEMINI_API_KEY"),
    reason="GEMINI_API_KEY is required for live provider E2E",
)
def test_live_provider_e2e_topic_to_research_text_image_and_preview(tmp_path):
    topic = "convergent evolution: why unrelated animals can evolve similar traits"
    research = FreeWebGeminiAdapter()
    assert isinstance(research, ResearchProvider)

    research_prompt = f"""You are the research stage.
Research this topic using only the supplied retrieval pack and return ONLY JSON:
{{"topic":"string","summary":"string","claims":[{{"id":"claim-1","text":"atomic factual claim","source_ids":["source-1"],"evidence_ids":["evidence-1"]}}],"sources":[{{"id":"source-1","title":"string","url":"https://..."}}],"evidence":[{{"id":"evidence-1","source_id":"source-1","excerpt":"short supporting passage"}}]}}
Keep claims bounded and do not use absolute language.
USER BRIEF:
{topic}
"""
    result = research.research(research_prompt)
    assert 200 <= result.status_code < 300
    payload = parse_research_json(research.text(result))
    claims = payload["claims"]
    sources = payload["sources"]
    evidence = payload["evidence"]
    assert claims and sources and evidence

    claim_text = str(claims[0]["text"])
    production_prompt = f"""Write one concise Telegram-ready paragraph about the topic.
Use only the supplied claim and evidence. Return ONLY JSON:
{{"title":"string","content":"string"}}
CLAIM: {claim_text}
EVIDENCE: {json.dumps(evidence, ensure_ascii=False)}
"""
    generated = research.research(production_prompt)
    assert 200 <= generated.status_code < 300
    generated_payload = json.loads(research.text(generated))
    assert generated_payload["content"].strip()

    images = OpenverseImageProvider().search(topic, limit=1)
    assert images, "Openverse returned no usable image candidates"
    image = images[0]
    assert isinstance(image.url, str) and image.url.startswith(("http://", "https://"))

    preview = {
        "topic": topic,
        "title": generated_payload["title"],
        "text": generated_payload["content"],
        "media": [image.to_dict()],
        "claims": claims,
        "evidence": evidence,
        "sources": sources,
        "qc": {
            "status": "PASS",
            "checks": [
                "research claims present",
                "generated text present",
                "Openverse image candidate present",
                "claim/evidence records retained in preview",
            ],
        },
    }
    path = tmp_path / "content-package-preview.json"
    path.write_text(json.dumps(preview, ensure_ascii=False, indent=2), encoding="utf-8")
    assert path.exists()
    assert json.loads(path.read_text(encoding="utf-8"))["media"][0]["source"] == "openverse"
