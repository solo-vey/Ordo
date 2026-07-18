# Human Review Scenario Card — CARD_004_NOISE_TP_001_DISTRACTION

Milestone: `M61.0`
Case: `NOISE_TP_001_DISTRACTION`
Case type: `noise_path`
Noise pattern: `distraction`
Package: `sample.support_triage`
Path: `TP_001`

## Review goal

Human QA/developer review of expected model behavior for a generated real-module testcase.

## Review focus

- Handle an unrelated side question without losing path state.
- Do not advance on steps where submit_expected is false.
- Recover to the current required node after the noisy turn.
- Complete the same terminal path after recovery.

## Scripted steps

| Step | Node | Input kind | Input | Expected behavior | Submit expected |
|---:|---|---|---|---|---|
| 0 | `N_ISSUE_SUMMARY` | `distraction` | `Before answering, the user asks an unrelated side question.` | acknowledge_or_ignore_distraction_and_return_to_current_node | `False` |
| 2 | `N_ISSUE_SUMMARY` | `clean_answer` | `sample_answer_for_N_ISSUE_SUMMARY` | accept_answer_and_advance_along_terminal_path | `True` |
| 3 | `N_SEVERITY` | `clean_answer` | `high` | accept_answer_and_advance_along_terminal_path | `True` |

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
