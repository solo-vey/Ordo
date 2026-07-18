# Evaluation Methodology — TC03 / EX02

**Profile ID:** TC03-EX02-EVAL-v1.1  
**General methodology:** `../../../EVALUATION_METHODOLOGY.md`  
**Test case:** `TC03_RECURRING_REGULATED_HIGH_COST_OMISSION / EX02_DATABASE_CHANGE_DOCUMENT_CRITICAL_ARTIFACT_SET`

## 1. Scope

This test case evaluates whether a playbook can produce or correctly withhold a critical database-change artifact set under regulated, high-cost-of-omission conditions. Evaluation prioritizes literal fidelity, deterministic evidence, correction behavior, rollback safety, deduplication semantics, and prohibition on invented facts.

The normal business artifact set is:

1. Passport.
2. Jira task.
3. Manual QA package.
4. Automation package.

The Implementation Prompt is reviewed when present but is excluded from the Documents average.

## 2. RUN applicability matrix

| RUN | Scenario role | Expected outcome class | Documents mode |
|---|---|---|---|
| **RUN_01** | clean positive control | complete artifact set and successful completion | document-producing |
| **RUN_02** | no-change/not-ready branch | no business artifact set; complete no-change evidence | **N/A**; Final = Process |
| **RUN_03** | scenario exhaustion | precise exhaustion decision without invented artifacts | terminal-deliverable |
| **RUN_04** | correction/backtrack branch | corrected and regenerated complete artifact set | document-producing |
| **RUN_05** | authoritative input blocker | precise blocked decision without invented artifacts | terminal-deliverable |

The mode above is fixed before evaluating any implementation.

## 3. Process evaluation requirements

Process is a **playbook-pure** score. It measures whether the playbook defines and supports the correct execution route. It does not score the quality of the result-packaging layer or mistakes made by the analyst/Driver that executes the playbook.

A high Process score requires evidence that the playbook itself:

- defines preservation of authoritative input literals;
- selects or makes available the correct branch for the RUN;
- defines all required gates in the correct order;
- defines validation before approval;
- routes fixable defects through the owning generation step;
- defines invalidation and regeneration of dependent artifacts after correction;
- permits hard stop only for a valid blocker, exhausted scenario, or exhausted correction budget;
- defines consistent terminal-state requirements.

The following are excluded from Process and Final:

- archive structure, filenames, package-wide checksum coverage, command-log export, and other result-packaging defects;
- alias gaps, incorrect fact recall, contradictory responses, accidental substitutions, and other analyst/Driver execution errors not caused by the playbook definition.

Those excluded dimensions may be retained as separate diagnostic observations. `126/126 PASS`, a parity report, or a successful regression harness does not by itself prove correct execution design.

## 4. Artifact scoring rules

### 4.1 Passport

Must capture the database-change contract, exact field path, old/new values, operation, identifiers, timestamp, event, normalization, deduplication, expected counts, assumptions, provenance, and affected artifacts. A path typo or altered literal is material.

### 4.2 Jira task

Acceptance criteria must be independently verifiable. Delivery rows must identify an action, target, measurable output, and evidence. The Jira task must remain consistent with the Passport and test fixtures.

### 4.3 Manual QA

Each case must be locally executable and contain setup, exact action, exact assertions, evidence, and safe rollback. Rollback must restore the same state that the test changes and prove restoration. Missing complete local assertions caps the score at **50**.

### 4.4 Automation

Tests must map exactly to requirements and Manual QA cases, include a per-test runner or equivalent executable unit, exact fixtures, expected assertions, cleanup/rollback, and evidence of no unintended side effects. Missing per-test execution or exact correspondence caps the score at **50**.

## 5. Cross-artifact invariants

Where present in the authoritative RUN input, these literals must remain identical across all artifacts and evidence:

- collection/table name;
- document and record identifiers;
- field path;
- old and new values;
- operation type;
- change identifier;
- timestamp;
- event name;
- normalization rule;
- deduplication key;
- expected change/event/error counts.

No artifact may silently add trailing punctuation to a field path, change case, trim values when not authorized, substitute identifiers, or reuse a deduplication identifier in a way that invalidates rollback or repeated execution.

## 6. RUN-specific rules

### RUN_01

Expected to traverse the full successful generation path. Documents are scored as the equal average of Passport, Jira, Manual QA, and Automation. A terminal `go` is invalid if material document defects remain or validators inspected different files.

### RUN_02

Expected to exercise the no-change/not-ready branch. No business-document score is assigned. Process is judged on correct branch selection, exact no-change evidence, consistent status, and absence of invented artifacts. Final equals Process.

### RUN_03

Expected to terminate as scenario exhausted when authoritative identifiers or field facts are insufficient. Documents scores the terminal evidence package and correct non-production, not missing business artifacts. Inventing data is a critical failure.

### RUN_04

Expected to exercise correction/backtrack. Full credit requires correction receipts, return to the correct owner, dependent invalidation, regeneration, revalidation, and updated approvals. Manually patching only one artifact while leaving dependents stale is a major process defect.

### RUN_05

Expected to terminate blocked because required authoritative inputs are missing. Documents scores the blocker package and correct non-production. The blocker must name exactly what is missing and what evidence would close it.

## 7. Score calculation

- Document-producing RUNs: `Documents = mean(Passport, Jira, Manual QA, Automation)`.
- RUN_02: `Documents = N/A`; `Final = Process`.
- RUN_03 and RUN_05: Documents is the terminal-deliverable conformance score.
- Otherwise: `Final = conventional rounding((Process + Documents) / 2)`.

## 8. Acceptance and storage

Scores are provisional until explicitly accepted by the user. Accepted values must be stored in the implementation's `ACCEPTED_SCORECARD.md` and `ACCEPTED_SCORECARD.json`. Dry self-checks and rejected external runs must not overwrite accepted scorecards.

The evaluator should preserve the evaluated archive, its SHA-256, the scoring rationale, and the methodology/profile versions used. Accepted scores under v1.1 supersede earlier scores that included packaging or analyst/Driver defects in Process.

## Executor–Evaluator Provenance

For all 20 currently accepted results, execution and evaluation are recorded as `different_chat_same_model`: both used `GPT-5.6 Thinking`, but in different chats. This is based on user attestation and returned archive transfer; it is not cryptographically verified.
