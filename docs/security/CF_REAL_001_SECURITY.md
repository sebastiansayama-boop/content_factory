# CF-REAL-001 Security Boundary

## Purpose

CF-REAL-001 proves one real provider-backed execution without enabling an externally observable publisher.

## Current controls

- `/run` requires a server-held bearer token.
- Bearer comparison uses constant-time comparison.
- Request bodies are capped at 64 KiB.
- Authorized `/run` calls are rate-limited to 10 per 60 seconds per process.
- Authentication failures are rate-limited to 20 per 60 seconds per client IP per process.
- Acceptance and release authorities are server-configured and compared against caller claims.
- `/health` does not disclose provider API-key presence.
- `requested_outcome` is capped at 16,000 characters.
- Invalid JSON, invalid UTF-8, incomplete bodies, and invalid payload shapes return controlled 400 responses.
- The default publisher is local/internal and is not externally observable.

## Residual risks

These controls are intentionally scoped to the current single-service deployment. Process-local rate limiting is not a substitute for an edge/WAF rate limiter when the service is horizontally scaled. A single shared bearer token is not an identity system and should not be used as the long-term multi-user authorization model. External publishing must remain disabled until publisher authentication, destination allowlisting, effect idempotency, timeout/retry policy, and reconciliation are separately verified.

## Test gate

Do not run CF-REAL-001 against a newly deployed build until the security and functional test workflows for that build are green. Do not enable `PUBLISH_URL` as part of CF-REAL-001.
