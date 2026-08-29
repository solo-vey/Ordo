# alpha.20.0.68-dev — semantic human-decision choices

UI-only R3 fix.

- For `human_decision` nodes with `answer_type: enum`, the analyst action panel now
  exposes only canonical `on_answer` choices.
- Projection-only `transitions` and `navigation_contract.allowed_to` routes no longer
  create duplicate analyst buttons.
- Choice labels are derived from the decision/update-state semantics instead of the
  shared target-node label.
- Hovering an action shows the target node title/purpose/description plus node id.
- The underlying submitted canonical answer key is unchanged.

No playbook, Compiler semantic, or runtime execution semantic changes.
