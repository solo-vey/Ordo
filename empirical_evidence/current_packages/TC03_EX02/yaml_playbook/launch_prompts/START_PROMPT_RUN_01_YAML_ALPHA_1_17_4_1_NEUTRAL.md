You are executing RUN_01 of the Ordo Database Change YAML Full-Fidelity package Alpha 1.17.4.1.

RUN_ID = RUN_01

INPUT PACKAGE
ORDO_YAML_FULL_FIDELITY_ALPHA_1_17_4_1_RUN_01_JIRA_DELIVERY_QUALITY_PATCH_REISSUE.zip

MANDATORY PRE-FLIGHT
1. Verify every entry in SHA256SUMS.txt.
2. Run exactly: `bash scripts/run_full_release_validation.sh`.
3. Do not independently execute validators marked `not_applicable_release_identity_validators` in `validation/REGRESSION_APPLICABILITY.json`.
4. Stop with NO_CHANGE on any failure from the exact release command.

RUN_01 EXECUTION
1. Execute the canonical 126-step playbook from T001.
2. Generate all route-authorized artifacts.
3. For Jira, use `prompts/hp.artifact.jira.generate_and_review.v6.md` and `contracts/JIRA_RUN_01_DELIVERY_QUALITY_CONTRACT_V5.yaml`.
4. Separate product implementation, verification, and evidence/package requirements.
5. Do not invent repository/module/class/function bindings. Use explicit discovery closure when unresolved.
6. Enforce complete and semantically aligned DEL ↔ AC traceability.
7. Reload authoritative selected-run facts before Jira generation and every regeneration.
8. Validate generated Jira with: `python3 validation/validate_jira_run_01_delivery_quality_v5.py . <JIRA_PATH>`.
9. Approval is forbidden on Jira validation failure or authoritative fact drift.
10. Preserve exact process evidence, but do not self-score.
11. Emit concise progress lines: `Крок <ID> — <суть> — <статус>`.

EXPECTED SUCCESS TERMINAL
T_COMPLETED / GO

Respond in Ukrainian.
