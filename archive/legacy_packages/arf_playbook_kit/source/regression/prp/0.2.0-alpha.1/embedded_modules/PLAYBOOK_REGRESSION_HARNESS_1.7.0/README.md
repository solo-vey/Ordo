# Playbook Regression Harness 1.7.0
## Unified Execution Modes

This version integrates chat-native testing and provider API testing into one regression workflow.

The workflow is:

1. Load baseline and candidate playbook packages.
2. Run canonicalization and static/deterministic regression checks.
3. Produce the deterministic regression report.
4. Ask which behavioral execution mode to use:
   - `provider_api`
   - `chat_native`
   - `skip_behavioral`
5. Generate a self-contained execution package for the selected mode.
6. Execute the behavioral pilot in another environment/chat.
7. Import result packages.
8. Run differential, stability, semantic, and promotion layers.

The mode-specific packages are generated from the same canonical scenarios and policies.


## New in 1.6.0 — Semantic Projection & Specification Diff v1

After static evaluation and before behavioral execution, PRH independently extracts and compares Behavioral Specification, Decision Table, and Invariant Catalogue. Every proposition requires source evidence. Mandatory weakening or removal is blocking.


## New in 1.7.0 — Negative-Test and Provenance Hardening

- expected violations declared for PRH-DYN-002, PRH-DYN-003 and PRH-DYN-005;
- Stability Analyzer v1.2 with fixture-aware negative-test semantics;
- `expected_violation_missing`, `unexpected_violation` and `unexpected_success`;
- release metadata consistency evaluator;
- checksum-domain and manifest-drift evaluator;
- regression tests for all new rules.
