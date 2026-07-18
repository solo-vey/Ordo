# 004. Test Case Creation Intake

**Version:** `0.2.0`  
**Status:** accepted working contract

## 1. Entry condition

Start this intake when a Benchmark Owner proposes a new semantic problem to compare across one or more instruction/package variants. Do not design RUN scenarios or compile variants until the test-case intake gate passes.

## 2. Intake sequence

### I01 — Identity and ownership
Capture:
- `suite_id` and version;
- proposed `test_case_id` and version;
- title and owner;
- creation reason and decision reference.

### I02 — Canonical semantic target
Capture:
- user/business goal;
- target analytical behavior;
- what must remain semantically identical across variants;
- explicit non-goals.

### I03 — Task classification
Apply `003_TASK_CLASS_MODEL.md` and record:
- primary class;
- optional secondary classes;
- rationale;
- scoring consequences.

### I04 — Source authority
Capture every allowed source artifact and its role:
- canonical source of truth;
- supporting evidence;
- runtime/operational contracts;
- examples (non-authoritative unless promoted);
- forbidden sources or stale versions.

### I05 — Input and uncertainty model
Capture:
- facts confirmed before execution;
- facts hidden behind Driver interaction;
- facts that may be tentative, corrected, withdrawn, unavailable or irrelevant;
- assumptions policy;
- required identifiers and hard-stop conditions.

### I06 — Expected artifact contract
For each possible terminal route define:
- required canonical artifacts;
- allowed terminal-result artifacts;
- forbidden artifacts;
- artifact-specific contract/version;
- approval requirements.

### I07 — Process claims
Define which process behavior is tested:
- required path or path family;
- state/checkpoint expectations;
- correction/backtrack behavior;
- invalidation/regeneration rules;
- premature finish behavior;
- expected terminal classes.

### I08 — Scenario coverage need
Describe required stress dimensions without yet assigning RUN IDs:
- clean path;
- branch/no-op/negative behavior;
- invalid or irrelevant evidence;
- correction/backtrack;
- incomplete hard stop;
- domain-specific additions.

### I09 — Variant comparability
Capture:
- variants planned for comparison;
- semantic invariants shared by all variants;
- allowed representational differences;
- required Driver family or unresolved Driver selection;
- contamination/isolation risks.

### I10 — Evaluation contract
Capture:
- process evaluation contract/version;
- document contracts by artifact type;
- score aggregation formula;
- failure caps/blockers;
- terminal-route scoring rule;
- explicitly excluded dimensions, including Evidence Capture Quality when applicable.

### I11 — Reproducibility and evidence
Capture:
- required hashes and manifests;
- launch parameters;
- expected returned evidence;
- executor/evaluator independence claims;
- version identity key.

### I12 — Owner confirmation
Present the normalized intake record and obtain:
- `approved`;
- `needs_changes` with exact fields;
- or `blocked` with missing authority/evidence.

## 3. Intake statuses

```text
draft
→ normalized
→ owner_review
→ approved
→ superseded
```

Blocked is a terminal authoring outcome until required authority is supplied.

## 4. Hard gates

The intake cannot become `approved` when any of these is missing:
- test-case identity and owner;
- canonical semantic target;
- exactly one primary Task Class;
- source authority list;
- expected artifact/terminal model;
- process and document evaluation boundaries;
- comparability invariant;
- assumptions/invention policy.

RUN scenario design is forbidden before approval.

## 5. Output

Approved intake produces:
- `test_case/TEST_CASE_CONTRACT.yaml` from the canonical template;
- `test_case/README.md` human-readable summary;
- source registry and manifest;
- explicit open questions/blockers ledger;
- owner approval record.
