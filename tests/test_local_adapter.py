from content_factory.local_adapter import LocalTextAdapter
from content_factory.workspace import _json_from_text


def test_local_adapter_planner_preserves_requested_formats():
    prompt = """Return ONLY valid JSON with this exact top-level shape:
{"objective":"string","research_questions":["question"],"source_requirements":["source"],"deliverables":[{"format":"requested format","purpose":"purpose"}]}
Requested formats: ["short_video", "telegram"]
"""
    adapter = LocalTextAdapter()
    value = _json_from_text(adapter.response_text(adapter.generate(prompt)))
    assert [item["format"] for item in value["deliverables"]] == ["short_video", "telegram"]


def test_local_adapter_reviewer_returns_valid_pass():
    prompt = """Return ONLY valid JSON:
{
  "status": "PASS | REVISE | FAIL",
  "issues": ["specific issue"],
  "required_changes": ["specific repair instruction"],
  "checked_claims": ["claim id"],
  "confidence": 0.0
}
KNOWLEDGE REFERENCES: ["kc-test"]
"""
    adapter = LocalTextAdapter()
    value = _json_from_text(adapter.response_text(adapter.generate(prompt)))
    assert value["status"] == "PASS"
    assert value["checked_claims"] == ["kc-test"]
    assert value["confidence"] == 0.9
