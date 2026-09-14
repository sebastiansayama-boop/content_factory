from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .runtime_store import RuntimeStore


FLOW = [
    ("input", "INPUT", "01_observation"),
    ("knowledge", "KNOWLEDGE", "02_memory"),
    ("editorial", "EDITORIAL", "05_decision"),
    ("production", "PRODUCTION", "06_production"),
    ("quality", "QUALITY", "07_verification"),
    ("distribution", "DISTRIBUTION", "08_effects_feedback"),
    ("learning", "LEARNING", "09_learning"),
]

SYSTEM_NODES = [
    {
        "id": "kernel",
        "title": "CONTROL KERNEL",
        "kind": "system",
        "description": "Durable lifecycle, identity, attempts, decisions and publication boundary.",
    },
    {
        "id": "execution",
        "title": "EXECUTION",
        "kind": "system",
        "description": "Execution substrate: n8n, agents, local workers and provider adapters.",
    },
    {
        "id": "semantic",
        "title": "SEMANTIC SUBSTRATE",
        "kind": "system",
        "description": "Identity, revisions, provenance, dependencies, claims and evidence.",
    },
]

HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Content Factory Control Plane</title>
<style>
:root{font-family:Inter,Segoe UI,Arial,sans-serif;color:#e9eef5;background:#0b0f14;}
*{box-sizing:border-box}body{margin:0}a{color:inherit;text-decoration:none}
.top{padding:20px 28px;border-bottom:1px solid #27303a;background:#11161d;display:flex;justify-content:space-between;align-items:center}
.top h1{margin:0;font-size:20px}.top small{color:#8e9aa8}.wrap{max-width:1200px;margin:0 auto;padding:28px}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:24px}.stat{background:#121820;border:1px solid #27303a;border-radius:12px;padding:16px}.stat b{display:block;font-size:25px;margin-top:5px}.muted{color:#8e9aa8}
.flow{display:flex;gap:8px;align-items:stretch;overflow:auto;padding-bottom:8px}.flow a{min-width:145px;background:#121820;border:1px solid #27303a;border-radius:12px;padding:16px}.flow a:hover,.card:hover{border-color:#64748b;background:#151c25}.arrow{align-self:center;color:#566270}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:24px}.card{background:#121820;border:1px solid #27303a;border-radius:12px;padding:18px;min-height:130px}.card h3{margin:0 0 8px;font-size:15px}.tag{display:inline-block;padding:4px 8px;border:1px solid #35404d;border-radius:999px;font-size:11px;color:#aeb9c5;margin-bottom:12px}
.panel{margin-top:24px;background:#0f141b;border:1px solid #27303a;border-radius:12px;padding:20px}.panel h2{margin-top:0;font-size:16px}.rows{display:grid;gap:8px}.row{display:flex;justify-content:space-between;gap:20px;padding:10px 12px;border:1px solid #252e38;border-radius:8px}.row code{color:#a9c8ff}
button{background:#18212b;color:#e9eef5;border:1px solid #34404d;border-radius:8px;padding:8px 12px;cursor:pointer}button:hover{background:#202b37}
pre{white-space:pre-wrap;color:#c7d1dc;background:#0a0e13;border-radius:8px;padding:14px;overflow:auto}
@media(max-width:850px){.stats,.grid{grid-template-columns:1fr 1fr}.flow{flex-direction:column}.arrow{display:none}}@media(max-width:560px){.stats,.grid{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="top"><div><h1>Content Factory Control Plane</h1><small>System map · runtime · repository navigation</small></div><button onclick="loadAll()">Refresh</button></div>
<div class="wrap">
<div class="stats" id="stats"></div>
<div class="panel"><h2>Factory value flow</h2><div class="flow" id="flow"></div></div>
<div class="grid" id="systems"></div>
<div class="panel"><h2>Runtime operations</h2><div class="rows" id="runtime"></div></div>
<div class="panel"><h2>Repository model</h2><pre id="model">Loading…</pre></div>
</div>
<script>
const esc=s=>String(s).replace(/[&<>\"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}[m]));
async function get(p){const r=await fetch(p); if(!r.ok) throw new Error(await r.text()); return r.json()}
async function loadAll(){
  const [o,m,r]=await Promise.all([get('/api/overview'),get('/api/model'),get('/api/runtime')]);
  document.getElementById('stats').innerHTML=`<div class="stat">Repository files<b>${o.repository_files}</b></div><div class="stat">Work items<b>${r.work_items.length}</b></div><div class="stat">Events<b>${r.events}</b></div><div class="stat">Runtime DB<b>${r.available?'AVAILABLE':'EMPTY'}</b></div>`;
  document.getElementById('flow').innerHTML=o.flow.map((x,i)=>`${i?'<div class="arrow">→</div>':''}<a href="#" onclick="focusZone('${x.zone}');return false"><span class="tag">${esc(x.zone)}</span><h3>${esc(x.title)}</h3><div class="muted">${x.files} files</div></a>`).join('');
  document.getElementById('systems').innerHTML=o.systems.map(x=>`<div class="card"><span class="tag">SYSTEM</span><h3>${esc(x.title)}</h3><div class="muted">${esc(x.description)}</div></div>`).join('');
  document.getElementById('runtime').innerHTML=r.work_items.length?r.work_items.map(x=>`<div class="row"><div><b>${esc(x.work_item_id)}</b><br><span class="muted">${esc(x.operation_id)}</span></div><div><span class="tag">${esc(x.state)}</span><br><code>${esc(x.revision_id)}</code></div></div>`).join(''):'<div class="muted">No durable runtime work items yet. The control plane is ready to display them when RuntimeStore is populated.</div>';
  document.getElementById('model').textContent=m.content;
}
function focusZone(zone){alert('Repository zone: '+zone+'\nUse the map above as the navigation boundary. Detailed drill-down is the next layer.');}
loadAll().catch(e=>document.getElementById('model').textContent='Control plane error: '+e.message);
</script>
</body></html>"""


def _root() -> Path:
    return Path(__import__("os").environ.get("CONTENT_FACTORY_ROOT", ".")).resolve()


def _json(data: object) -> bytes:
    return json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")


def _overview(root: Path) -> dict[str, object]:
    zones: list[dict[str, object]] = []
    for zone_id, title, dirname in FLOW:
        path = root / dirname
        files = len([p for p in path.iterdir() if p.is_file()]) if path.exists() else 0
        zones.append({"id": zone_id, "title": title, "zone": dirname, "files": files})
    return {
        "repository_files": sum(1 for p in root.rglob("*") if p.is_file() and ".venv" not in p.parts and ".git" not in p.parts),
        "flow": zones,
        "systems": SYSTEM_NODES,
    }


def _runtime(root: Path) -> dict[str, object]:
    db = root / "data" / "runtime.sqlite3"
    if not db.exists():
        return {"available": False, "work_items": [], "events": 0}
    with RuntimeStore(db) as store:
        items = [
            {
                "work_item_id": x.work_item_id,
                "operation_id": x.operation_id,
                "revision_id": x.revision_id,
                "state": x.state,
            }
            for x in store.load_work_items()
        ]
        return {"available": True, "work_items": items, "events": len(store.load_events())}


class _Handler(BaseHTTPRequestHandler):
    server_version = "ContentFactoryControlPlane/0.1"

    def _send(self, body: bytes, content_type: str = "text/html; charset=utf-8", status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        root = _root()
        path = urlparse(self.path).path
        try:
            if path == "/":
                return self._send(HTML.encode("utf-8"))
            if path == "/api/overview":
                return self._send(_json(_overview(root)), "application/json; charset=utf-8")
            if path == "/api/runtime":
                return self._send(_json(_runtime(root)), "application/json; charset=utf-8")
            if path == "/api/model":
                model = root / "model" / "content-factory-map.yaml"
                if not model.exists():
                    return self._send(_json({"error": "model/content-factory-map.yaml not found"}), "application/json", 404)
                return self._send(_json({"content": model.read_text(encoding="utf-8")}), "application/json; charset=utf-8")
            return self._send(b"Not found", "text/plain; charset=utf-8", 404)
        except Exception as exc:  # pragma: no cover - exercised through HTTP process
            return self._send(_json({"error": str(exc)}), "application/json; charset=utf-8", 500)

    def log_message(self, format: str, *args: object) -> None:
        print("[control-plane] " + format % args)


def serve(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), _Handler)
    print(f"Content Factory Control Plane: http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping control plane")
    finally:
        server.server_close()
