# Noise Testcase — NOISE_TP_001_INVALID_BRANCH

Milestone: `M60.7.5`
Package: `sample.support_triage`
Path: `TP_001`
Noise pattern: `invalid_branch`
Branch signature: `N_ISSUE_SUMMARY=* -> N_SEVERITY=high -> G_TRIAGE_COMPLETE`

## Scripted steps

| Step | Node | Input kind | Answer | Expected behavior | Submit expected |
|---:|---|---|---|---|---|
| 0 | `N_ISSUE_SUMMARY` | `invalid_branch` | `__INVALID_BRANCH_SENTINEL__` | `reject_invalid_branch_without_advancing_current_node` | `False` |
| 2 | `N_ISSUE_SUMMARY` | `clean_answer` | `sample_answer_for_N_ISSUE_SUMMARY` | `` | `True` |
| 3 | `N_SEVERITY` | `clean_answer` | `high` | `` | `True` |

## Expected outcome

Terminal after recovery: `G_TRIAGE_COMPLETE` / `gate`
Expected outputs: `OUT_TRIAGE_NOTE`

## Readiness

Case artifact ready: `True`
Runtime execution ready: `False`
Scoring ready: `False`
Calibration ready: `False`
