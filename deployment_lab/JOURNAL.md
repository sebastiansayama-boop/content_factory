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

### Current status
IMPLEMENTED — awaiting deployment and external HTTP verification.

### Interpretation rule
A successful Render deployment alone does not count as proof of public HTTP availability. Public HTTP response is required.
