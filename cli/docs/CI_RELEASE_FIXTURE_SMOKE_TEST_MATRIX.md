# CI / release fixture and smoke-test matrix

M69.4 validates the M69 clean-gate line without changing the clean-check or repo-check engines.

| Scenario | PR gate | Main gate | Release gate | Evidence expectation |
|---|---:|---:|---:|---|
| Clean required root | pass | pass | pass | JSON report created |
| Warning root | pass | block | block | report preserves warning status |
| Blocked required root | block | block | block | non-zero CLI exit code |
| No repo policy | pass / not applicable | pass / not applicable | pass / not applicable | applied packages remain delegated |
| JSON stdout + `--out` | equivalent | equivalent | equivalent | same parsed report |
| Release provenance | n/a | n/a | pass | SHA-256 and byte-size link exact report bytes |

Gate policy remains:

- PR: `standard`, warnings allowed.
- Main: `standard --fail-on-warning`.
- Release: `strict --fail-on-warning`.

The matrix is implemented in `cli/tests/test_ci_release_smoke_matrix.py` and reuses the real clean-check fixtures from M68.1.
