# Office Opening Disturbance Scenario Suite

This suite tests control-flow quality rather than document prose alone. It covers alternative branches, loops, rejected inputs, rollback/correction, and incomplete runs.

Run the internal regression suite with:

```bash
python3 tools/run_disturbance_suite.py .
```

The runner creates isolated temporary copies and never mutates the package under test. Results are written to `reports/DISTURBANCE_SCENARIO_SUITE_REPORT.json`.


## External single-scenario execution

Read `SCENARIO_EXECUTION_CONTRACT.md`. An explicit `SCENARIO_ID` is mandatory; no default scenario exists. Baseline output fixtures are internal regression references and must never be copied into external run outputs.
