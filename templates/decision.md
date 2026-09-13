# Decision Record

## Identity

- `decision_id`:
- `decision_type`:
- `created_at`:
- `authority`:

## Target

- `target_type`:
- `target_id`:
- `target_revision`:

## Basis

- review_result_id:
- evidence_refs:
- dependency_refs:
- relevant_unknowns:

## Outcome

- outcome:
- rationale:

## Effects

### Authorized

- 

### Explicitly not authorized

- 

## Consequences

- state_after_decision:
- new_revision_required: yes | no
- downstream_objects_affected:

## Trace

```text
Decision
  → Target revision
  → Review result
  → Evidence
  → Upstream dependencies
```

## Reconsideration trigger

What new evidence, upstream revision, observation, or operational event would require this decision to be revisited?
