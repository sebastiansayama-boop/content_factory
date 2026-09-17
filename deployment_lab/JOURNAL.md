# Deployment Journal

## 2026-09-17 — Probe 001: public HTTP service

### Question
Can this repository produce a minimal public HTTP service on Render independently of the Content Factory runtime?

### Existing failure observed
The current `content_factory` Render service reports `live`, but the public root returns `{"error":"not found"}`. Repository code binds the Content Factory server to `PORT` with a Docker default of `8080`. Render service configuration is Docker-based. This is not yet sufficient to identify the exact public routing failure, so the factory deployment is frozen while the deployment substrate is isolated.

### Experiment
Added `deployment_lab/app.py`, a stdlib-only HTTP server. It exposes `/` and `/health` and binds to the environment-provided `PORT` (default `10000`). No factory code is involved.

### Expected evidence
1. Render build succeeds.
2. Service reaches `live`.
3. Public `GET /` returns HTTP 200.
4. Public `GET /health` returns HTTP 200 and the expected JSON body.
5. Render request metrics show requests reaching the service.

### Verification — 2026-09-17
The external public probe ran from a GitHub-hosted runner (workflow run `35167955960`, job `105033170268`) against the Render public URL.

Observed:
- `GET /` → HTTP/2 200
- response body: `deployment-probe: OK`
- `GET /health` → HTTP/2 200
- response body: `{"status": "ok", "service": "deployment-probe"}`
- public responses included `server: cloudflare`, `cf-ray`, and `x-render-origin-server: BaseHTTP/0.6 Python/3.14.3`
- Render application logs recorded the same external GET requests with HTTP 200 and matching `cf_ray` values.
- Render deployment `dep-daljh36q1p3s739qgau0` reached `live` on commit `bb6e514b4f88e09eefdf18967f96a03ebdccd854`.

### Current status
PASS — D0 (repository → deploy → process) and D1 (public HTTP ingress) are independently verified for the minimal deployment probe.

This does not prove the original Content Factory runtime or its public routing. The probe is intentionally isolated from factory logic.

### Interpretation rule
A successful Render deployment alone does not count as proof of public HTTP availability. Public HTTP response plus server-side request observation is required.
