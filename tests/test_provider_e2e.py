import json
import os

import pytest

from content_factory.assembly import QualityGate
from content_factory.asset_registry import RegisteredAsset
from content_factory.free_research import FreeWebGeminiAdapter
from content_factory.openverse_adapter import OpenverseImageProvider
from content_factory.providers import ImageProvider, QCProvider, ResearchProvider
from content_factory.research import parse_research_json


pytestmark = pytest.mark.external


@pytest.mark.skipif(
    not os.environ.get("GEMINI_API_KEY"),
    reason="GEMINI_API_KEY is required for live provider E2E",
)
def test_live_provider_e2e_topic_to_research_text_image_qc_and_preview(tmp_path):
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

    claim = claims[0]
    claim_id = str(claim["id"])
    evidence_id = str(claim["evidence_ids"][0])

    production_prompt = f"""Write one concise Telegram-ready paragraph about the topic.
Use only the supplied claim and evidence. Return ONLY JSON:
{{"title":"string","content":"string"}}
CLAIM: {claim["text"]}
EVIDENCE: {json.dumps(evidence, ensure_ascii=False)}
"""
    generated = research.research(production_prompt)
    assert 200 <= generated.status_code < 300
    generated_payload = json.loads(research.text(generated))
    title = str(generated_payload["title"]).strip()
    text = str(generated_payload["content"]).strip()
    assert title and text

    images = OpenverseImageProvider().search(topic, limit=1)
    assert images, "Openverse returned no usable image candidates"
    image = images[0]
    assert isinstance(image.url, str) and image.url.startswith(("http://", "https://"))

    run_id = "provider-e2e"
    unit_id = "unit-1"
    asset = RegisteredAsset(
        asset_id="asset-openverse-1",
        run_id=run_id,
        job_id="job-openverse-1",
        asset_request_id="request-visual",
        script_unit_id=unit_id,
        asset_type="visual",
        provider=image.source,
        uri=image.url,
        claim_refs=(claim_id,),
        evidence_refs=(evidence_id,),
        metadata=image.to_dict(),
        created_at="",
    )
    script = {
        "title": title,
        "claim_refs": [claim_id],
        "units": [{
            "unit_id": unit_id,
            "kind": "body",
            "text": text,
            "visual_intent": topic,
            "claim_refs": [claim_id],
        }],
    }
    production_plan = {
        "format": "telegram",
        "asset_requests": [{
            "asset_request_id": "request-visual",
            "script_unit_id": unit_id,
            "type": "visual",
            "claim_refs": [claim_id],
            "evidence_refs": [evidence_id],
        }],
    }
    information_flow = {
        "claims": [{
            "claim_id": claim_id,
            "evidence_ids": [evidence_id],
        }],
        "evidence": [{
            "evidence_id": evidence_id,
            "claim_ids": [claim_id],
        }],
        "editorial_points": [{
            "point_id": "point-1",
            "claim_ids": [claim_id],
            "evidence_ids": [evidence_id],
        }],
        "content_elements": [{
            "element_id": "element-1",
        }],
        "artifacts": [{
            "artifact_id": "artifact-1",
            "content_element_ids": ["element-1"],
        }],
    }
    output = {
        "output_id": "output-provider-e2e",
        "uri": str(tmp_path / "preview.json"),
        "format": "telegram",
        "title": title,
        "sequence": [{
            "script_unit_id": unit_id,
            "text": text,
        }],
    }

    qc = QualityGate()
    assert isinstance(qc, QCProvider)
    qc_result = qc.evaluate(
        run_id=run_id,
        script=script,
        production_plan=production_plan,
        assets=[asset],
        output=output,
        information_flow=information_flow,
    )
    assert qc_result["passed"], qc_result

    preview = {
        "package_version": 1,
        "package_id": f"{run_id}:package",
        "run_id": run_id,
        "platform": "telegram",
        "title": title,
        "text": text,
        "media": [{
            **image.to_dict(),
            "type": "image",
            "claim_refs": [claim_id],
            "evidence_refs": [evidence_id],
        }],
        "claims": claims,
        "evidence": evidence,
        "provenance": {
            "research_provider": research.provider,
            "image_provider": image.source,
            "qc_id": qc_result["qc_id"],
        },
        "qc": qc_result,
    }
    path = tmp_path / "content-package-preview.json"
    path.write_text(json.dumps(preview, ensure_ascii=False, indent=2), encoding="utf-8")
    assert path.exists()
    stored = json.loads(path.read_text(encoding="utf-8"))
    assert stored["qc"]["passed"] is True
    assert stored["media"][0]["source"] == "openverse"


@pytest.mark.skipif(
    not os.environ.get("GEMINI_API_KEY"),
    reason="GEMINI_API_KEY is required for live publication text variation E2E",
)
def test_live_historical_publication_text_variations_without_images():
    topic = "Малоизвестные факты из истории человечества"
    research = FreeWebGeminiAdapter()
    research_prompt = f"""You are the research stage.
Research this topic and return ONLY JSON:
{{"topic":"string","summary":"string","claims":[{{"id":"claim-1","text":"atomic factual claim","source_ids":["source-1"],"evidence_ids":["evidence-1"]}}],"sources":[{{"id":"source-1","title":"string","url":"https://..."}}],"evidence":[{{"id":"evidence-1","source_id":"source-1","excerpt":"short supporting passage"}}]}}
Use several distinct historical examples from different periods or regions. Keep every claim bounded and source-backed. Do not invent facts.
TOPIC:
{topic}
"""
    result = research.research(research_prompt)
    assert 200 <= result.status_code < 300
    payload = parse_research_json(research.text(result))
    claims = payload["claims"]
    evidence = payload["evidence"]
    assert len(claims) >= 3
    assert evidence

    knowledge = json.dumps(
        {"claims": claims[:6], "evidence": evidence[:12]},
        ensure_ascii=False,
    )
    variants = [
        ("default", "natural", "medium"),
        ("story", "natural", "medium"),
        ("analysis", "explanatory", "low"),
    ]
    outputs = {}

    for variation, style, tone in variants:
        rules = __import__("content_factory.publication_text_rules", fromlist=["resolve_publication_text_rules", "validate_publication_text"]).resolve_publication_text_rules(
            [f"style: {style}", "length: short", f"tone_strength: {tone}", f"variation: {variation}"]
        )
        prompt = f"""Write one finished Telegram publication in Russian.
Return ONLY JSON: {{"title":"string","content":"string"}}.
The publication must be 500-1000 characters and must be one coherent text, not a list.
Variation: {variation}.
Style: {style}.
Tone strength: {tone}.
Rules:
- no em dash;
- no generic openings such as "Вы знали?";
- no invented facts;
- preserve uncertainty and scope of the supplied evidence;
- use only the supplied claims and evidence;
- make this variation structurally different from the other variations.
TOPIC:
{topic}
ACCEPTED KNOWLEDGE:
{knowledge}
"""
        generated = research.research(prompt)
        assert 200 <= generated.status_code < 300
        generated_payload = json.loads(research.text(generated))
        text = str(generated_payload["content"]).strip()
        assert text
        __import__("content_factory.publication_text_rules", fromlist=["validate_publication_text"]).validate_publication_text(text, rules)
        assert "—" not in text
        assert "Вы знали?" not in text
        outputs[variation] = text

    assert len(set(outputs.values())) == 3
    assert all(len(text) >= 500 for text in outputs.values())
