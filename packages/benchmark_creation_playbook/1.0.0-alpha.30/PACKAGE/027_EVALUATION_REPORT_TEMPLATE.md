# 027. Evaluation Report Template

**Version:** 0.8.0  
**Backlog:** BL-BENCH-027  
**Status:** implemented

## Required report fields

- evaluation ID and timestamp;
- artifact identity and checksum;
- artifact type;
- active contract ID/version;
- evaluator identity/mode;
- focused-scope record;
- criterion-level raw scores and evidence;
- findings and severities;
- confirmed cap records;
- raw score, final score and readiness;
- uncertainty and unavailable evidence;
- supersedes/superseded-by references.

## Criterion record

```text
criterion_id
weight
score_awarded
status: passed | partial | failed | not_applicable | blocked
artifact_evidence
finding
severity
confidence
```

## Score rule

The raw weighted score is calculated before caps. The final score is the minimum of the raw score and all confirmed cap maxima. Not-applicable criteria must follow the active contract's normalization rule and cannot be removed informally.

## Handoff status

Allowed statuses:

- `evaluated`;
- `evaluated-with-notes`;
- `blocked-evidence`;
- `invalid-contract-binding`;
- `superseded`.
