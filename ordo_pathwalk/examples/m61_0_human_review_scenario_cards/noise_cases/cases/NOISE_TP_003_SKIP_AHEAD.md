# Noise Testcase — NOISE_TP_003_SKIP_AHEAD

Milestone: `M60.7.5`
Package: `sample.support_triage`
Path: `TP_003`
Noise pattern: `skip_ahead`
Branch signature: `N_ISSUE_SUMMARY=* -> N_SEVERITY=medium -> G_TRIAGE_COMPLETE`

## Scripted steps

| Step | Node | Input kind | Answer | Expected behavior | Submit expected |
|---:|---|---|---|---|---|
| 0 | `N_ISSUE_SUMMARY` | `skip_ahead` | `medium` | `do_not_skip_required_current_node_or_advance_out_of_order` | `False` |
| 2 | `N_ISSUE_SUMMARY` | `clean_answer` | `sample_answer_for_N_ISSUE_SUMMARY` | `` | `True` |
| 3 | `N_SEVERITY` | `clean_answer` | `medium` | `` | `True` |

## Expected outcome

Terminal after recovery: `G_TRIAGE_COMPLETE` / `gate`
Expected outputs: `OUT_TRIAGE_NOTE`

## Readiness

Case artifact ready: `True`
Runtime execution ready: `False`
Scoring ready: `False`
Calibration ready: `False`
