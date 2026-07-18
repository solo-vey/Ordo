# M64.0 LIP Classification Matrix

Status: `accepted-as-planning-classification`

M64.0 does not change runtime core, does not add opcodes, and does not implement IR-level flow joins.

| LIP | Priority | Initial home | M64.0 decision | Target | Notes |
|---|---:|---|---|---|---|
| LIP-01 — Program-level contract layer | P0 | schema convention + package authoring standard | Accept first wave | M64.1 | Do not promote to opcode; define top-level contract schema and review block first. |
| LIP-02 — Interaction model | P0 | schema convention + validation/lint candidate | Accept first wave | M64.2 | Document human/AI/CLI ownership and raw-tool-output policy. |
| LIP-03 — Process rail definition | P0 | process model convention | Accept first wave | M64.2 | Policy layer for deviation/resume/backtracking; no deterministic classifier yet. |
| LIP-04 — Conversation semantics | P0 | schema convention + runtime/lint candidate later | Accept as policy contract | M64.2 | Allowed input classes and routing policies; not a full NL classifier. |
| LIP-05 — Hybrid execution model | P0 | package standard + runtime profile convention | Accept first wave | M64.2 | Clarifies AI driver / CLI validator / human reviewer boundary. |
| LIP-06 — Program-level approval gate | P0 | gate standard / lint candidate | Accept as lint/profile design | M64.3 | Implement as documented gate and validation profile before compiler/IR semantics. |
| LIP-07 — Package profile and startup gates | P1 | package standard | Defer after first wave | M64.4 | Generalize compile/start-prompt/README startup gates. |
| LIP-08 — Derived artifact synchronization | P1 | package validation standard | Defer after first wave | M64.5 | Use warning/error modes; avoid making every stale doc a blocker. |
| LIP-09 — SVG graph artifact standard | P1 | companion utility/package artifact standard | Defer after first wave | M64.6 | Promote provenance/manifest standard only, not renderer implementation. |
| LIP-10 — Delta backlog convention | P1 | release discipline/package standard | Accept as backlog discipline | M64.4 or M64.5 | Preserve cross-chat improvement prompts with structured metadata. |
| LIP-11 — FLOW.JOIN / SHARED.TAIL.REFERENCE | P2 | future IR design candidate | Design spike only | M64.8 or M65 | Do not implement quickly; affects graph/IR/compiler/path enumeration/rendering. |
| LIP-12 — Real-module testcase generation mode | P2 | companion utility/testing standard | Defer | M64.7 or M65 | Artifact generation is useful; runtime execution/scoring remains out of scope. |
| LIP-13 — Two-tier rendering model for output templates | P1 | language/rendering docs + renderer capability standard | Docs hardening | M64.4+ | Already partially present; improve guide and validation expectations, not new core runtime. |
| LIP-14 — Attribute/value schema documentation standard | P1 | language book + schema docs | Accept as documentation standard | M64.4+ | Every YAML field needs meaning/type/enum values/compiler behavior/validation behavior. |
| LIP-15 — Visual graph annotation/highlight standard | P2 | graph utility feature standard | Defer | M64.6+ | Useful companion utility extension; not language core. |

## First-wave recommendation

```text
M64.1 — Program-level contract schema convention
M64.2 — Interaction model + process rail + conversation semantics docs
M64.3 — Program-level approval gate lint/profile design
```

## Explicit non-promotion decisions

```text
FLOW.JOIN = future IR design candidate; not implemented in M64.0
SHARED.TAIL.REFERENCE = future IR design candidate; not implemented in M64.0
CONVERSATION.SEMANTICS = policy/schema contract; not deterministic NL classifier
Real-module testcase generation = companion utility/test artifact standard; no runtime scoring/calibration
```