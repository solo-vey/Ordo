# alpha.20.0.104-dev — Execute Playbook scroll-to-latest

- Adds a centered floating down-arrow control above the composer.
- The control is visible only when the transcript has additional content below the current viewport.
- It disappears automatically when the user reaches the bottom.
- Clicking it smoothly scrolls to the latest transcript content.
- Its vertical position is calculated from the live composer height, so it remains above single-line, multiline, and expanded composers.
- The control does not alter runtime or playbook semantics.
