# Noise Testcase — NOISE_TP_001_CLARIFICATION_WITHOUT_SUBMIT

Milestone: `M60.7.5`
Package: `sample.support_triage`
Path: `TP_001`
Noise pattern: `clarification_without_submit`
Branch signature: `N_ISSUE_SUMMARY=* -> N_SEVERITY=high -> G_TRIAGE_COMPLETE`

## Scripted steps

| Step | Node | Input kind | Answer | Expected behavior | Submit expected |
|---:|---|---|---|---|---|
| 0 | `N_ISSUE_SUMMARY` | `clarification_without_submit` | `The user asks for clarification before giving an answer.` | `answer_or_acknowledge_clarification_without_submitting_or_advancing` | `False` |
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
