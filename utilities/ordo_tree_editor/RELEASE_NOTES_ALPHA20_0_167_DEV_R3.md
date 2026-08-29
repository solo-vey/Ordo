# Ordo Tree Editor 0.2.0-alpha.20.0.167-dev

## Verification pipeline performance

No canonical Ordo/runtime semantics changed in this release.

Added `verify_editor.py` as the single stable verification entrypoint:

- `python verify_editor.py fast` — normal post-change feedback gate, target <15 s.
- `python verify_editor.py affected --changed <path>` — adds change-family regressions only when needed.
- `python verify_editor.py full` — exhaustive Python + JS verification, explicit 120 s Python budget; not part of every local TDD iteration.

Every stage emits real START/END timestamps, elapsed wall time and a hard timeout result.

The previous workflow repeatedly paid the ~100 s exhaustive Python suite after small changes. The new workflow separates targeted/fast feedback from the expensive exhaustive pre-release gate.
