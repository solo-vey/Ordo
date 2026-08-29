# alpha.20.0.140-dev

Derived directly from .139 runtime diagnostics.

Generic semantic-recovery normalization now accepts common structurally equivalent model spellings:
- flat `state_patch` path/value mapping -> canonical `set` operations;
- operation with `path` + `value` but missing `op` -> `op: set`;
- `next_node` -> canonical `next_id`.

It does NOT coerce values. Array/object/null mismatches remain validation errors and are sent to the repair model together with:
- exact allowed value schemas;
- canonical operation contract;
- exact validator errors.

If `operations` is explicitly present with the wrong container type, it remains invalid and enters repair rather than being silently normalized away.

No playbook/domain source changed.
