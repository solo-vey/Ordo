# RUN-07 Action-family mismatch review

**Decision:** the eight action mismatches are not classification failures.

- 7 are definite alias-normalization gaps.
- 1 is an alias gap plus safety mutation-policy ambiguity.
- Classification errors: 0.
- Protected-state violations: 0.

## Cases
- `CSG-BACKTRACK-01` — `alias_gap`: “Return workflow to alias step” clearly preserves backtrack intent.
- `CSG-PAUSE-02` — `alias_gap`: “Temporarily suspend workflow” is a pause synonym not covered by current tokens.
- `CSG-META-01` — `alias_gap`: “Report current workflow step” is a process-meta response.
- `CSG-META-02` — `alias_gap`: “Explain the next process step” is a process-meta response.
- `CSG-UNRELATED-01` — `alias_gap`: “Handle separately without advancing workflow” correctly redirects/isolates the side request.
- `CSG-UNRELATED-02` — `alias_gap`: Same semantic action as the previous unrelated-topic case.
- `CSG-SAFETY-02` — `alias_gap_plus_policy_ambiguity`: Urgent medical help is a safety bypass, but mutation semantics are ambiguous.
- `CSG-UNKNOWN-01` — `alias_gap`: Requesting a specific unambiguous answer is classification clarification.

## Separate policy problem

`state_mutation_performed` does not distinguish control-state suspension from business/protected-state mutation.
Add `mutation_scope`, allow safety control suspension, and make unauthorized business/protected mutation a hard gate.
