# EX02 — Database Change Document-Critical Artifact Set

This test-case directory is the canonical evidence location for the four compared playbook representations:

- YAML Playbook
- Structured Instructions
- Mixed Accumulated Instructions
- Domain Adapted All-in-One

For each representation, the directory contains the current implementation archive, launch prompts, five accepted run evidence artifacts, individual run evaluations, an aggregate evaluation, and checksums.

Canonical navigation:

1. `06_manifests/CASE_EVIDENCE_INVENTORY.md`
2. `05_comparative_analysis/CURRENT_COMPARATIVE_SCORECARD.md`
3. `02_implementations/`
4. `03_launch_prompts/`
5. `04_runs/`
6. `05_analysis/`
7. `LANGUAGE_POLICY.md`

## Current scoring policy

The authoritative scoring profile is `TC03-EX02-EVAL-v1.1`. Process is playbook-pure: result-packaging defects and analyst/Driver execution errors are excluded. See `03_test_cases/PROCESS_SCORING_POLICY_V1_1.md` and `05_comparative_analysis/CURRENT_COMPARATIVE_SCORECARD.md`.

## Executor–Evaluator Provenance

For all 20 currently accepted results, execution and evaluation are recorded as `different_chat_same_model`: both used `GPT-5.6 Thinking`, but in different chats. This is based on user attestation and returned archive transfer; it is not cryptographically verified.
