# 00 — Inbox

Incoming material before classification.

## Purpose

`00_inbox` is the entry boundary for material whose semantic status is not yet established. It is a holding area, not a knowledge base and not a workflow state of the content itself.

## Allowed input

- raw notes
- links and external references
- imported text or files
- new questions
- unclassified case inputs
- requests whose evidence basis is not yet assessed

## Minimum intake record

Every material item should be identifiable and reconstructable with, at minimum:

```text
inbox_item_id
received_at
source_ref
raw_content_or_content_ref
submitted_by_or_origin
initial_context
classification_status
```

`source_ref` identifies where the material came from. `raw_content_or_content_ref` preserves the original input or a stable reference to it. Secrets must not be stored in repository records.

## Classification

The first operation on an inbox item is classification, not interpretation.

A classifier may determine that the item is:

```text
OBSERVATION_CANDIDATE
EVIDENCE_CANDIDATE
QUESTION
WORK_REQUEST
RESEARCH_LEAD
DUPLICATE
IRRELEVANT
INVALID
```

Classification is a decision about how the input may be handled. It is not proof that the underlying content is true.

## Allowed exits

```text
INBOX
  ├─→ observation / evidence handling
  ├─→ working context for an identified work item
  ├─→ research queue / question
  ├─→ explicit discard
  └─→ remain pending
```

An item may support more than one downstream object. Classification must preserve the link to the original inbox item.

## Invariants

- Inbox content is not authoritative.
- Classification does not promote a claim to knowledge.
- Discard must be explicit; absence of processing is not discard.
- The original material must remain reconstructable until an explicit retention policy permits removal.
- No downstream stage may silently replace the original provenance.

## Completion criterion

An inbox item is processed only when it has an explicit classification outcome and a traceable downstream reference or an explicit discard record.

This README defines the operating contract; it does not itself constitute a classification record.