# alpha.20.0.17 — Compiled operation-variant enforcement

Release 1 runtime hardening discovered by the Preflight Harness v1.0 StatePatch mutation matrix.

The runtime now validates every StatePatch operation against the compiler-declared `output_contract.state_patch.operation_variants` when those variants are present. This closes the compiler/runtime gap where a path/value could be valid while the operation itself was not declared for that path.

No semantic values, routes, or model outputs are repaired by this change. It is a fail-closed authority check against the compiled plan.
