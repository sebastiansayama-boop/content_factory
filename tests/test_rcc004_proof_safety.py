from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rcc004_approved_telegram_proof.py"
WORKFLOW = ROOT / ".github" / "workflows" / "rcc004-approved-telegram-proof.yml"


def test_rcc004_workflow_is_manual_fake_only():
    raw = WORKFLOW.read_text(encoding="utf-8")
    assert "\non:\n  push:" in raw
    assert "workflow_dispatch:" in raw
    assert "branches: [main]" in raw
    assert ".github/workflows/rcc004-approved-telegram-proof.yml" in raw
    assert "\n  schedule:" not in raw
    assert "TELEGRAM_BOT_TOKEN" not in raw
    assert "rcc004_approved_telegram_proof.py" not in raw
    assert "FACTORY_TELEGRAM_FAKE" in raw
    assert "test_library_publication_idempotency.py" in raw


def test_rcc004_real_send_requires_explicit_gate_and_exact_destination():
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    constants = {
        target.id: value.value
        for node in tree.body if isinstance(node, ast.Assign)
        for target in node.targets if isinstance(target, ast.Name)
        for value in [node.value] if isinstance(value, ast.Constant)
    }
    assert constants["DESTINATION"] == "@AtlasOpenLab"
    source = SCRIPT.read_text(encoding="utf-8")
    assert 'os.environ.get("RCC004_APPROVED") != "YES"' in source
    assert 'os.environ.get("TELEGRAM_CHAT_ID") != DESTINATION' in source
