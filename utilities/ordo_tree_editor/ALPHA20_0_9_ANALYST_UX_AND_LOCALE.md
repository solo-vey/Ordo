# alpha.20.0.9 — Analyst UX & Locale

- Human gates show the actual validation criterion and clear analyst actions instead of raw route semantics.
- `on_fail` from a human gate opens a clarification step so the analyst can state what failed before the failure router runs.
- Recovery cards show failed checks, missing coverage/information and the grounded recommended recovery point before routing.
- When a recovery target is grounded, it is the primary action rather than presenting unrelated graph routes as equal choices.
- Analyst-facing runtime/model/recovery text follows the semantic plan `interaction_contract`.
- Current Risk Factor Passport declares `uk-UA` / `uk`. Technical IDs and machine keys remain unchanged.
