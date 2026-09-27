# Concept Factory lifecycle

The product lifecycle is durable and explicit:

`INPUT -> RESEARCH -> EVIDENCE -> KNOWLEDGE -> EDITORIAL -> CONTENT SPEC -> PRODUCTION -> QUALITY -> APPROVAL -> RENDER/EXPORT -> DISTRIBUTION -> OBSERVATION -> LEARNING -> KNOWLEDGE`

The protected product API exposes a one-click vertical slice at `POST /api/runs/{run_id}/factory`. It stops at `REVIEW`; approval, export and publication remain separate actions.

Lifecycle inspection:
- `GET /api/runs/{run_id}`
- `GET /api/runs/{run_id}/timeline`
- `GET /api/runs/{run_id}/jobs`
- `GET /api/runs/{run_id}/publications`
- `GET /api/runs/{run_id}/observations`

Durable control actions:
- `POST /api/runs/{run_id}/approve`
- `POST /api/runs/{run_id}/export`
- `POST /api/runs/{run_id}/publish`
- `POST /api/runs/{run_id}/observe`
- `POST /api/runs/{run_id}/learn`
- `POST /api/learning/{learning_id}/promote`
- `POST /api/runs/{run_id}/replay`

Replay is incremental: unchanged research, knowledge, editorial and script are retained; only assets linked to changed claims are regenerated. A style-bible change requests a ContentSpec style revision and forces downstream production/QC/approval/export to be rerun.

## Rendering

Set `FACTORY_RENDERER=whisper_studio` and `WHISPER_STUDIO_ROOT` to the local Whisper Studio checkout. The adapter writes a local pack containing PNG and WAV assets and invokes its active `one_command.py --local-pack` contract. Whisper Studio produces `manifest.json` and `render/final.mp4`; Factory then copies the final video to its export directory and records SHA-256.

No external media provider is required for the local renderer path. The real integration test is marked `external` and runs when `WHISPER_STUDIO_ROOT` is configured.
