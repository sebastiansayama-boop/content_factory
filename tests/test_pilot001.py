import json
from pathlib import Path

from content_factory.pilot001 import Draft, ResearchItem, OllamaClient, render_carousel, save_draft
from content_factory.telegram_pilot import keyboard, preview_text


def test_pilot001_draft_roundtrip_and_carousel(tmp_path: Path):
    research = [ResearchItem("Headline", "https://example.com", "Example", "today", "summary")]
    draft = Draft(
        draft_id="draft-001",
        direction="AI agents",
        angle="A useful angle",
        why_now="Because people care",
        post_text="Post text",
        carousel_slides=["One", "Two", "Three", "Four"],
        research_used=[0],
        created_at="now",
    )
    draft_root = tmp_path / "drafts"
    asset_root = tmp_path / "assets"
    path = save_draft(draft_root, draft, research)
    assert path.exists()
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["draft"]["draft_id"] == "draft-001"
    images = render_carousel(draft, asset_root / draft.draft_id)
    assert len(images) == 4
    assert all(p.exists() and p.suffix == ".png" for p in images)


def test_preview_and_keyboard_have_review_actions():
    draft = Draft(
        draft_id="draft-002",
        direction="AI",
        angle="Angle",
        why_now="Now",
        post_text="Text",
        carousel_slides=["1", "2", "3", "4"],
        research_used=[],
        created_at="now",
    )
    preview = preview_text(draft, [])
    assert "PILOT001" in preview
    kb = keyboard(draft.draft_id)
    buttons = [button for row in kb["inline_keyboard"] for button in row]
    assert {"approve:draft-002", "regen:draft-002", "reject:draft-002"} == {
        button["callback_data"] for button in buttons
    }


def test_ollama_default_is_local():
    client = OllamaClient()
    assert client.base_url == "http://localhost:11434"
    assert client.model
