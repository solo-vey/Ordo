# Node Helper — N_PATH_SELECT source type clarification

Use this helper when the analyst is choosing the History Event path.

## Goal

Explain the available path options in plain language and help the analyst choose one of the existing allowed answers: `A`, `B`, `C`, or `D`.

## Suggested explanation

- `A` — the event comes from a source row / ChangeRecord-style flow.
- `B` — the event comes from a derived or aggregated state.
- `C` — the event is already provided as an external History Event fact.
- `D` — the situation is non-standard or needs custom review.

## Clarification behavior

Ask one short clarifying question if the input is unclear. Prefer mapping the answer to one of the declared options instead of creating a new path.

## Do not

- Do not introduce extra path options.
- Do not ask legacy A1/A2/A3/A4/A5 subquestions unless those nodes exist in the compiled process.
- Do not silently change `selected_path`.
- Do not claim a gate or validation result.

## Authority boundary

This helper explains the node only. The node, state update, allowed answers, gates, and CLI evidence remain authoritative.
