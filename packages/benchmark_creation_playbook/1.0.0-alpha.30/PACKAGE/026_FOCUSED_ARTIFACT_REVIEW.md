# 026. Focused Artifact Review

**Version:** 0.8.0  
**Backlog:** BL-BENCH-026  
**Status:** implemented

## Mandatory startup gate

Before evaluating a document, the evaluator must record:

1. exact artifact path/name;
2. artifact type;
3. active contract ID and version;
4. final rendered artifact under review;
5. relevant rules included;
6. non-relevant rules explicitly excluded;
7. allowed external references;
8. evaluation evidence sources.

## Review sequence

```text
identify artifact
→ bind contract
→ load only artifact-specific rules
→ inspect final rendered artifact
→ score criteria with evidence
→ confirm failures
→ apply lowest cap
→ issue final report
```

## Blocking conditions

Review is blocked when:

- artifact type is ambiguous;
- no active contract exists;
- evaluator is reviewing an intermediate source instead of the final rendered artifact;
- required referenced Passport/source is unavailable and the contract permits dependency on it;
- criteria from another artifact type are being applied.

## Anti-cross-contamination examples

- Do not require unit-test rows in Jira merely because Automation requires them.
- Do not require Jira to reproduce the full Passport.
- Do not award Manual QA executability points to a contract-only checklist.
- Do not evaluate document content using process-route failure caps.

## Re-evaluation rule

When criteria change, the old score is superseded, not silently overwritten. The new report records the new contract version and the reason for re-evaluation.
