You are executing RUN_02 of the Ordo Database Change YAML Full-Fidelity package Alpha 1.17.1.

RUN_ID = RUN_02

INPUT PACKAGE
ORDO_YAML_FULL_FIDELITY_ALPHA_1_17_1_RUN_02_COMPLETION_PATCH.zip

CANONICAL PROCESS SOURCE
playbook/PLAYBOOK.yaml

MANDATORY PRE-FLIGHT
1. Verify SHA256SUMS.txt; stop with NO_CHANGE on mismatch.
2. Run `python validation/preflight_alpha_1_13_full_fidelity.py .`.
3. Run all available versioned regression scripts in ascending version order.
4. Run `python validation/validate_alpha_1_17_1_run_02_completion.py .`.
5. Stop with NO_CHANGE on any preflight or regression failure.

RUN_02 EXECUTION REQUIREMENTS
1. Execute the canonical 126-step Playbook from T001.
2. Before rendering Passport, satisfy `UNIT_INPUT_COMPLETENESS`.
3. Ask separately for the exact rule identifier, duplicate replay and second-cycle side effects, payload-empty fallback, missing-data and absent-change expectations, and rollback verification.
4. Map unit-validator errors to focused questions, regenerate, and revalidate.
5. Validator failure alone is not a valid terminal reason for this positive route.
6. Continue correction until PASS, authoritative exhaustion, or measured improvement plateau.
7. Never invent unavailable facts, validator PASS, approvals, bindings, or live results.
8. Emit concise progress lines: `Крок <ID> — <коротка суть> — <статус>`.
9. Return only route-authorized artifacts and complete execution evidence.
10. Do not self-score.

EXPECTED SUCCESS TERMINAL
T_COMPLETED / GO

Respond in Ukrainian.
