# Owner requirement and incident context for BL-BENCH-047

## Observed behavior

A real RUN_02 invocation completed as `NO_CHANGE / INCOMPLETE_VALIDATION_HARD_STOP` after package integrity, pre-flight and versioned regressions passed. A Passport candidate then failed `unit_provider_semantics_v3`, no route-authorized artifacts were returned, and the Driver had no validation receipts, approvals or terminal completion.

## Process gap

The package had passed development-time validators, but that did not prove that a separate external executor could complete the full canonical run. Static fixtures, unit-level validators, package structure checks and synthetic acceptance tests are not equivalent to a blind black-box end-to-end execution.

## Owner decision

Before every package release, the creating model must independently execute the built package as an external executor in blind mode and preserve the results.

Required pre-release cycle:

1. Build a release candidate.
2. Use only the sealed package, neutral launch prompt and canonical RUN input.
3. Execute `RUN_01` through `RUN_05` without manually editing generated artifacts.
4. Pass every validator result through the Driver.
5. Permit canonical correction loops to invalidate, regenerate, revalidate and re-present new artifact versions.
6. Confirm receipts, exact presented versions, approvals, terminal state and result-package release gate.
7. Re-open and validate the final returned ZIP as a consumer would.
8. Compare every generated artifact against authoritative selected-run facts and cross-artifact rules.
9. Expected positive scenarios must reach their permitted successful terminal state; expected negative scenarios must stop at the specified hard stop without fabricated artifacts.
10. Preserve one immutable archive per RUN plus a campaign summary, checksums, neutral launch prompts and machine-readable reports.
11. If a point correction is possible, patch the candidate and rerun the complete affected campaign until valid.
12. Stop and request owner participation only when an authoritative input, policy decision or unavailable external binding is genuinely required.

The five self-validation RUN archives must be delivered together with the release candidate and explicitly identified as pre-release execution evidence, not canonical benchmark results and not user-confirmed evidence.
