import json

from content_factory.local_adapter import LocalTextAdapter


def test_local_script_uses_supplied_accepted_knowledge():
    prompt = """Create a complete script from this ContentSpec.
Return JSON: {"script_id":"script-1","title":"string","units":[]}
Every factual unit must retain the relevant durable claim and evidence refs from the ContentSpec.
CONTENT SPEC:
{"spec_id":"spec-1","title":"Thai spirit houses","claim_refs":["kc-123"],"evidence_refs":["ke-456"]}
ACCEPTED KNOWLEDGE:
{"claims":[{"claim_id":"kc-123","text":"Thai spirit houses are commonly associated with offerings.","evidence_ids":["ke-456"]}]}
"""
    result = LocalTextAdapter().generate(prompt)
    payload = json.loads(LocalTextAdapter.response_text(result))

    texts = [unit["text"] for unit in payload["units"]]
    assert any("Thai spirit houses are commonly associated with offerings." in text for text in texts)
    assert not any(text == "Here is what the evidence tells us." for text in texts)
