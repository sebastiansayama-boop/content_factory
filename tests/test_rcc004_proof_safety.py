from __future__ import annotations

import ast
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rcc004_approved_telegram_proof.py"
WORKFLOW = ROOT / ".github" / "workflows" / "rcc004-approved-telegram-proof.yml"


def test_rcc004_workflow_has_no_automatic_real_send_trigger():
    raw = WORKFLOW.read_text(encoding="utf-8")
    # PyYAML may interpret YAML 1.1 'on' as True.
    data = yaml.safe_load(raw)
    events = data.get("on", data.get(True, {}))
    assert isinstance(events, dict)
    assert set(events) == {"workflow_dispatch"}
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
