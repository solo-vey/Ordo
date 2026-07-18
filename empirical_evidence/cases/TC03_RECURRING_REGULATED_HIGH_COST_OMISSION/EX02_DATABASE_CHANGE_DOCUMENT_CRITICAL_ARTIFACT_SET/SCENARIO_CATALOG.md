# Five-scenario catalog

| Run | Scenario | Expected terminal behavior |
|---|---|---|
| RUN_01 | Clean control | Complete the analytical package |
| RUN_02 | Branch heavy | Complete with normalization/no-op/duplicate branches |
| RUN_03 | Invalid and irrelevant | `T_SCENARIO_EXHAUSTED`, no canonical package |
| RUN_04 | Backtrack and correct | Invalidate stale artifacts, regenerate and reapprove |
| RUN_05 | Incomplete hard stop | `T_INPUT_BLOCKED`, no invented mandatory facts |

The same five semantic scenarios are used across all four implementation conditions.
