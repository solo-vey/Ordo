# A0 Decisions and Next-Patch Boundaries

Status: `proposed-for-human-confirmation`

## Proposed A0 decisions

### A0-D01 — Adaptation is compatibility alignment, not APF redesign

Preserve all confirmed rc.7–rc.12 APF methodology and gates unless a concrete v0.12 incompatibility requires a scoped change.

### A0-D02 — Use capability-status labels

Every APF claim must distinguish `runtime-enforced`, `schema-supported`, `accepted-convention`, `package-local`, `documented-only`, `deferred`, `unsupported` and `audit-required`.

### A0-D03 — Program-level and conversational contracts are mandatory adaptation work

Program metadata, interaction model, process rail and conversation semantics are required for adaptation even where Ordo treats them as accepted source conventions rather than runtime opcodes.

### A0-D04 — Prompt Registry is a separate patch line

Do not mix prompt migration with process-rail changes. Prompt IDs must be semantic and stable, not aliases of node IDs.

### A0-D05 — Runtime claims require evidence

Do not claim replay, snapshots, diffs, restore or generalized prompt trace support until A6 confirms schema, CLI, runtime enforcement, tests and APF package use.

### A0-D06 — Deferred backlog remains closed

`BL-APF-001` and `BL-APF-002` stay `deferred-pending-new-language-package-adaptation`. A0 does not start implementation or decide their order.

## Next patch boundaries

### A1 — Program contract and metadata alignment

May change:
- APF top-level metadata/source schema;
- compatibility declarations;
- required program-contract review artifact/gate.

Must not change:
- authoring branches;
- concrete intake methodology;
- prompt content;
- runtime core.

### A2 — Interaction model, process rail and conversation semantics

May change:
- role/authority declarations;
- deviation/resume/backtrack policy;
- state invalidation/reconfirmation policy;
- input-class handling contract.

Must preserve:
- rc.8 confirmation requirements;
- rc.11 startup gate;
- rc.12 intake gate;
- human content and release authority.

### A3 — Prompt Registry migration

May change:
- prompt catalog, IDs, refs, manifests and validation;
- prompt packaging and evidence format.

Must not change:
- deterministic routing;
- node/gate authority;
- confirmed state without the node contract.

### A4 — IR, state and checkpoint alignment

May change:
- explicit state/checkpoint mappings;
- freshness and invalidation checks;
- next-step contract.

Must not introduce:
- prompt-driven routing;
- Markdown as source of truth;
- new core opcodes.

### A5 — Validation and release hygiene

May change:
- APF validation profile;
- package-type separation;
- APF-local release checks.

Must not:
- fail APF because a non-promoted parent CLI command is absent;
- fabricate historical evidence.

### A6 — Real capability audit

Evidence-only milestone for replay, snapshots, diffs, restore, trace and backtracking. No backlog implementation is authorized.

### A7 — Regression and release candidate

Allowed only after A1–A6 and explicit human confirmation. Release number is not decided by A0.

## Recommended immediate next step

Proceed to `A1 — Program contract and metadata alignment` after confirming A0 decisions and matrix.
