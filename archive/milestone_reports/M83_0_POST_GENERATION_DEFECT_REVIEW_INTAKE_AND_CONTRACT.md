# M83.0 — APF Post-Generation Defect Review: Intake and Contract

Status: `contract-defined / implementation-not-yet-accepted`
Backlog: `BL-ORDO-014`
Source rationale: `APF_POST_GENERATION_DEFECT_REVIEW_RATIONALE_UK.md`
Impact level: `L3 — shared APF process, review, confirmation, and trace semantics`

## 1. Decision

APF accepts post-generation defect review as a new mandatory review layer for critical and high-impact artifacts.

The feature is not a replacement for structural validation. It is a separate blocking control whose purpose is to detect externally false, unsupported, stale, or cross-artifact-inconsistent claims that may remain internally coherent.

## 2. Core risk

A generated artifact can be:

- syntactically valid;
- structurally complete;
- internally consistent;
- plausible to a domain reader;

and still be operationally unsafe because executable or contract-sensitive values have no authoritative evidence.

The protected property is therefore not only artifact form, but claim provenance and external contract fidelity.

## 3. Applicability and criticality

### 3.1 Critical artifacts

Mandatory full review:

- manual QA and operational runbooks;
- automation specifications;
- implementation prompts that can change production behavior;
- API and data contracts;
- migration, reload, restore, and state-transfer prompts;
- release readiness and rollback reports;
- Jira implementation tasks containing executable contract details;
- operational playbooks and rollback instructions.

### 3.2 High-impact artifacts

Mandatory review, with profile-specific depth:

- package manifests and upgrade instructions;
- configuration instructions;
- test plans with executable payloads;
- cross-artifact contract summaries;
- confirmation records that authorize downstream execution.

### 3.3 Normal descriptive artifacts

The review may be reduced or `not-applicable` only when the artifact contains no executable or contract-sensitive claims. The reason must be recorded.

Criticality may not be lowered merely to bypass a failed gate.

## 4. Canonical process rail

```text
GENERATE_ARTIFACT
→ STRUCTURAL_VALIDATION
→ CONTRACT_EVIDENCE_VALIDATION
→ ADVERSARIAL_DEFECT_REVIEW
→ CROSS_ARTIFACT_REVIEW
→ TARGETED_CORRECTION_IF_REQUIRED
→ POST_CORRECTION_REVIEW
→ CONFIRM_ARTIFACT
```

No critical artifact may enter `CONFIRM_ARTIFACT` directly from structural validation.

## 5. Trust and evidence boundary

Every executable or contract-sensitive value must be classified by evidence source.

Accepted materialization classes:

- `confirmed_user`;
- `canonical_example`;
- `repository_derived`;
- `package_confirmed`;
- `official_schema`.

Non-materializable classes:

- `model_proposed`;
- `unknown`.

A value in a non-materializable class may appear only as an explicit proposal, open question, placeholder, or blocked gap. It must not appear as a final executable instruction.

Names of endpoints, fields, files, commands, or operations are not evidence of their schema or semantics.

## 6. Mandatory defect search

The adversarial review must actively search for:

- plausible but unsupported parameters;
- fields absent from authoritative schemas;
- missing required fields;
- inferred semantics based only on names;
- source-path, delta-path, and REST-path confusion;
- legacy/current contract mixing;
- action/rollback drift;
- hidden assumptions;
- selective use of examples without version reconciliation;
- contradictions with repository, package, user-confirmed, or schema evidence.

Mandatory review question:

> What in this artifact may be externally wrong even though it is internally coherent?

## 7. Cross-artifact boundary

Critical artifacts must be checked against all relevant related views, including when available:

- canonical contract/passport;
- Jira task;
- implementation prompt;
- manual QA;
- automation specification;
- API/data contract;
- rollback contract;
- package manifest;
- confirmed user decisions;
- current repository-derived behavior.

A conflicting related artifact blocks confirmation until reconciled or explicitly superseded.

## 8. Selective reconciliation

When sources conflict, APF must reconcile claim-by-claim rather than copy or reject an entire source.

Priority is not determined by timestamp alone. Reconciliation must preserve:

