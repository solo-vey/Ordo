# PROMPT: PRH Chat-Native Multi-Chat Execution

Switch this conversation to `PRH chat_native` mode.

The chat must have access to the baseline playbook, candidate playbook, PRH scenario fixtures (or their transfer package), and campaign configuration.

1. Read `README.md`, `CHAT_NATIVE_POLICY.yaml`, and the campaign YAML.
2. Record `campaign_id`, a unique `chat_id`, the user-declared UI model in `declared_model_label`, `model_label_verified_by_provider: false`, and `evidence_mode: chat_native`.
3. Execute only the scenarios and repeats assigned to this chat.
4. Execute baseline and candidate separately for every scenario.
5. Start every repeat from the fixture again with a clean run envelope.
6. Never reuse a previous repeat as the next response.
7. Never invent API request IDs, provider provenance, exact token usage, or hidden model parameters.
8. For each run create a run manifest, raw response, normalized trace, and dynamic property evaluation.
9. Mark context-contamination risk as `low`, `medium`, `high`, or `unknown`.
10. At completion, create `PRH_CHAT_NATIVE_PARTIAL_RESULTS_<chat_id>.zip`.
11. Do not issue a cross-chat promotion verdict when this chat executes only part of the campaign.
12. Report planned and completed runs, skipped or failed runs, declared model, execution mode, and the ZIP SHA-256.

Proceed without additional confirmation. If context approaches its limit, create a continuation manifest and a ZIP containing completed runs.
