# Process Scoring Policy v1.1 — Playbook-Pure Execution Quality

**Effective date:** 2026-07-17  
**Status:** accepted for TC03 / EX02

## Decision

The Process score measures the quality of the playbook's own execution path, independently of errors attributable to the result-packaging layer or to the analyst/Driver executing the playbook.

The Process score therefore excludes:

1. **Result-packaging defects** — archive layout, filenames, missing package-wide checksums, incomplete command-log packaging, export-only metadata defects, and other defects introduced after or outside the playbook path.
2. **Analyst/Driver execution defects** — incorrect fact recall, alias gaps, inconsistent Driver responses, accidental analyst substitutions, or other execution-agent errors that are not caused by a defect in the playbook's process definition.

The Process score retains only playbook-owned behavior, including:

- correct branch and route definition;
- required gate ordering;
- availability of correction/backtrack routes;
- dependency and invalidation logic defined by the playbook;
- valid terminal conditions;
- fail-closed and non-invention requirements;
- process completeness and determinism encoded by the playbook.

Document scores are unchanged. Final scores continue to use the existing calculation rules, but with the revised playbook-pure Process score.

Packaging quality and analyst/Driver quality may still be recorded as separate diagnostic dimensions. They must not reduce the accepted Process or Final score for playbook quality.
