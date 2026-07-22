# Human Review Scenario Card — CARD_013_NOISE_TP_003_INVALID_BRANCH

Milestone: `M61.0`
Case: `NOISE_TP_003_INVALID_BRANCH`
Case type: `noise_path`
Noise pattern: `invalid_branch`
Package: `sample.support_triage`
Path: `TP_003`

## Review goal

Human QA/developer review of expected model behavior for a generated real-module testcase.

## Review focus

- Reject an invalid branch answer without mutating path state.
- Do not advance on steps where submit_expected is false.
- Recover to the current required node after the noisy turn.
- Complete the same terminal path after recovery.

## Scripted steps

| Step | Node | Input kind | Input | Expected behavior | Submit expected |
|---:|---|---|---|---|---|
| 0 | `N_ISSUE_SUMMARY` | `invalid_branch` | `__INVALID_BRANCH_SENTINEL__` | reject_invalid_branch_without_advancing_current_node | `False` |
| 2 | `N_ISSUE_SUMMARY` | `clean_answer` | `sample_answer_for_N_ISSUE_SUMMARY` | accept_answer_and_advance_along_terminal_path | `True` |
| 3 | `N_SEVERITY` | `clean_answer` | `medium` | accept_answer_and_advance_along_terminal_path | `True` |

## Expected outcome

Terminal: `G_TRIAGE_COMPLETE` / `gate`
Expected outputs: `OUT_TRIAGE_NOTE`
Expected state updates: `issue_summary`, `owner_team`, `severity`

## Review checklist

- [required] Current-node state remains coherent through the card.
- [required] No step with submit_expected=false advances the path.
- [required] Expected terminal target is reached after all valid submits.
- [required] No runtime execution, model scoring, or calibration is implied by this card.

## Readiness

Review card ready: `True`
Runtime execution ready: `False`
Scoring ready: `False`
Calibration ready: `False`
