# Canonical Benchmark Evaluation Methodology

Version: `1.0.0`  
Status: `canonical`  
Scope: every benchmark test case, run audit, score ledger entry and comparative conclusion.

## 1. Purpose

This document defines how result quality is evaluated independently of a Playbook's own self-report. A validator PASS, complete step count or successful terminal response is evidence, but never an automatic score of 100.

## 2. Mandatory evaluation objects

Every run is evaluated against the exact test-case inputs, approved Playbook revision, generated artifacts, execution evidence, validator receipts, Driver state, terminal state and effective evaluation methodology.

A run receives exactly three primary scores:

1. **Process Quality** — correctness of route, gates, transitions, correction loops, approvals, provenance and terminal behavior.
2. **Document Quality** — quality of the canonical generated documents under the test-case document profile.
3. **Final Quality** — ordinary rounded mean of Process Quality and Document Quality.

`Final Quality = round((Process Quality + Document Quality) / 2)`.

## 3. Evidence-first rule

Scores must be derived from inspected files, not from an execution summary alone. Missing evidence is not silently treated as PASS. Claims unsupported by authoritative evidence are defects.

## 4. Process Quality dimensions

The evaluator checks route fidelity, required-step coverage, gate execution, selected-run fact consistency, validation/correction behavior, approval/version binding, terminal-state correctness, no-fabrication behavior, rollback/provenance, package integrity and agreement between state ledger and reports.

Critical process defects may cap or block the score. A process that formally completes while allowing a materially invalid artifact cannot receive full credit.

## 5. Document Quality

The default canonical document set is Passport, Jira, Manual QA and Automation, equally weighted unless the test-case profile explicitly declares another permitted composition. Each document is evaluated against its authoritative template, external validation rules and semantic quality criteria.

## 6. Blocked and negative scenarios

A correct hard stop may receive a high score when the expected terminal state is blocking, authoritative data is genuinely absent, no data is fabricated and sufficient stop evidence is preserved. Absence of generated documents is not a defect when generation is forbidden by the scenario.

## 7. Test-case profiles

Every test case must contain `EVALUATION_PROFILE.md` and `EVALUATION_PROFILE.json`. The profile inherits this methodology and may only:

- identify canonical artifacts and weights;
- bind scenario-specific facts and expected terminals;
- add stricter checks or caps;
- clarify how general dimensions apply locally.

A profile may not remove evidence-first evaluation, change the three-score model, permit unsupported claims, weaken mandatory integrity rules or make validator PASS sufficient by itself.

## 8. Methodology binding

Every audit and score record must store methodology version, root methodology SHA-256, profile version, profile SHA-256 and compiled effective-methodology SHA-256. Historical scores remain bound to their original methodology and are not silently recomputed.

## 9. Acceptance gate

A score is ineligible for the canonical ledger when the root methodology or profile is missing, hashes do not match, forbidden overrides exist, the effective methodology cannot be compiled, or the audit lacks methodology binding.

## 10. Change governance

Methodology changes are versioned. Re-evaluation under a newer methodology creates a new audit revision and explicit comparison; it never overwrites the prior canonical record.
