# M78.0 — APF Real-Case Replay and Analyst Experience Validation

Status: `PASS`

Backlog: `BL-ORDO-008`

## Scope

Real case: `history_event.guided_intake`.

Validated scenarios:

- normal answer and advance;
- clarification without advancement;
- backtrack with prior-state preservation;
- requirement/scope change followed by QA-only handoff.

## Results

- Cases: **4/4 PASS**
- Mean analyst-experience score: **0.9750**
- Protected-state violations: **0**
- Lost prior answers: **0**
- Active-node/question mismatches: **0**
- Handoff failures: **0**

## Claim boundary

- Deterministic replay contract: validated.
- State continuity and allowed mutation boundaries: validated.
- Analyst-facing rendering: validated against minimized real-case transcripts.
- No claim of a statistical usability study or broad analyst-population generalization.

## Evidence

- `fixtures/apf_real_case_replay/history_event_replay_cases.json`
- `cli/ordo/apf_replay.py`
- `cli/tests/test_m78_0_apf_real_case_replay.py`
- `M78_0_APF_REAL_CASE_REPLAY_REPORT.json`

## Verdict

`BL-ORDO-008` may be closed for deterministic real-case replay and analyst-experience gate coverage.
