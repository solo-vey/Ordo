# Start Prompt — Office Opening Ordo RC19 — S04_BACKTRACK_AND_CORRECT

SCENARIO_ID: `S04_BACKTRACK_AND_CORRECT`

# Start Prompt — Office Opening Ordo RC19

Extract the package, enter its root, and read:

- `START_HERE_RUNTIME_MODE.md`
- `scenario_suite/SCENARIO_EXECUTION_CONTRACT.md`
- `scenario_suite/README.md`

An exact `SCENARIO_ID` is mandatory. There is no default scenario. If it is absent or invalid, stop before intake with `SCENARIO_ID_REQUIRED`; never infer `S01_CLEAN_CONTROL`.

Record the selection first:

```bash
python3 tools/select_scenario.py . --scenario S04_BACKTRACK_AND_CORRECT
```

Then run the complete Ordo preflight and execute the selected scenario continuously until `T_COMPLETED` or a formal CLI hard stop.

Never copy files from `scenario_suite/fixtures/baseline_outputs/` into `outputs/`. Generate D1/D2/D3 from the current canonical `runtime/run_state.json` and validate each document before continuing.

Do not return a partial completion result while runtime status is `active`.

Write all user-facing questions, progress messages, explanations, and the final response in Ukrainian. Keep commands, node IDs, gate IDs, filenames, JSON keys, schema IDs, and status values unchanged.
