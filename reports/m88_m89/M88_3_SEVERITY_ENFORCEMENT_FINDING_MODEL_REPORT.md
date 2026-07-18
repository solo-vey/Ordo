# M88.3 — Severity, enforcement and ANTIPATTERN.FINDING model

Status: **passed**

Implemented:

- canonical `ANTIPATTERN.FINDING` schema;
- severity and enforcement policy;
- mandatory `critical → blocking` rule;
- decisions: `allow`, `allow_with_advisory`, `block`, `inconclusive`;
- stable finding IDs;
- source, evidence and timestamp binding;
- finding validation;
- aggregation into `GATE.REPORT`;
- blocking and advisory finding summaries.

Validation: **38/38 tests passed**.
