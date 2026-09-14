from __future__ import annotations

import json
import os
import re
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
        "paths": ["src/content_factory/runtime.py", "src/content_factory/runtime_store.py", "docs/architecture/factory-kernel-v0.md"],
    },
    {
        "id": "execution",
        "title": "EXECUTION",
        "kind": "system",
        "description": "Execution substrate: n8n, agents, local workers and provider adapters.",
        "paths": ["src/content_factory/n8n_capability.py", "src/content_factory/n8n_adapter.py", "src/content_factory/openai_capability.py", "src/content_factory/openai_adapter.py"],
    },
    {
        "id": "semantic",
        "title": "SEMANTIC SUBSTRATE",
        "kind": "system",
        "description": "Identity, revisions, provenance, dependencies, claims and evidence.",
        "paths": ["ontology", "model/content-factory-map.yaml", "model/state-machine.yaml"],
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
.top{position:sticky;top:0;z-index:10;padding:18px 24px;border-bottom:1px solid #27303a;background:#11161df2;backdrop-filter:blur(8px);display:flex;justify-content:space-between;align-items:center}
.top h1{margin:0;font-size:20px}.top small{color:#8e9aa8}.wrap{max-width:1250px;margin:0 auto;padding:24px}
.breadcrumb{display:flex;gap:8px;align-items:center;flex-wrap:wrap;color:#8e9aa8;font-size:13px;margin-bottom:18px}.breadcrumb a:hover{color:#fff}.crumb-current{color:#e9eef5}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:20px}.stat{background:#121820;border:1px solid #27303a;border-radius:12px;padding:15px}.stat b{display:block;font-size:24px;margin-top:5px}.muted{color:#8e9aa8}
.panel{margin-top:18px;background:#0f141b;border:1px solid #27303a;border-radius:12px;padding:18px}.panel h2{margin:0 0 14px;font-size:16px}
.flow{display:grid;grid-template-columns:repeat(7,1fr);gap:8px}.flow a{background:#121820;border:1px solid #27303a;border-radius:10px;padding:13px;min-height:112px}.flow a:hover,.card:hover,.file:hover,.work:hover{border-color:#64748b;background:#151c25}.flow h3{font-size:14px;margin:7px 0}.tag{display:inline-block;padding:4px 8px;border:1px solid #35404d;border-radius:999px;font-size:10px;color:#aeb9c5}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.card{background:#121820;border:1px solid #27303a;border-radius:12px;padding:16px;min-height:145px}.card h3{margin:9px 0 8px;font-size:15px}
.rows{display:grid;gap:8px}.row{display:flex;justify-content:space-between;gap:20px;padding:11px 12px;border:1px solid #252e38;border-radius:8px}.row code{color:#a9c8ff}
.files{display:grid;grid-template-columns:repeat(2,1fr);gap:8px}.file{padding:11px 12px;border:1px solid #252e38;border-radius:8px;background:#10161d}.file code{font-size:12px;color:#c8d3df}
.model-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}.model-section{border:1px solid #252e38;border-radius:9px;overflow:hidden}.model-section summary{cursor:pointer;padding:12px;background:#121820}.model-section pre{margin:0;border-radius:0;border-top:1px solid #252e38}
pre{white-space:pre-wrap;color:#c7d1dc;background:#0a0e13;border-radius:8px;padding:14px;overflow:auto;font-size:12px;line-height:1.45}
button{background:#18212b;color:#e9eef5;border:1px solid #34404d;border-radius:8px;padding:8px 12px;cursor:pointer}button:hover{background:#202b37}
.empty{padding:14px;border:1px dashed #34404d;border-radius:9px}.state{font-weight:600}
@media(max-width:1000px){.flow{grid-template-columns:repeat(4,1fr)}}@media(max-width:760px){.stats,.grid,.files,.model-grid{grid-template-columns:1fr 1fr}.flow{grid-template-columns:1fr 1fr}}@media(max-width:520px){.stats,.grid,.files,.model-grid,.flow{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="top"><div><h1>Content Factory Control Plane</h1><small>System map · runtime · repository navigation</small></div><button onclick="loadView()">Refresh</button></div>
<div class="wrap">
<div class="breadcrumb" id="breadcrumb"></div>
<div id="app">Loading…</div>
</div>
<script>
const esc=s=>String(s??'').replace(/[&<>\"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}[m]));
async function get(p){const r=await fetch(p);if(!r.ok)throw new Error(await r.text());return r.json()}
function qs(){return new URLSearchParams(location.search)}
function breadcrumb(parts){document.getElementById('breadcrumb').innerHTML=parts.map((x,i)=>i===parts.length-1?`<span class="crumb-current">${esc(x[0])}</span>`:`<a href="${x[1]}">${esc(x[0])}</a>`).join('<span> / </span>')}
function card(title,tag,text,href){return href?`<a class="card" href="${href}"><span class="tag">${esc(tag)}</span><h3>${esc(title)}</h3><div class="muted">${esc(text)}</div></a>`:`<div class="card"><span class="tag">${esc(tag)}</span><h3>${esc(title)}</h3><div class="muted">${esc(text)}</div></div>`}
async function loadView(){
  const q=qs(); const view=q.get('view')||'home';
  try{
    const [o,m,r]=await Promise.all([get('/api/overview'),get('/api/model'),get('/api/runtime')]);
    if(view==='zone') return renderZone(o,q.get('id'));
    if(view==='system') return renderSystem(o,q.get('id'));
    if(view==='runtime') return renderRuntime(r);
    renderHome(o,m,r);
  }catch(e){document.getElementById('app').innerHTML=`<div class="empty">Control plane error: ${esc(e.message)}</div>`}
}
function renderHome(o,m,r){
  breadcrumb([['Factory','#']]);
  document.getElementById('app').innerHTML=`
  <div class="stats"><div class="stat">Repository files<b>${o.repository_files}</b></div><div class="stat">Work items<b>${r.work_items.length}</b></div><div class="stat">Events<b>${r.events}</b></div><div class="stat">Runtime DB<b>${r.available?'AVAILABLE':'EMPTY'}</b></div></div>
  <div class="panel"><h2>Factory value flow</h2><div class="flow">${o.flow.map((x,i)=>`${i?'<div></div>':''}<a href="?view=zone&id=${encodeURIComponent(x.id)}"><span class="tag">${esc(x.zone)}</span><h3>${esc(x.title)}</h3><div class="muted">${x.files} files</div></a>`).join('')}</div></div>
  <div class="panel"><h2>System layers</h2><div class="grid">${o.systems.map(x=>card(x.title,'SYSTEM',x.description,`?view=system&id=${encodeURIComponent(x.id)}`)).join('')}</div></div>
  <div class="panel"><h2>Runtime</h2>${r.work_items.length?`<div class="rows">${r.work_items.slice(0,8).map(x=>workRow(x)).join('')}</div><p><a href="?view=runtime">Open runtime →</a></p>`:'<div class="empty">No durable runtime work items yet. This is expected until a RuntimeStore-backed operation is executed.</div>'}</div>
  <div class="panel"><h2>Repository model</h2><div class="model-grid">${m.sections.map((s,i)=>`<details class="model-section" ${i<4?'open':''}><summary>${esc(s.name)}</summary><pre>${esc(s.content)}</pre></details>`).join('')}</div><p><a href="?view=model">Open complete model →</a></p></div>`;
}
function workRow(x){return `<a class="row work" href="?view=runtime&id=${encodeURIComponent(x.work_item_id)}"><div><b>${esc(x.work_item_id)}</b><br><span class="muted">${esc(x.operation_id)}</span></div><div><span class="tag state">${esc(x.state)}</span><br><code>${esc(x.revision_id)}</code></div></a>`}
async function renderZone(o,id){const x=o.flow.find(v=>v.id===id)||o.flow[0];const z=await get('/api/zone/'+encodeURIComponent(x.id));breadcrumb([['Factory','#'],[x.title,`?view=zone&id=${encodeURIComponent(x.id)}`]]);document.getElementById('app').innerHTML=`<div class="panel"><h2>${esc(x.title)}</h2><p class="muted">Repository zone <code>${esc(x.zone)}</code>. ${z.files.length} files.</p><div class="files">${z.files.map(f=>`<div class="file"><code>${esc(f)}</code></div>`).join('')}</div></div>`}
async function renderSystem(o,id){const x=o.systems.find(v=>v.id===id)||o.systems[0];breadcrumb([['Factory','#'],[x.title,`?view=system&id=${encodeURIComponent(x.id)}`]]);document.getElementById('app').innerHTML=`<div class="panel"><span class="tag">SYSTEM</span><h2 style="margin-top:10px">${esc(x.title)}</h2><p class="muted">${esc(x.description)}</p><h2>Known implementation surfaces</h2><div class="files">${x.paths.map(p=>`<div class="file"><code>${esc(p)}</code></div>`).join('')}</div></div>`}
async function renderRuntime(r){const id=qs().get('id');breadcrumb([['Factory','#'],['Runtime','?view=runtime']]);if(!r.work_items.length){document.getElementById('app').innerHTML='<div class="panel"><h2>Runtime</h2><div class="empty">Runtime DB is empty. Execute a RuntimeStore-backed operation to populate this view.</div></div>';return}const x=r.work_items.find(v=>v.work_item_id===id)||r.work_items[0];const detail=await get('/api/runtime/'+encodeURIComponent(x.work_item_id));document.getElementById('app').innerHTML=`<div class="panel"><span class="tag">${esc(x.state)}</span><h2 style="margin-top:10px">${esc(x.work_item_id)}</h2><div class="rows"><div class="row"><span>operation_id</span><code>${esc(x.operation_id)}</code></div><div class="row"><span>revision_id</span><code>${esc(x.revision_id)}</code></div><div class="row"><span>state</span><span>${esc(x.state)}</span></div></div></div><div class="panel"><h2>Event history</h2><div class="rows">${detail.events.map(e=>`<div class="row"><div><b>${esc(e.operation)}</b><br><span class="muted">${esc(e.actor)}</span></div><div><span class="tag">${esc(e.state)}</span><br><small>${esc(e.timestamp)}</small></div></div>`).join('')}</div></div><div class="panel"><h2>Execution attempts</h2>${detail.attempts.length?`<div class="rows">${detail.attempts.map(a=>`<div class="row"><div><b>Attempt ${a.attempt_no}</b><br><code>${esc(a.execution_id)}</code></div><div><span class="tag">${esc(a.status)}</span></div></div>`).join('')}</div>`:'<div class="empty">No execution attempts recorded.</div>'}</div>`}
loadView();
</script>
</body></html>"""


def _root() -> Path:
    return Path(os.environ.get("CONTENT_FACTORY_ROOT", ".")).resolve()


def _json(data: object) -> bytes:
    return json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")


def _overview(root: Path) -> dict[str, object]:
    zones: list[dict[str, object]] = []
    for zone_id, title, dirname in FLOW:
        path = root / dirname
        files = sorted(str(p.relative_to(root)).replace("\\", "/") for p in path.rglob("*") if p.is_file()) if path.exists() else []
        zones.append({"id": zone_id, "title": title, "zone": dirname, "files": len(files)})
    return {
        "repository_files": sum(1 for p in root.rglob("*") if p.is_file() and ".venv" not in p.parts and ".git" not in p.parts),
        "flow": zones,
        "systems": SYSTEM_NODES,
    }


def _zone(root: Path, zone_id: str) -> dict[str, object]:
    match = next((x for x in FLOW if x[0] == zone_id), None)
    if match is None:
        raise KeyError(f"unknown zone: {zone_id}")
    path = root / match[2]
    files = sorted(str(p.relative_to(root)).replace("\\", "/") for p in path.rglob("*") if p.is_file()) if path.exists() else []
    return {"id": match[0], "title": match[1], "zone": match[2], "files": files}


def _model(root: Path) -> dict[str, object]:
    path = root / "model" / "content-factory-map.yaml"
    content = path.read_text(encoding="utf-8") if path.exists() else ""
    matches = list(re.finditer(r"(?m)^[A-Za-z][A-Za-z0-9_-]*:", content))
    sections = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
        block = content[start:end].strip()
        sections.append({"name": match.group(0)[:-1], "content": block})
    return {"content": content, "sections": sections}


def _runtime(root: Path) -> dict[str, object]:
    db = root / "data" / "runtime.sqlite3"
    if not db.exists():
        return {"available": False, "work_items": [], "events": 0}
    with RuntimeStore(db) as store:
        items = [
            {"work_item_id": x.work_item_id, "operation_id": x.operation_id, "revision_id": x.revision_id, "state": x.state}
            for x in store.load_work_items()
        ]
        return {"available": True, "work_items": items, "events": len(store.load_events())}


def _runtime_item(root: Path, work_item_id: str) -> dict[str, object]:
    db = root / "data" / "runtime.sqlite3"
    if not db.exists():
        raise KeyError("runtime database not found")
    with RuntimeStore(db) as store:
        item = next((x for x in store.load_work_items() if x.work_item_id == work_item_id), None)
        if item is None:
            raise KeyError(f"unknown work item: {work_item_id}")
        return {"work_item_id": work_item_id, "events": store.load_events(work_item_id), "attempts": store.load_attempts(work_item_id)}


class _Handler(BaseHTTPRequestHandler):
    server_version = "ContentFactoryControlPlane/0.2"

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
            if path == "/api/model":
                return self._send(_json(_model(root)), "application/json; charset=utf-8")
            if path == "/api/runtime":
                return self._send(_json(_runtime(root)), "application/json; charset=utf-8")
            if path.startswith("/api/zone/"):
                return self._send(_json(_zone(root, path.rsplit("/", 1)[1])), "application/json; charset=utf-8")
            if path.startswith("/api/runtime/"):
                return self._send(_json(_runtime_item(root, path.rsplit("/", 1)[1])), "application/json; charset=utf-8")
            return self._send(b"Not found", "text/plain; charset=utf-8", 404)
        except KeyError as exc:
            return self._send(_json({"error": str(exc)}), "application/json; charset=utf-8", 404)
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
