# Node Helper — N_DISPLAY_NAME_UK / N_DISPLAY_NAME_EN human display texts

Use this helper when collecting human-readable names or future UI-facing copy.

## Goal

Keep display text readable, confirmed, and traceable to analyst input.

## Ask for

- Ukrainian user-facing event name.
- English technical documentation name.
- Short description or title only if the current node/package asks for it.
- Placeholder/fallback behavior only if it is part of the confirmed scope.

## Style guidance

Prefer clear business language. Avoid leaking implementation fields into user-facing text unless the analyst confirms that wording.

## Do not

- Do not invent display copy outside confirmed state.
- Do not add new UI text artifacts unless the package structure requires them.
- Do not silently translate in a way that changes meaning.

## Authority boundary

This helper improves wording. The node answer is still the only source for confirmed display-name state.
