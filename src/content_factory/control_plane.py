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
    {"id": "kernel", "title": "CONTROL KERNEL", "description": "Durable lifecycle, identity, attempts, decisions and publication boundary.", "paths": ["src/content_factory/runtime.py", "src/content_factory/runtime_store.py", "docs/architecture/factory-kernel-v0.md"]},
    {"id": "execution", "title": "EXECUTION", "description": "n8n, agents, local workers and provider adapters.", "paths": ["src/content_factory/n8n_capability.py", "src/content_factory/n8n_adapter.py", "src/content_factory/openai_capability.py", "src/content_factory/openai_adapter.py"]},
    {"id": "semantic", "title": "SEMANTIC SUBSTRATE", "description": "Identity, revisions, provenance, dependencies, claims and evidence.", "paths": ["ontology", "model/content-factory-map.yaml", "model/state-machine.yaml"]},
]

HTML = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Content Factory Control Plane</title>
<style>
:root{font-family:Inter,Segoe UI,Arial,sans-serif;color:#e9eef5;background:#0b0f14}*{box-sizing:border-box}body{margin:0}a{color:inherit;text-decoration:none}
.top{position:sticky;top:0;z-index:5;padding:18px 24px;border-bottom:1px solid #27303a;background:#11161df2;display:flex;justify-content:space-between;align-items:center}.top h1{margin:0;font-size:20px}.top small,.muted{color:#8e9aa8}.wrap{max-width:1280px;margin:0 auto;padding:24px}.breadcrumb{display:flex;gap:8px;flex-wrap:wrap;color:#8e9aa8;font-size:13px;margin-bottom:18px}.crumb-current{color:#fff}.stats,.grid{display:grid;gap:12px}.stats{grid-template-columns:repeat(4,1fr)}.grid{grid-template-columns:repeat(3,1fr)}.stat,.panel,.card,.step,.kv,.file{background:#121820;border:1px solid #27303a;border-radius:12px}.stat{padding:15px}.stat b{display:block;font-size:24px;margin-top:5px}.panel{margin-top:18px;padding:18px}.panel h2{margin:0 0 14px;font-size:16px}.flow{display:grid;grid-template-columns:repeat(7,1fr);gap:8px}.flow a,.card{padding:14px;min-height:110px}.flow a:hover,.card:hover,.step:hover,.kv:hover,.file:hover{border-color:#64748b;background:#151c25}.flow h3,.card h3{font-size:14px;margin:8px 0}.tag{display:inline-block;padding:4px 8px;border:1px solid #35404d;border-radius:999px;font-size:10px;color:#aeb9c5}.rows{display:grid;gap:8px}.row{display:flex;justify-content:space-between;gap:20px;padding:10px 12px;border:1px solid #252e38;border-radius:8px}.row code,.kv code{color:#a9c8ff}.files{display:grid;grid-template-columns:repeat(2,1fr);gap:8px}.file{padding:11px 12px;background:#10161d}.model-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}.model-section{border:1px solid #252e38;border-radius:9px;overflow:hidden;background:#10161d}.model-head{padding:12px;background:#151c25;display:flex;justify-content:space-between}.model-body{padding:12px;border-top:1px solid #252e38}.model-body pre{max-height:280px;overflow:auto}.steps{display:grid;grid-template-columns:repeat(11,minmax(120px,1fr));gap:8px;overflow:auto}.step{padding:12px;min-height:105px}.step b{display:block;margin:7px 0}.status-ok{color:#b8f2c8}.status-muted{color:#9aa6b2}.status-warn{color:#f3d48b}.kv-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:8px}.kv{padding:11px 12px}.kv span{display:block;color:#8e9aa8;font-size:11px;text-transform:uppercase;letter-spacing:.05em;margin-bottom:5px}.timeline{display:grid;gap:8px}.timeline .row{background:#10161d}.empty{padding:14px;border:1px dashed #34404d;border-radius:9px}pre{white-space:pre-wrap;color:#c7d1dc;background:#0a0e13;border-radius:8px;padding:14px;font-size:12px;line-height:1.45}button{background:#18212b;color:#e9eef5;border:1px solid #34404d;border-radius:8px;padding:8px 12px;cursor:pointer}@media(max-width:1100px){.flow{grid-template-columns:repeat(4,1fr)}.steps{grid-template-columns:repeat(6,minmax(120px,1fr))}}@media(max-width:760px){.stats,.grid,.files,.model-grid,.kv-grid{grid-template-columns:1fr 1fr}.flow{grid-template-columns:1fr 1fr}}@media(max-width:520px){.stats,.grid,.files,.model-grid,.kv-grid,.flow{grid-template-columns:1fr}}
</style></head>
<body><div class="top"><div><h1>Content Factory Control Plane</h1><small>System map · runtime · operation trace</small></div><button onclick="loadView()">Refresh</button></div><div class="wrap"><div class="breadcrumb" id="breadcrumb"></div><div id="app">Loading…</div></div>
<script>
const esc=s=>String(s??'').replace(/[&<>\"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}[m]));
const q=()=>new URLSearchParams(location.search); const get=async p=>{const r=await fetch(p);if(!r.ok)throw new Error(await r.text());return r.json()};
function bread(parts){document.getElementById('breadcrumb').innerHTML=parts.map((x,i)=>i===parts.length-1?`<span class="crumb-current">${esc(x[0])}</span>`:`<a href="${x[1]}">${esc(x[0])}</a>`).join('<span> / </span>')}
function workLink(x){return `<a class="row" href="?view=operation&id=${encodeURIComponent(x.work_item_id)}"><div><b>${esc(x.work_item_id)}</b><br><span class="muted">${esc(x.operation_id)}</span></div><div><span class="tag">${esc(x.state)}</span><br><code>${esc(x.revision_id)}</code></div></a>`}
async function loadView(){try{const view=q().get('view')||'home';const [o,m,r]=await Promise.all([get('/api/overview'),get('/api/model'),get('/api/runtime')]);if(view==='operation')return renderOperation(q().get('id'));if(view==='runtime')return renderRuntime(r);if(view==='zone')return renderZone(o,q().get('id'));if(view==='system')return renderSystem(o,q().get('id'));if(view==='model')return renderModel(m);renderHome(o,m,r)}catch(e){document.getElementById('app').innerHTML=`<div class="empty">Control plane error: ${esc(e.message)}</div>`}}
function renderHome(o,m,r){bread([['Factory','#']]);document.getElementById('app').innerHTML=`<div class="stats"><div class="stat">Repository files<b>${o.repository_files}</b></div><div class="stat">Work items<b>${r.work_items.length}</b></div><div class="stat">Events<b>${r.events}</b></div><div class="stat">Runtime DB<b>${r.available?'AVAILABLE':'EMPTY'}</b></div></div><div class="panel"><h2>Factory value flow</h2><div class="flow">${o.flow.map(x=>`<a href="?view=zone&id=${encodeURIComponent(x.id)}"><span class="tag">${esc(x.zone)}</span><h3>${esc(x.title)}</h3><div class="muted">${x.files} files</div></a>`).join('')}</div></div><div class="panel"><h2>System layers</h2><div class="grid">${o.systems.map(x=>`<a class="card" href="?view=system&id=${encodeURIComponent(x.id)}"><span class="tag">SYSTEM</span><h3>${esc(x.title)}</h3><div class="muted">${esc(x.description)}</div></a>`).join('')}</div></div><div class="panel"><h2>Operations</h2>${r.work_items.length?`<div class="rows">${r.work_items.map(workLink).join('')}</div>`:'<div class="empty">No durable operations yet.</div>'}</div><div class="panel"><h2>Repository model</h2><div class="model-grid">${m.sections.slice(0,8).map(s=>`<div class="model-section"><div class="model-head"><b>${esc(s.name)}</b><span class="muted">${s.lines} lines</span></div><div class="model-body"><div class="muted">${esc(s.summary||'Structured model section')}</div><details style="margin-top:8px"><summary>Show data</summary><pre>${esc(s.content)}</pre></details></div></div>`).join('')}</div><p><a href="?view=model">Open complete model →</a></p></div>`}
async function renderOperation(id){const d=await get('/api/operation/'+encodeURIComponent(id));bread([['Factory','#'],['Operations','?view=runtime'],[d.work_item.work_item_id,`?view=operation&id=${encodeURIComponent(d.work_item.work_item_id)}`]]);const s=name=>{const x=d.state_map[name];return `<div class="step"><span class="tag">${esc(x.status)}</span><b>${esc(x.title)}</b><div class="muted">${esc(x.value||'—')}</div></div>`};document.getElementById('app').innerHTML=`<div class="stats"><div class="stat">State<b>${esc(d.work_item.state)}</b></div><div class="stat">Attempts<b>${d.attempts.length}</b></div><div class="stat">Events<b>${d.events.length}</b></div><div class="stat">Operation<b style="font-size:13px;word-break:break-all">${esc(d.work_item.operation_id)}</b></div></div><div class="panel"><h2>Operation trace</h2><div class="steps">${['work_item','operation','attempt','execution','output','verification','acceptance','release','publication','delivery','observation'].map(s).join('')}</div></div><div class="panel"><h2>Work item</h2><div class="kv-grid"><div class="kv"><span>ID</span><code>${esc(d.work_item.work_item_id)}</code></div><div class="kv"><span>Revision</span><code>${esc(d.work_item.revision_id)}</code></div><div class="kv"><span>Operation ID</span><code>${esc(d.work_item.operation_id)}</code></div><div class="kv"><span>State</span>${esc(d.work_item.state)}</div></div></div><div class="panel"><h2>Attempts</h2>${d.attempts.length?`<div class="rows">${d.attempts.map(a=>`<div class="row"><div><b>Attempt ${a.attempt_no}</b><br><code>${esc(a.execution_id)}</code><br><span class="muted">${esc(a.started_at)}</span></div><div><span class="tag">${esc(a.status)}</span>${a.error?`<br><small>${esc(a.error)}</small>`:''}</div></div>`).join('')}</div>`:'<div class="empty">No attempts recorded.</div>'}</div><div class="panel"><h2>Durable projections</h2><div class="rows">${Object.entries(d.records).map(([k,v])=>`<details class="row"><summary><b>${esc(k)}</b></summary><pre>${esc(JSON.stringify(v,null,2))}</pre></details>`).join('')||'<div class="empty">No projections recorded.</div>'}</div></div><div class="panel"><h2>Event history</h2><div class="timeline">${d.events.map(e=>`<div class="row"><div><b>${esc(e.operation)}</b><br><span class="muted">${esc(e.actor)}</span></div><div><span class="tag">${esc(e.state)}</span><br><small>${esc(e.timestamp)}</small></div></div>`).join('')}</div></div>`}
async function renderRuntime(r){bread([['Factory','#'],['Operations','?view=runtime']]);document.getElementById('app').innerHTML=`<div class="panel"><h2>Operations</h2>${r.work_items.length?`<div class="rows">${r.work_items.map(workLink).join('')}</div>`:'<div class="empty">Runtime DB is empty.</div>'}</div>`}
async function renderZone(o,id){const x=o.flow.find(v=>v.id===id)||o.flow[0],z=await get('/api/zone/'+encodeURIComponent(x.id));bread([['Factory','#'],[x.title,`?view=zone&id=${encodeURIComponent(x.id)}`]]);document.getElementById('app').innerHTML=`<div class="panel"><h2>${esc(x.title)}</h2><p class="muted"><code>${esc(x.zone)}</code></p><div class="files">${z.files.map(f=>`<div class="file"><code>${esc(f)}</code></div>`).join('')||'<div class="empty">No files.</div>'}</div></div>`}
async function renderSystem(o,id){const x=o.systems.find(v=>v.id===id)||o.systems[0];bread([['Factory','#'],[x.title,`?view=system&id=${encodeURIComponent(x.id)}`]]);document.getElementById('app').innerHTML=`<div class="panel"><span class="tag">SYSTEM</span><h2 style="margin-top:10px">${esc(x.title)}</h2><p class="muted">${esc(x.description)}</p><div class="files">${x.paths.map(p=>`<div class="file"><code>${esc(p)}</code></div>`).join('')}</div></div>`}
function renderModel(m){bread([['Factory','#'],['Repository model','?view=model']]);document.getElementById('app').innerHTML=`<div class="panel"><h2>Machine model</h2><div class="model-grid">${m.sections.map(s=>`<div class="model-section"><div class="model-head"><b>${esc(s.name)}</b><span class="muted">${s.lines} lines</span></div><div class="model-body"><div>${esc(s.summary||'Structured model section')}</div><details style="margin-top:8px"><summary>Show data</summary><pre>${esc(s.content)}</pre></details></div></div>`).join('')}</div></div>`}
loadView();
</script></body></html>'''


def _root() -> Path:
    return Path(os.environ.get("CONTENT_FACTORY_ROOT", ".")).resolve()


def _json(data: object) -> bytes:
    return json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")


def _overview(root: Path) -> dict[str, object]:
    zones = []
    for zone_id, title, dirname in FLOW:
        path = root / dirname
        files = sorted(str(p.relative_to(root)).replace("\\", "/") for p in path.rglob("*") if p.is_file()) if path.exists() else []
        zones.append({"id": zone_id, "title": title, "zone": dirname, "files": len(files)})
    return {"repository_files": sum(1 for p in root.rglob("*") if p.is_file() and ".venv" not in p.parts and ".git" not in p.parts), "flow": zones, "systems": SYSTEM_NODES}


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
        start = match.start(); end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
        block = content[start:end].strip(); lines = block.count("\n") + 1; first = block.splitlines()[1].strip() if len(block.splitlines()) > 1 else ""
        sections.append({"name": match.group(0)[:-1], "content": block, "lines": lines, "summary": first})
    return {"content": content, "sections": sections}


def _runtime(root: Path) -> dict[str, object]:
    db = root / "data" / "runtime.sqlite3"
    if not db.exists():
        return {"available": False, "work_items": [], "events": 0}
    with RuntimeStore(db) as store:
        items = [{"work_item_id": x.work_item_id, "operation_id": x.operation_id, "revision_id": x.revision_id, "state": x.state} for x in store.load_work_items()]
        return {"available": True, "work_items": items, "events": len(store.load_events())}


def _operation(root: Path, work_item_id: str) -> dict[str, object]:
    db = root / "data" / "runtime.sqlite3"
    if not db.exists():
        raise KeyError("runtime database not found")
    with RuntimeStore(db) as store:
        item = next((x for x in store.load_work_items() if x.work_item_id == work_item_id), None)
        if item is None:
            raise KeyError(f"unknown work item: {work_item_id}")
        events = store.load_events(work_item_id)
        attempts = store.load_attempts(work_item_id)
        records = {}
        for record_type in ("execution", "verification", "acceptance", "publication"):
            value = store.load_record(work_item_id, record_type)
            if value is not None:
                records[record_type] = value
        execution = records.get("execution", {})
        verification = records.get("verification", {})
        acceptance = records.get("acceptance", {})
        publication = records.get("publication", {})
        state = item.state
        state_map = {
            "work_item": {"title": "Work Item", "status": "CURRENT", "value": item.work_item_id},
            "operation": {"title": "Operation", "status": "CURRENT", "value": item.operation_id},
            "attempt": {"title": "Attempt", "status": "PRESENT" if attempts else "EMPTY", "value": f"{len(attempts)} attempt(s)"},
            "execution": {"title": "Execution", "status": "PRESENT" if execution else "EMPTY", "value": execution.get("execution_id", "")},
            "output": {"title": "Output", "status": "PRESENT" if execution else "EMPTY", "value": execution.get("output_revision_id", "")},
            "verification": {"title": "Verification", "status": "PASSED" if verification.get("passed") else ("PRESENT" if verification else "EMPTY"), "value": verification.get("output_revision_id", "")},
            "acceptance": {"title": "Acceptance", "status": "ACCEPTED" if acceptance.get("accepted") else ("PRESENT" if acceptance else "EMPTY"), "value": acceptance.get("authority", "")},
            "release": {"title": "Release", "status": "RELEASED" if state in {"RELEASED", "DELIVERED", "OBSERVED"} else "NOT_REACHED", "value": "release boundary"},
            "publication": {"title": "Publication", "status": "PRESENT" if publication else "EMPTY", "value": publication.get("publication_id", "")},
            "delivery": {"title": "Delivery", "status": "DELIVERED" if state in {"DELIVERED", "OBSERVED"} else "NOT_REACHED", "value": publication.get("target", "")},
            "observation": {"title": "Observation", "status": "OBSERVED" if state == "OBSERVED" else "NOT_OBSERVED", "value": "external effect"},
        }
        return {
            "work_item": {"work_item_id": item.work_item_id, "operation_id": item.operation_id, "revision_id": item.revision_id, "state": item.state},
            "attempts": attempts,
            "events": events,
            "records": records,
            "state_map": state_map,
        }


class _Handler(BaseHTTPRequestHandler):
    server_version = "ContentFactoryControlPlane/0.3"
    def _send(self, body: bytes, content_type: str = "text/html; charset=utf-8", status: int = 200) -> None:
        self.send_response(status); self.send_header("Content-Type", content_type); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
    def do_GET(self) -> None:  # noqa: N802
        root = _root(); path = urlparse(self.path).path
        try:
            if path == "/": return self._send(HTML.encode("utf-8"))
            if path == "/api/overview": return self._send(_json(_overview(root)), "application/json; charset=utf-8")
            if path == "/api/model": return self._send(_json(_model(root)), "application/json; charset=utf-8")
            if path == "/api/runtime": return self._send(_json(_runtime(root)), "application/json; charset=utf-8")
            if path.startswith("/api/zone/"): return self._send(_json(_zone(root, path.rsplit("/", 1)[-1])), "application/json; charset=utf-8")
            if path.startswith("/api/operation/"): return self._send(_json(_operation(root, path.rsplit("/", 1)[-1])), "application/json; charset=utf-8")
            return self._send(b"Not found", "text/plain; charset=utf-8", 404)
        except Exception as exc:
            return self._send(_json({"error": str(exc)}), "application/json; charset=utf-8", 500)
    def log_message(self, fmt: str, *args: object) -> None:
        print("[control-plane] " + fmt % args)


def serve(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), _Handler)
    print(f"Content Factory Control Plane: http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping control plane")
    finally:
        server.server_close()
