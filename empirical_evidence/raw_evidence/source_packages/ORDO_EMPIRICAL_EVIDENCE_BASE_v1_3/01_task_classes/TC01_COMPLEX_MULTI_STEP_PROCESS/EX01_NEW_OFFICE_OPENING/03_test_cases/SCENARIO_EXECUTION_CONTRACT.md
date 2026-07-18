# Scenario Selection and Artifact Generation Contract

## Mandatory explicit scenario

Every external single-scenario run MUST declare exactly one `SCENARIO_ID` from:

- `S01_CLEAN_CONTROL`
- `S02_BRANCH_HEAVY`
- `S03_INVALID_AND_IRRELEVANT`
- `S04_BACKTRACK_AND_CORRECT`
- `S05_INCOMPLETE_HARD_STOP`

There is no default scenario. If `SCENARIO_ID` is missing, unknown, or ambiguous, stop before runtime intake and create a diagnostic result with reason code `SCENARIO_ID_REQUIRED`. Never infer or silently select `S01_CLEAN_CONTROL`.

Before preflight, run:

```bash
python3 tools/select_scenario.py . --scenario <SCENARIO_ID>
```

This creates `runtime/selected_scenario.json`. Runtime evidence and the final result package must include this file.

## Baseline fixtures are not runtime outputs

Files under `scenario_suite/fixtures/baseline_outputs/` are internal regression references only. They MUST NOT be copied into `outputs/` during an external model execution.

At `N11D`, `N17D`, and `N20D`, generate documents from the current canonical `runtime/run_state.json`, the current route, and the declared templates/contracts. After each document node, validate the newly created document against canonical state before continuing.

If a generated document conflicts with canonical state, do not proceed to later document nodes. Correct/regenerate the document or return a formal diagnostic hard stop.
