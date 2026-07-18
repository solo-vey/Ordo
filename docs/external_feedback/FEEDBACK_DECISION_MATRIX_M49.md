# M49 Feedback Decision Matrix

| Severity | Meaning | Default action |
|---|---|---|
| blocker | Breaks CI, release integrity, or core trust claim | Must fix before release |
| high | Core behavior or validation guarantee is incomplete or misleading | Fix in next milestone unless scope is too large |
| medium | Important UX, docs, or consistency issue | Schedule if aligned with release scope |
| low | Cleanup, wording, small maintainability issue | Batch with nearby work |
| question | Needs clarification or reviewer assumption may be wrong | Ask for evidence or decide no action |

## Decision meanings

| Decision | Meaning |
|---|---|
| accepted | Fix as requested |
| accepted_with_scope_limit | Fix the core issue, not the whole suggested expansion |
| needs_more_evidence | Do not change yet; request reproduction or example |
| deferred | Valid but not required for this preview release |
| rejected | Not aligned with current product/language direction |
| not_applicable | Feedback does not apply to the current package state |
