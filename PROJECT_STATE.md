# Content Factory State

- As of: 2026-09-16
- Status: `ACTIVE_PROTOTYPE`
- Canonical runtime: `src/content_factory/`
- Current product scope: bounded V0 + text-source Content Workspace
- Automatic continuation from historical work: `NONE`

## Current role

Content Factory is the active executable content-production environment. It contains a semantic/research chain and a bounded execution runtime, with a user-facing HTTP workspace for the current text-source vertical slice.

## Current runtime boundary

The executable path is:

```text
WORK ITEM
  -> ADMIT
  -> EXECUTE CAPABILITY
  -> VERIFY EXACT REVISION
  -> ACCEPT + AUTHORITY
  -> RELEASE AUTHORITY
  -> RELEASE
  -> PUBLISHER
  -> OBSERVABLE EFFECT
```

The current repository contains a real provider boundary, persistent runtime state, HTTP service, product workspace, container and CI verification.

## Deployment truth

- Live hosted instance: `NOT_YET_DEPLOYED`
- Real external destination: `NOT_YET_CONFIGURED`
- Real external proof: `PENDING_DEPLOYMENT + DESTINATION`

These conditions must not be represented as live deployment or external business outcome.

## Repository relationship

Atlas Agent has an explicit HTTP client for Content Factory. This is an application-level integration and should be treated as a real dependency edge only where the concrete client/API contract is involved. Other repositories are not runtime dependencies merely because they contain historical Atlas material.

## Evidence rule

Research and production documents describe intended or observed work but are not proof of execution. Runtime claims should be checked against implementation and tests; external-effect claims require evidence from the external destination.
