# START PLAYBOOK REGRESSION PLAYBOOK

Switch this chat to `PB_PLAYBOOK_REGRESSION` execution mode.

The chat must have access to the baseline playbook package, candidate playbook package, and this PRP package.

1. Verify every package and SHA-256 value.
2. Read `source/program.ordo.yaml` and `contracts/PLAYBOOK_CONTRACT.md`.
3. Execute S1–S3 without intermediate confirmation, including release-metadata and checksum-domain validation:
   - Prepare Regression Pair;
   - Build Comparable Specifications;
   - Run Deterministic Regression.
4. Show the deterministic verdict, semantic specification-diff verdict, blocking findings, and warnings separately.
5. Ask only: `Which behavioral mode should be selected: skip, chat_native, provider_api, or combined?`
6. For `chat_native` or `provider_api`, create a self-contained execution package with both playbook versions and all fixtures, prompts, and scripts.
7. After a results ZIP is returned, execute S5–S6.
8. Never issue production `GO` from chat-native evidence alone.
9. Create the final regression evidence ZIP, backlog, and SHA-256.

Canonical technical artifacts must be written in English. User conversation may remain in the user's language.

10. For negative-test fixtures use PRH Stability Analyzer v1.2:
    - `expected_violation_observed` — positive result;
    - `expected_violation_missing` — blocking failure;
    - `unexpected_violation` — blocking failure;
    - `unexpected_success` — blocking failure.
11. Do not automatically repair metadata or checksum declarations inside tested playbook packages; record the defect and backlog owner instead.
