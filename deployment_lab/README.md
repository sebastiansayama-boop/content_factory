# Deployment Lab

Small, independently deployable proofs used to establish the infrastructure required by Content Factory before modifying the factory itself.

## Probe 001 — public HTTP service

Purpose: prove that a minimal application from this repository can be built and exposed publicly on Render without Docker, and that the application binds to Render's supplied `PORT`.

Endpoints:

- `GET /` → plain-text success response
- `GET /health` → JSON health response

Success condition: the public URL returns HTTP 200 for both endpoints.

This probe intentionally has no Content Factory logic, database, AI provider, authentication, or external side effects.
