from __future__ import annotations

import json
from pathlib import Path
from threading import Thread
from urllib.request import urlopen

from content_factory.control_plane import ThreadingHTTPServer, _Handler, serve


def test_overview_uses_repository_zones(tmp_path: Path, monkeypatch):
    for zone in ["01_observation", "02_memory", "05_decision", "06_production", "07_verification", "08_effects_feedback", "09_learning"]:
        (tmp_path / zone).mkdir()
        (tmp_path / zone / "README.md").write_text("x", encoding="utf-8")
    monkeypatch.setenv("CONTENT_FACTORY_ROOT", str(tmp_path))

    from content_factory.control_plane import _overview

    result = _overview(tmp_path)
    assert result["flow"][0]["title"] == "INPUT"
    assert result["flow"][3]["files"] == 1


def test_control_plane_http_smoke(tmp_path: Path, monkeypatch):
    (tmp_path / "model").mkdir()
    (tmp_path / "model" / "content-factory-map.yaml").write_text("name: content_factory\n", encoding="utf-8")
    monkeypatch.setenv("CONTENT_FACTORY_ROOT", str(tmp_path))

    server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base = f"http://127.0.0.1:{server.server_port}"
        with urlopen(base + "/api/overview") as response:
            payload = json.loads(response.read().decode("utf-8"))
        assert "flow" in payload
        with urlopen(base + "/api/model") as response:
            model = json.loads(response.read().decode("utf-8"))
        assert "content_factory" in model["content"]
        with urlopen(base + "/") as response:
            html = response.read().decode("utf-8")
        assert "Content Factory Control Plane" in html
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
