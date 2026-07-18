# Clean Path Testcase — CLEAN_TP_001

Milestone: `M60.7.3`
Package: `sample.support_triage`
Path: `TP_001`
Noise pattern: `none`
Branch signature: `N_ISSUE_SUMMARY=* -> N_SEVERITY=high -> G_TRIAGE_COMPLETE`

## Answer steps

| Step | Node | Answer | To |
|---:|---|---|---|
| 1 | `N_ISSUE_SUMMARY` | `sample_answer_for_N_ISSUE_SUMMARY` | `N_SEVERITY` / `node` |
| 2 | `N_SEVERITY` | `high` | `G_TRIAGE_COMPLETE` / `gate` |

## Expected outcome

Terminal: `G_TRIAGE_COMPLETE` / `gate`
Expected outputs: `OUT_TRIAGE_NOTE`
Expected state updates: `issue_summary`, `owner_team`, `severity`

## Readiness

Case artifact ready: `True`
Runtime execution ready: `False`
Noise generation ready: `False`
