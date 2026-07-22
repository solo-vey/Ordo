# Human Review Scenario Card — CARD_001_CLEAN_TP_001

Milestone: `M61.0`
Case: `CLEAN_TP_001`
Case type: `clean_path`
Noise pattern: `none`
Package: `sample.support_triage`
Path: `TP_001`

## Review goal

Human QA/developer review of expected model behavior for a generated real-module testcase.

## Review focus

- Follow the expected path without extra detours.
- Reach the expected terminal target.
- Expose any expected output only after its allowed terminal/gate.

## Scripted steps

| Step | Node | Input kind | Input | Expected behavior | Submit expected |
|---:|---|---|---|---|---|
| 1 | `N_ISSUE_SUMMARY` | `clean_answer` | `sample_answer_for_N_ISSUE_SUMMARY` | accept_answer_and_advance_along_terminal_path | `True` |
| 2 | `N_SEVERITY` | `clean_answer` | `high` | accept_answer_and_advance_along_terminal_path | `True` |

## Expected outcome

Terminal: `G_TRIAGE_COMPLETE` / `gate`
Expected outputs: `OUT_TRIAGE_NOTE`
Expected state updates: `issue_summary`, `owner_team`, `severity`

## Review checklist

- [required] Current-node state remains coherent through the card.
- [optional/contextual] No step with submit_expected=false advances the path.
- [required] Expected terminal target is reached after all valid submits.
- [required] No runtime execution, model scoring, or calibration is implied by this card.

## Readiness

Review card ready: `True`
Runtime execution ready: `False`
Scoring ready: `False`
Calibration ready: `False`
