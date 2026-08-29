# alpha.20.0.11 — Conversational Recovery

- `N_VALIDATION_FAILURE_RECOVERY` / `AI.EXPLAIN_VALIDATION_FAILURE_AND_ROUTE` supports free-form dialogue instead of enum-only input.
- The analyst remains on the recovery node for diagnostic conversation.
- Recorded auto-answers pause immediately on entering conversational recovery.
- Model-proposed StatePatch writes are fail-closed to `affected_state` roots from the recorded gate failure.
- Analyst can ask to re-run the failed gate without leaving recovery manually.
- Analyst can explicitly request a grounded repair target; editor enters that node with auto-answer paused/manual correction mode.
- Graph authority remains with runtime; free conversation cannot invent arbitrary targets.
