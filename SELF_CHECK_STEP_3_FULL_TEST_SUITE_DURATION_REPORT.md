# Self-check step 3 — full test suite and duration report

**Status:** `failed_one_regression`

## Summary

- Runner: `pytest` (required because M71.3/M71.4 contain pytest-style function tests).
- Result: **147 passed, 1 failed, 10 subtests passed**.
- Duration: **84.28 seconds**.

## Failure

`RuntimeModeStartFilesStandardTest.test_minimal_prompt_exists_and_does_not_duplicate_protocol` failed because `START_PROMPT_RUNTIME_MODE.md` contains **96 words**, while the active standard allows at most **90**.

## Test-isolation finding

Some CLI workflow tests leave generated `lock_report.json` and `lock_validation_report.json` in the source package `reports/` directory. A strict repository check run immediately afterward therefore fails generated-artifact hygiene until those test artifacts are removed.

## Per-file durations

| Test file | Tests | Failures | Duration, s |
|---|---:|---:|---:|
| `cli/tests/test_cli_workflow.py` | 85 | 1 | 52.890 |
| `cli/tests/test_ci_release_smoke_matrix.py` | 6 | 0 | 17.291 |
| `cli/tests/test_repo_check_clean_integration.py` | 4 | 0 | 6.806 |
| `cli/tests/test_m70_4_production_ci_release_validation.py` | 4 | 0 | 3.208 |
| `cli/tests/test_clean_check_fixtures.py` | 11 | 0 | 2.740 |
| `cli/tests/test_production_repo_hygiene_policy.py` | 4 | 0 | 0.381 |
| `cli/tests/test_language_cli_root_contracts.py` | 4 | 0 | 0.162 |
| `cli/tests/test_ci_clean_gate_workflow.py` | 4 | 0 | 0.155 |
| `cli/tests/test_m71_3_history_event_prompt_registry_migration.py` | 5 | 0 | 0.114 |
| `cli/tests/test_m71_4_runtime_prompt_trace_validation.py` | 6 | 0 | 0.079 |
| `cli/tests/test_m71_2_prompt_registry_schema_profile.py` | 6 | 0 | 0.026 |
| `cli/tests/test_release_clean_gate_provenance_linkage.py` | 5 | 0 | 0.001 |
| `cli/tests/test_release_clean_gate_workflow.py` | 4 | 0 | 0.001 |

## Scope

No product fixes were applied in this step. Generated test artifacts were removed after evidence capture, and strict repository hygiene was rechecked.