```text
current confirmed contracts
+ compatible canonical invariants
+ repository or official-schema evidence
→ reconciled artifact
```

Each accepted and rejected claim must retain provenance and reason.

## 9. Targeted invalidation

A defect invalidates the smallest safely identifiable scope.

The review must record:

- sections invalidated;
- sections preserved;
- related assertions requiring recheck;
- regeneration scope;
- unresolved risks.

Whole-artifact invalidation is required only when defect scope cannot be bounded or the source-of-truth relationship is compromised.

Correction does not automatically restore confirmation eligibility.

## 10. Post-correction contract

After any material correction, APF must rerun:

- structural validation;
- contract evidence validation;
- adversarial defect review;
- cross-artifact consistency;
- defect-class regression checks.

The post-correction review must be logically independent from the correction action. A correction operation may not self-attest its own success without validation evidence.

## 11. Confirmation eligibility

For a critical artifact:

```text
structural_validation = passed
contract_evidence_validation = passed
adversarial_defect_review = passed
cross_artifact_review = passed
post_correction_review = passed | not-applicable
blocking_evidence_gaps = 0
```

All conditions are blocking. Automatic confirmation, package approval, or user approval of the process change may not bypass technical fidelity gates.

## 12. Gate set accepted for implementation

- `EVIDENCE-COVERAGE-01`
- `NO-UNSUPPORTED-INFERENCE-01`
- `CANONICAL-CONTRACT-01`
- `CURRENT-VERSION-RECONCILIATION-01`
- `PATH-DOMAIN-01`
- `ROLLBACK-CONTRACT-01`
- `CROSS-ARTIFACT-01`
- `ADVERSARIAL-REVIEW-01`
- `POST-CORRECTION-REVIEW-01`

Allowed gate results:

- `passed`;
- `failed`;
- `not-applicable`.

A blocking defect may not be downgraded to a warning.

## 13. Required review record

M83.1 must define a versioned machine-readable schema containing at minimum:

- artifact identity and version;
- criticality and review profile;
- reviewed sections;
- authoritative sources;
- claim-level provenance;
- defects, assumptions, evidence gaps, and conflicts;
- invalidated and preserved sections;
- corrections and unresolved risks;
- cross-artifact and regression checks;
- gate results;
- confirmation eligibility.

## 14. Execution Trace requirements

The implementation line must support trace events equivalent to:

- `POST_GENERATION_REVIEW_STARTED`;
- `UNSUPPORTED_INFERENCE_DETECTED`;
- `ARTIFACT_SECTION_INVALIDATED`;
- `TARGETED_REGENERATION_COMPLETED`;
- `POST_CORRECTION_REVIEW_PASSED`;
- `ARTIFACT_CONFIRMATION_ELIGIBLE`.

Trace data must not reveal hidden model reasoning. It records evidence, decisions, statuses, and artifact effects only.

## 15. Non-goals

M83 does not claim:

- elimination of all model errors;
- automatic truth discovery without authoritative sources;
- replacement of domain expert or owner approval;
- deterministic semantic verification of arbitrary natural language;
- blanket invalidation of all artifacts after one localized defect;
- permission to expose private chain-of-thought.

## 16. Implementation milestones

### M83.1 — Evidence provenance and review schema

Define source classes, claim-level provenance, versioned review record schema, gate result model, and confirmation eligibility calculation.

### M83.2 — Adversarial and cross-artifact semantics

Define review profiles, defect taxonomy, related-artifact resolution, selective reconciliation, and conflict/supersession behavior.

### M83.3 — Correction and trace semantics

Define targeted invalidation, regeneration scope, post-correction independence, Execution Trace events, and resume/rollback behavior.

### M83.4 — Integration and closure

Integrate with APF process rails, validators, confirmation semantics, documentation, fixtures, negative regressions, and close BL-ORDO-014 only after all gates pass.

## 17. M83.0 acceptance

M83.0 passes only if:

- the improvement is registered in the canonical Markdown and JSON backlog;
- the paused translation state is recorded without unsupported completion claims;
- criticality, evidence classes, process rail, reconciliation, invalidation, post-correction, and confirmation rules are explicit;
- implementation is not falsely claimed;
- M83.1–M83.4 gates are defined.
