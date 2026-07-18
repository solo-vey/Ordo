# 023. Document Quality Contract Registry

**Version:** 0.8.0  
**Backlog:** BL-BENCH-023  
**Status:** implemented

## Purpose

This registry defines which evaluation contract applies to each generated artifact. Document quality is evaluated independently from process quality. A high-quality document cannot repair a failed process route, and a correct process does not guarantee a high-quality document.

## Canonical artifact types

| Artifact type | Contract ID | Primary role | Canonical/derived | Score range |
|---|---|---|---|---|
| Passport | `DQC-PASSPORT-1` | canonical analytical contract | canonical | 0–100 |
| Jira | `DQC-JIRA-1` | delivery and tracking view | derived | 0–100 |
| Implementation Prompt | `DQC-IMPL-PROMPT-1` | implementation handoff | derived | 0–100 |
| Manual QA | `DQC-MANUAL-QA-1` | executable human verification | derived | 0–100 |
| Automation | `DQC-AUTOMATION-1` | runner-oriented verification | derived | 0–100 |

## Contract selection

Before review, the evaluator must identify exactly one artifact type and one active contract version. Cross-applying criteria is prohibited. In particular:

- Jira is not evaluated as a Passport;
- Manual QA is not evaluated as an automation specification;
- Automation is not evaluated as an implementation prompt;
- document score does not include process-route correctness.

## Common evidence rule

Every awarded or deducted point must cite evidence from the final rendered artifact. External references may satisfy a criterion only when the active artifact contract explicitly permits references.

## Common score lifecycle

```text
raw criterion score
  → confirmed artifact findings
  → lowest applicable document cap
  → final artifact score
```

## Registry governance

A contract change requires a version bump when it changes required blocks, scoring weights, caps, or interpretation. Historical evaluations retain the contract version used at evaluation time.
