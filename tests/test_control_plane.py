from __future__ import annotations

import json
from pathlib import Path
from threading import Thread
from urllib.request import urlopen
from uuid import uuid4

from content_factory.control_plane import ThreadingHTTPServer, _Handler
from content_factory.runtime_store import RuntimeStore


def test_overview_uses_repository_zones(tmp_path: Path, monkeypatch):
    for zone in ["01_observation", "02_memory", "05_decision", "06_production", "07_verification", "08_effects_feedback", "09_learning"]:
        (tmp_path / zone).mkdir()
        (tmp_path / zone / "README.md").write_text("x", encoding="utf-8")
    monkeypatch.setenv("CONTENT_FACTORY_ROOT", str(tmp_path))

    from content_factory.control_plane import _overview

    result = _overview(tmp_path)
    assert result["flow"][0]["title"] == "INPUT"
    assert result["flow"][3]["files"] == 1


def test_operation_projection_is_reconstructable(tmp_path: Path):
    db = tmp_path / "data" / "runtime.sqlite3"
    db.parent.mkdir()
    work_item_id = "wi-op-view"
    operation_id = "op-op-view"
    now = "2026-09-14T00:00:00+00:00"
    event = {
        "event_id": str(uuid4()), "work_item_id": work_item_id, "revision_id": "spec-r1",
        "timestamp": now, "state": "RECEIVED", "operation": "submit", "actor": "test",
        "data": {"operation_id": operation_id},
    }
    with RuntimeStore(db) as store:
        store.create_work_item(work_item_id=work_item_id, operation_id=operation_id, revision_id="spec-r1", state="RECEIVED", updated_at=now, event=event)
        attempt_id, execution_id = str(uuid4()), str(uuid4())
        store.start_attempt(attempt_id=attempt_id, work_item_id=work_item_id, operation_id=operation_id, execution_id=execution_id, attempt_no=1, started_at=now)
        store.finish_attempt(attempt_id, status="SUCCEEDED", completed_at=now)
        store.save_record(work_item_id, "execution", {"execution_id": execution_id, "capability_id": "write", "output_revision_id": "asset-r1", "payload": "demo"})
        store.save_record(work_item_id, "verification", {"output_revision_id": "asset-r1", "passed": True})
        store.save_record(work_item_id, "acceptance", {"output_revision_id": "asset-r1", "accepted": True, "authority": "approver"})
        store.save_record(work_item_id, "publication", {"publication_id": "pub-1", "output_revision_id": "asset-r1", "target": "demo://simulated", "externally_observable": False})

    from content_factory.control_plane import _operation
    result = _operation(tmp_path, work_item_id)
    assert result["work_item"]["operation_id"] == operation_id
    assert result["attempts"][0]["execution_id"] == execution_id
    assert result["records"]["verification"]["passed"] is True
    assert result["records"]["acceptance"]["authority"] == "approver"
    assert result["records"]["publication"]["publication_id"] == "pub-1"


def test_control_plane_http_smoke_and_operation_view(tmp_path: Path, monkeypatch):
    for zone in ["01_observation", "02_memory", "05_decision", "06_production", "07_verification", "08_effects_feedback", "09_learning"]:
        (tmp_path / zone).mkdir()
        (tmp_path / zone / "README.md").write_text("x", encoding="utf-8")
    (tmp_path / "model").mkdir()
    (tmp_path / "model" / "content-factory-map.yaml").write_text("name: content_factory\narchitecture:\n  value_flow:\n    - input\n", encoding="utf-8")
    (tmp_path / "data").mkdir()
    with RuntimeStore(tmp_path / "data" / "runtime.sqlite3") as store:
        now = "2026-09-14T00:00:00+00:00"
        work_item_id, operation_id = "wi-http-op", "op-http-op"
        store.create_work_item(
            work_item_id=work_item_id, operation_id=operation_id, revision_id="spec-r1", state="DELIVERED", updated_at=now,
            event={"event_id": str(uuid4()), "work_item_id": work_item_id, "revision_id": "spec-r1", "timestamp": now, "state": "DELIVERED", "operation": "deliver", "actor": "test", "data": {"operation_id": operation_id}},
        )
        attempt_id, execution_id = str(uuid4()), str(uuid4())
        store.start_attempt(attempt_id=attempt_id, work_item_id=work_item_id, operation_id=operation_id, execution_id=execution_id, attempt_no=1, started_at=now)
        store.finish_attempt(attempt_id, status="SUCCEEDED", completed_at=now)
        store.save_record(work_item_id, "execution", {"execution_id": execution_id, "capability_id": "write", "output_revision_id": "asset-r1", "payload": "demo"})
        store.save_record(work_item_id, "verification", {"output_revision_id": "asset-r1", "passed": True})
        store.save_record(work_item_id, "acceptance", {"output_revision_id": "asset-r1", "accepted": True, "authority": "approver"})
        store.save_record(work_item_id, "publication", {"publication_id": "pub-1", "output_revision_id": "asset-r1", "target": "demo://simulated", "externally_observable": False})
    monkeypatch.setenv("CONTENT_FACTORY_ROOT", str(tmp_path))

    server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    thread = Thread(target=server.serve_forever, daemon=True); thread.start()
    try:
        base = f"http://127.0.0.1:{server.server_port}"
        with urlopen(base + "/api/overview") as response:
            payload = json.loads(response.read().decode("utf-8"))
        assert "flow" in payload
        with urlopen(base + "/api/model") as response:
            model = json.loads(response.read().decode("utf-8"))
        assert "content_factory" in model["content"]
        with urlopen(base + "/api/operation/wi-http-op") as response:
            operation = json.loads(response.read().decode("utf-8"))
        assert operation["work_item"]["operation_id"] == operation_id
        assert operation["state_map"]["execution"]["status"] == "PRESENT"
        assert operation["state_map"]["acceptance"]["status"] == "ACCEPTED"
        assert operation["state_map"]["delivery"]["status"] == "DELIVERED"
        with urlopen(base + "/api/zone/production") as response:
            zone = json.loads(response.read().decode("utf-8"))
        assert zone["title"] == "PRODUCTION"
        with urlopen(base + "/") as response:
            html = response.read().decode("utf-8")
        assert "Content Factory Control Plane" in html
        assert "?view=operation&id=" in html
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=2)
