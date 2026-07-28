# PROMPT: Run Unified PRH Regression from the Beginning

Two versions of the Monitoring Event Playbook are available in this chat:

- `MONITORING_EVENT_PLAYBOOK_V0.3.40_20260727T074431Z.zip` — baseline;
- `MONITORING_EVENT_PLAYBOOK_V0.4.0_FINAL.zip` — candidate.

The `PLAYBOOK_REGRESSION_HARNESS_1.5.0_UNIFIED_EXECUTION_MODES.zip` module is also available.

Run the complete PRH workflow from the beginning.

## Stage 1. Input packages

1. Check the presence and integrity of baseline and candidate.
2. Do not ask the user to upload them again when they are available.
3. Record package identity, versions, and SHA-256 values.

## Stage 2. Deterministic regression

4. Run canonicalization, package inventory comparison, static evaluation, graph/reference integrity, artifact/control integrity, and deterministic scenario-plan validation.
5. Produce a separate deterministic regression report.
6. Never turn an unexecuted check into a positive result.

## Stage 3. Behavioral-mode choice

7. After the deterministic report, stop only for one user choice:

   **Which behavioral testing mode should be prepared?**
   - `provider_api`;
   - `chat_native`;
   - `skip_behavioral`.

8. Do not ask other clarification questions when the data is sufficient.

## Stage 4A. If `provider_api` is selected

9. Create a self-contained `PRH_PROVIDER_API_TEST_PACKAGE.zip` containing both playbook versions, scenario fixtures, provider adapter, live-run configuration, runbook, schemas, scripts, provenance rules, and result-import instructions.
10. Never include API credentials.

## Stage 4B. If `chat_native` is selected

11. Create a self-contained `PRH_CHAT_NATIVE_TEST_PACKAGE.zip` containing both playbook ZIPs, scenario fixtures, `campaign.yaml`, evidence policy, normalized-trace and run-manifest schemas, prompts for a separate execution chat, continuation and merge prompts, and a README.
12. Let the campaign specify the declared model, repeat count, scenarios, and one or more chats.
13. Treat the model name as user-declared UI metadata, not provider provenance.
14. A chat-native package must not promise production `GO`.

## Stage 5. Return results

15. Include a prompt for returning the results ZIP to this chat.
16. After importing results, run differential comparison, stability analysis, semantic judging, and Promotion Policy v2.
17. Keep deterministic, chat-native/provider behavioral, and production-readiness verdicts separate.

## Output

18. Provide the deterministic regression report ZIP, selected execution package ZIP, a separate prompt file for the next chat, and a short description of the mode and its limits.
19. Every ZIP must contain `SHA256SUMS.txt`.
20. Work without further confirmation except for the `provider_api` / `chat_native` / `skip_behavioral` choice.

## Mandatory semantic projection and specification diff

After static evaluation and before the behavioral-mode choice, create a Behavioral Specification, Decision Table, and Invariant Catalogue for both baseline and candidate. Every proposition must map to evidence. Mandatory semantic weakening or disappearance of a mandatory invariant is a blocking regression. Projection disagreement or insufficient evidence is `REVIEW_REQUIRED`. Include the semantic projection report in the deterministic regression package.
