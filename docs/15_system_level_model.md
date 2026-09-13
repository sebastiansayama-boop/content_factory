# 15 — System-Level Model

The repository is now modeled at two nested system levels:

```text
CONTENT ECOSYSTEM
        ↓
CONTENT FACTORY
        ↓
repository model / cases / records
```

The previous cognitive-production analogy remains useful as a functional model, but it is no longer treated as the top-level business architecture.

## 1. Content Ecosystem

The ecosystem connects strategic intent, audience/market context, content production, experience and broader outcomes.

```text
                         CONTENT ECOSYSTEM
                                │
        ┌───────────────────────┼────────────────────────┐
        ▼                       ▼                        ▼
 STRATEGY / INTENT      AUDIENCE / MARKET        PRODUCT / BUSINESS
        │                       │                        │
        └───────────────┬───────┴───────────────┬────────┘
                        ▼                       ▼
                 CONTENT DEMAND           PRODUCT CONTEXT
                        │                       │
                        └───────────┬───────────┘
                                    ▼
                             CONTENT FACTORY
                                    │
                                    ▼
                             CONTENT PRODUCTS
                                    │
                                    ▼
                          EXPERIENCE / CHANNELS
                                    │
                                    ▼
                              RESPONSE / OUTCOME
                                    │
                              STRATEGY UPDATE
                                    ↺
```

The ecosystem is broader than content production. Its outer functions provide intent and context and consume consequences.

See `docs/22_content_ecosystem_model.md` for the detailed boundary model.

## 2. Content Factory

The Content Factory is the production subsystem inside the ecosystem.

```text
CONTENT FACTORY
│
├── STRATEGY / PORTFOLIO INTENT
├── VALUE FLOW
│   ├── INPUT
│   ├── KNOWLEDGE
│   ├── EDITORIAL
│   ├── PRODUCTION
│   ├── QUALITY
│   ├── DISTRIBUTION
│   └── LEARNING
├── FACTORY CONTROL
└── SHARED SEMANTIC SUBSTRATE
```

See `docs/21_content_factory_level_model.md` and `docs/23_content_factory_operating_model.md` for the integrated factory model.

## 3. Functional cognitive analogy

The older analogy remains useful only inside the system model:

```text
WORLD
→ SENSE
→ REPRESENT
→ MODEL
→ WORK
→ DECIDE
→ ACT
→ OBSERVE CONSEQUENCE
→ LEARN
→ MODEL UPDATE
```

This is a functional loop, not a biological ontology.

## 4. System boundaries

There are three important boundaries:

### Ecosystem boundary

```text
external world / market
        ↓
observed context
        ↓
content ecosystem
        ↓
external experience and outcomes
```

### Factory boundary

```text
strategic demand
+ audience context
+ evidence-backed knowledge
        ↓
CONTENT FACTORY
        ↓
verified / authorized content release
```

### Repository boundary

```text
external information
        ↓
repository observation
        ↓
controlled model / records
        ↓
repository-driven action or release record
```

## 5. Design implication

A new requirement must first be classified:

```text
ecosystem concern?
factory concern?
repository/model concern?
```

Do not solve an ecosystem problem by expanding the factory automatically.

## 6. Status

`candidate / integrated working model`
