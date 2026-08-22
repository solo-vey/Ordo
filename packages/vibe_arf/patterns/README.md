# Reusable Data+Execution Pattern Library

Canonical reusable components are selected during **Data Layer authoring**, not during tree synthesis. Each pattern owns a small Data Layer interface template plus an execution projection template. A project persists pattern instances and bindings in `authoring/pattern_instance_catalog.yaml`; the tree is derived from those instances and must not independently re-select a pattern.

## Advanced reusable process-semantic patterns (Change 9 candidate)

The library also contains four compiler-hardened generic patterns:

- `DOCUMENT_RECONCILIATION_VERIFICATION` v1.2
- `VERIFIED_DOCUMENT_JIRA_TASK_MATERIALIZATION` v1.1
- `VERIFIED_DOCUMENT_CODE_IMPLEMENTATION` v1.2
- `EXECUTION_DEBUG_EVIDENCE_EXPORT` v1.1

For these patterns, `outcome_edges` are canonical semantics, not editor routing syntax. Target playbooks must lower them using the pattern `COMPILATION_CONTRACT.md` and `source/reusable-pattern-compiler-lowering-policy.json`, preserving exact outcome tokens and failing closed on invalid discriminators. Domain facts and host/runtime bindings remain outside generic pattern core.

## SIMPLE alternative patterns (Change 10 candidate)

The library additionally contains two intentionally simplified alternatives that **coexist** with their advanced family members:

- `SIMPLE_DOCUMENT_RECONCILIATION_VERIFICATION` v1.1 — lightweight evidence-grounded reconciliation with one selected domain profile, analyst-only unresolved decisions, targeted mutation, and repeat-until-clean loop.
- `SIMPLE_VERIFIED_DOCUMENT_CODE_IMPLEMENTATION` v1.0 — lightweight one-shot implementation prompt, exact `LOCAL_SAFE` / `HANDOFF_REQUIRED` scope gate, bounded implementation+verification, and no advanced planning/recovery tree.

When both SIMPLE and advanced members of the same variant family match, selection is explicit; discovery must not silently choose, upgrade, downgrade, or merge the variants.
