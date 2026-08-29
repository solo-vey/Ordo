# alpha.20.0.51-dev — R3 headless CI + StatePatch metadata normalization

- Adds `headless_runner.py` with package preflight and recorded-result step replay modes.
- Replay mode is explicitly regression-only (`acceptance_eligible=false`).
- Adds generic StatePatch adaptation for model output that misnests operation-envelope
  `basis`/`reason` inside a row `value`; adaptation is accepted only when the exact
  declared patch contract validates after the move.
- Strengthens the model contract prompt: `basis`/`reason` are siblings of `value`.
- No playbook/domain semantics are encoded in the Editor.
