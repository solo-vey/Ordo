# BL-BENCH-049 — Canonical Evaluation Methodology and Test-Case-Specific Evaluation Profiles

## Status

`OPEN`

## Problem

The benchmark evidence package currently stores playbooks, test inputs, run outputs, audits and scores, but the methodology used to derive those scores is not guaranteed to be present as an explicit, versioned source of truth. This makes the evidence package less reproducible: another evaluator may see the scores without being able to reconstruct exactly how Process Quality, Document Quality and Final Quality were determined.

A single universal methodology is also insufficient by itself. Individual test cases may require additional scoring rules, caps, expected terminal states, artifact weights, scenario-specific blocking rules or clarifications. Those differences must be explicit and must not silently replace the general methodology.

## Goal

Introduce a two-level evaluation-methodology model:

1. a canonical general methodology stored at the root of every benchmark evidence package;
2. a mandatory test-case-specific evaluation profile stored inside every test-case directory.

The test-case profile inherits the general methodology and may add or override only explicitly permitted fields. Every run audit and score must identify the exact methodology versions used.

## Required artifacts

### Root-level canonical methodology

The evidence package root must contain, at minimum:

```text
EVALUATION_METHODOLOGY.md
EVALUATION_METHODOLOGY.json
```

The methodology must define:

- evaluation purpose and scope;
- evaluator independence and evidence requirements;
- Process Quality criteria;
- Document Quality criteria;
- Final Quality formula;
- rounding rules;
- artifact weighting;
- failure caps and zero-tolerance defects;
- treatment of blocked and hard-stop terminal states;
- distinction between validator PASS and actual quality;
- requirements for audit evidence and provenance;
- score reproducibility requirements;
- methodology versioning and change control.

### Test-case-specific profile

Each test case must contain:

```text
EVALUATION_PROFILE.md
EVALUATION_PROFILE.json
```

The profile must declare:

- inherited root methodology ID and version;
- test-case ID and version;
- expected terminal states per run;
- test-specific process criteria;
- test-specific document criteria;
- artifact set and weights;
- additional caps or blocking defects;
- authoritative inputs used during evaluation;
- allowed overrides with rationale;
- effective methodology fingerprint.

## Inheritance and override contract

The test-case profile must inherit the root methodology by default.

Overrides are allowed only when:

- the overridden field is explicitly marked overrideable;
- the profile provides a rationale;
- the change is machine-readable;
- the effective methodology remains internally consistent;
- the override does not silently weaken a mandatory root-level safety or evidence rule.

Missing, stale, incompatible or undeclared methodology/profile references must fail closed.

## Evaluation binding

Every run audit and score ledger record must include:

```json
{
  "evaluation_methodology_id": "...",
  "evaluation_methodology_version": "...",
  "test_case_evaluation_profile_id": "...",
  "test_case_evaluation_profile_version": "...",
  "effective_methodology_sha256": "..."
}
```

A score is noncanonical when this binding is absent or cannot be reproduced.

## Required process gate

Add a mandatory `EVALUATION_METHODOLOGY_BINDING_GATE` before evaluation and before canonical evidence acceptance.

The gate must verify:

1. root methodology files exist and agree;
2. test-case profile files exist and agree;
3. inheritance and overrides are valid;
4. effective methodology can be deterministically compiled;
5. run audit uses the compiled methodology version;
6. score formulas and caps match the effective methodology;
7. the methodology fingerprint is stored in the audit and ledger.

On failure:

```text
BLOCKED_MISSING_OR_INVALID_EVALUATION_METHODOLOGY
```

The run may be audited as working evidence, but it must not enter the canonical score ledger or comparative scoreboard.

## Package-template changes

Update the canonical evidence structure so that it includes:

```text
benchmark_evidence_base/
├── EVALUATION_METHODOLOGY.md
├── EVALUATION_METHODOLOGY.json
└── task_classes/
    └── <TASK_CLASS>/
        └── <TEST_CASE>/
            ├── EVALUATION_PROFILE.md
            └── EVALUATION_PROFILE.json
```

Update the test-case creation flow to create the profile before any runs are accepted.

## Acceptance criteria

1. A package without the root methodology is rejected.
2. A test case without its evaluation profile is rejected.
3. An undeclared or weakening override is rejected.
4. A valid inherited profile compiles to a deterministic effective methodology.
5. Every run audit stores the exact methodology/profile versions and SHA-256.
6. Re-evaluating the same evidence with the same effective methodology produces the same scores.
7. Comparative tables contain only methodology-bound canonical scores.
8. Methodology changes create a new version and do not silently rewrite historical scores.
9. Documentation clearly distinguishes general methodology from test-specific clarifications.
10. Positive and negative acceptance fixtures are included.

## Definition of done

- root methodology templates implemented;
- test-case evaluation profile templates implemented;
- JSON schemas implemented;
- deterministic methodology compiler implemented;
- binding validator and fail-closed gate implemented;
- evidence package and test-case templates updated;
- audit report and score ledger schemas updated;
- migration guidance for existing test cases added;
- acceptance tests pass;
- backlog, README, changelog, manifests and checksums updated.


## Implementation closure

Implemented in alpha.17: root methodology, JSON contract, mandatory profile templates, effective-methodology compiler, audit binding validator, sample migration, fail-closed acceptance tests and release evidence.
