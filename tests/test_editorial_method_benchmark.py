import json
import os
import re

import pytest

from content_factory.free_research import FreeWebGeminiAdapter
from content_factory.research import parse_research_json


pytestmark = pytest.mark.external


def _metrics(text: str) -> dict:
    value = " ".join(text.strip().split())
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", value) if s.strip()]
    words = re.findall(r"[A-Za-zА-Яа-яЁё0-9]+", value.casefold())
    trigrams = [tuple(words[i:i + 3]) for i in range(len(words) - 2)]
    repeated_trigrams = len(trigrams) - len(set(trigrams))
    generic_openings = (
        "история полна",
        "мало кто знает",
        "вы знали",
        "знаете ли вы",
        "многие считают",
        "с древних времен",
        "на протяжении веков",
    )
    opening = value.casefold()[:140]
    generic_opening = any(item in opening for item in generic_openings)
    concrete_markers = bool(
        re.search(r"\b(?:1[0-9]{3}|20[0-9]{2}|19[0-9]{2}|18[0-9]{2}|17[0-9]{2})\b", value)
        or re.search(r"\b(?:вулкан|император|король|город|война|экспедици|археолог|летопис|учен|остров)\b", value.casefold())
    )
    abstract_fillers = sum(
        value.casefold().count(item)
        for item in (
            "важно отметить",
            "таким образом",
            "следует отметить",
            "интересно, что",
            "в современном мире",
            "это показывает",
        )
    )
    return {
        "chars": len(value),
        "sentences": len(sentences),
        "unique_word_ratio": round(len(set(words)) / max(len(words), 1), 3),
        "repeated_trigrams": repeated_trigrams,
        "generic_opening": generic_opening,
        "concrete_opening": concrete_markers,
        "abstract_fillers": abstract_fillers,
    }


@pytest.mark.skipif(
    not os.environ.get("GEMINI_API_KEY"),
    reason="GEMINI_API_KEY is required for live editorial benchmark",
)
def test_live_editorial_method_benchmark_same_knowledge():
    topic = "Малоизвестные факты из истории человечества"
    research = FreeWebGeminiAdapter()

    research_prompt = f"""Research the topic and return ONLY JSON:
{{"topic":"string","summary":"string","claims":[{{"id":"claim-1","text":"atomic factual claim","source_ids":["source-1"],"evidence_ids":["evidence-1"]}}],"sources":[{{"id":"source-1","title":"string","url":"https://..."}}],"evidence":[{{"id":"evidence-1","source_id":"source-1","excerpt":"short supporting passage"}}]}}
Use several distinct historical examples from different periods or regions. Keep claims bounded and source-backed. Do not invent facts.
TOPIC:
{topic}
"""
    result = research.research(research_prompt)
    assert 200 <= result.status_code < 300
    payload = parse_research_json(research.text(result))
    claims = payload["claims"]
    evidence = payload["evidence"]
    assert len(claims) >= 3 and evidence

    knowledge = json.dumps(
        {"claims": claims[:6], "evidence": evidence[:12]},
        ensure_ascii=False,
    )

    prompts = {
        "baseline": f"""Write one finished Telegram publication in Russian.
Return ONLY JSON: {{"title":"string","content":"string"}}.
Length: 500-1000 characters. Use only the supplied claims and evidence.
Write naturally and coherently.
TOPIC: {topic}
KNOWLEDGE: {knowledge}
""",
        "editorial": f"""Write one finished Telegram publication in Russian.
Return ONLY JSON: {{"title":"string","content":"string"}}.
Length: 500-1000 characters. Use only the supplied claims and evidence.
Apply this editorial method:
1. Open with the most concrete, surprising verified fact or scene, not a generic statement about history.
2. Develop one clear idea instead of summarizing the whole topic.
3. Use specific names, dates, places or actions when supported by the evidence.
4. Every factual sentence must stay within the scope of the supplied claims.
5. Prefer short, varied sentences and natural transitions over template connectors.
6. End with a conclusion that follows from the example, not a generic moral.
7. No clickbait, no rhetorical 'Вы знали?', no filler, no em dash.
TOPIC: {topic}
KNOWLEDGE: {knowledge}
""",
        "editorial_plus": f"""Write one finished Telegram publication in Russian.
Return ONLY JSON: {{"title":"string","content":"string"}}.
Length: 500-1000 characters. Use only the supplied claims and evidence.
Apply a two-pass editorial method.
PASS 1: Draft around ONE strongest factual tension, contrast, or historical turning point.
PASS 2: Rewrite the draft as a human editor would: remove generic openings, filler, repeated conclusions, empty transitions, excessive adjectives and unnecessary context; make the first two sentences concrete; vary sentence length; preserve epistemic limits; finish on the strongest idea rather than a moral.
Hard constraints: no invented facts, no 'Вы знали?', no em dash, no generic 'история полна...' opening.
TOPIC: {topic}
KNOWLEDGE: {knowledge}
""",
    }

    outputs = {}
    metrics = {}
    for method, prompt in prompts.items():
        generated = research.research(prompt)
        assert 200 <= generated.status_code < 300
        payload_out = json.loads(research.text(generated))
        text = str(payload_out["content"]).strip()
        assert 500 <= len(text) <= 1000
        assert "—" not in text
        outputs[method] = text
        metrics[method] = _metrics(text)

    assert len(set(outputs.values())) == 3

    print("\n=== EDITORIAL BENCHMARK ===")
    for method in ("baseline", "editorial", "editorial_plus"):
        print(f"\n[{method}]")
        print(outputs[method])
        print(json.dumps(metrics[method], ensure_ascii=False))

    # The benchmark is diagnostic: methods are compared on observed properties.
    assert all(not metrics[m]["generic_opening"] for m in ("editorial", "editorial_plus"))
    assert all(metrics[m]["abstract_fillers"] <= metrics["baseline"]["abstract_fillers"] for m in ("editorial", "editorial_plus"))
