# Visual QC Telegram E2E matrix

These scenarios are the minimum manual/real-Telegram acceptance set for visual QC and regeneration.
They are intentionally scenario-driven rather than topic-random.

## Execution protocol

For each scenario:

1. Send the exact topic to the real Telegram bot.
2. Complete knowledge review if the bot requests it.
3. Inspect every image in the preview.
4. Record the machine visual decision before clicking the Telegram button.
5. Click `Подходит` or `Не подходит`.
6. For REJECT, use the specified reason and wait for the replacement.
7. Inspect the replacement and record its new machine decision.
8. Accept or reject the replacement.
9. Record the full lineage.

Required trace:

`run_id, asset_id, decision_id, candidate_id, policy_version, machine_decision, score, human_action, human_reason, timestamp, source_run_id, replacement_run_id, regeneration_instruction, replacement_decision_id, replacement_machine_decision, replacement_human_action, final_status`.

## Scenarios

| ID | Scenario | Topic / visual intent | Human action | Required observation |
|---|---|---|---|---|
| VQC-01 | Clean accept | "Крокодилы Нила: где они живут и как охотятся" / Nile crocodile in natural river habitat | ACCEPT | machine ACCEPT -> human ACCEPT; no regeneration |
| VQC-02 | Hard negative | Same topic; candidate set must include an image of a Nile cruise ship | REJECT cruise image as WRONG_SUBJECT | cruise image must not survive selection; crocodile candidate remains eligible |
| VQC-03 | Wrong subject | "Космический телескоп James Webb" / James Webb Space Telescope | REJECT any rocket/astronaut/other telescope as WRONG_SUBJECT | machine ACCEPT + human REJECT identifies false accept |
| VQC-04 | Wrong context | "Средневековая жизнь в городе" / medieval European city street | REJECT modern-looking or unrelated historical scene as WRONG_CONTEXT | verifier distinguishes subject from contextual mismatch |
| VQC-05 | Wrong image type | "Карта маршрута экспедиции" / expedition route map | REJECT photograph when map/cartographic visual is required as WRONG_IMAGE_TYPE | image_type_match participates in decision |
| VQC-06 | Multi-asset package | "Как менялось представление о будущем от античности до XX века" / 3-4 distinct historical visuals | ACCEPT valid assets, REJECT at least one deliberately bad asset | feedback is attached to the correct asset/decision, not the whole run |
| VQC-07 | Successful regeneration | Use rejected asset from VQC-06 | REJECT -> replacement ACCEPT | source decision -> regeneration -> replacement decision lineage is complete |
| VQC-08 | Repeated regeneration | Use an asset whose first replacement is still wrong | REJECT -> replacement REJECT -> second regeneration -> final ACCEPT | second regeneration keeps lineage and does not reuse stale decision_id |

## Controlled reject reasons

Use only:

- `WRONG_SUBJECT`
- `WRONG_SCENE`
- `WRONG_IMAGE_TYPE`
- `WRONG_CONTEXT`
- `QUALITY`
- `DUPLICATE`
- `OTHER`

For VQC-02 use `WRONG_SUBJECT`; VQC-04 use `WRONG_CONTEXT`; VQC-05 use `WRONG_IMAGE_TYPE`.

## Result classification

Each reviewed asset gets exactly one terminal classification:

- `PASS`: machine ACCEPT + human ACCEPT.
- `FALSE_ACCEPT`: machine ACCEPT + human REJECT.
- `REGENERATION_FAILED`: human REJECT but no replacement run completes.
- `REPLACEMENT_FALSE_ACCEPT`: replacement machine ACCEPT + human REJECT.
- `RECOVERED`: rejected asset -> replacement -> human ACCEPT.
- `REPEATED_REJECTION`: replacement also rejected and a second regeneration is required.

## Failure isolation

- machine ACCEPT + human REJECT -> visual verifier / candidate ranking.
- machine REJECT + no suitable candidate -> retrieval / candidate coverage.
- human REJECT + regeneration request fails -> regeneration API / lineage.
- replacement machine REJECT -> replacement retrieval / verifier.
- replacement machine ACCEPT + human REJECT -> regeneration instruction or candidate selection.
- replacement human ACCEPT -> end-to-end recovery succeeded.
- wrong asset receives feedback -> Telegram callback-to-asset binding defect.
- second regeneration reuses the first decision -> lineage/idempotency defect.

## Completion gate

Do not call the visual Telegram E2E pass after only VQC-01.

Minimum evidence for a meaningful pass:

- VQC-01 completed.
- VQC-02 or an equivalent hard negative completed.
- At least one FALSE_ACCEPT observed or explicitly not reproducible after inspection.
- VQC-06 completed with multiple assets.
- VQC-07 completed with human ACCEPT on the replacement.
- VQC-08 completed if a second rejection can be induced.
- Every REJECT has a decision_id, source_run_id, replacement_run_id (when regeneration was requested), and replacement decision_id.
- No replacement is accepted merely because regeneration returned HTTP 201; the replacement image must be reviewed.

## Data capture

Use one row per reviewed asset, not one row per run. This is important because VQC-06 can contain both accepted and rejected images in the same run.

Recommended compact export:

`scenario_id,run_id,asset_id,decision_id,machine_decision,score,human_action,human_reason,replacement_run_id,replacement_decision_id,replacement_machine_decision,replacement_human_action,final_status`.
