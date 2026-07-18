# Declared-Contract Archive Pre-Release Self-Application Rules

## Mandatory decision node

This contract is executed after the candidate external-testing archive has been sealed and before any external testing bundle is exposed.

The exact sealed ZIP must be opened in a clean consumer workspace and evaluated against every validator, runtime prerequisite, entry point, regression command, required path, and release criterion that the archive itself declares.

## Rules

1. Build a machine-readable inventory from the archive's declared contracts.
2. Every declared validator and command must exist at the declared path and be invocable.
3. The actual runtime entry point must equal the declared entry point.
4. Required files and schemas must exist inside the sealed archive.
5. No local substitute or undocumented equivalent may satisfy a declared check.
6. Execute checks against the exact sealed candidate, never against an unsealed working directory.
7. On failure, block release and permit at most five scoped correction passes.
8. Every pass creates immutable evidence.
9. Release is allowed only with `PASS_RELEASE`.
10. Exhaustion or owner-dependent ambiguity ends as `NO_CHANGE / PRE_RELEASE_DECLARED_CONTRACT_MISMATCH`.

## Gate outputs

- `DECLARED_CONTRACT_INVENTORY.json`
- `DECLARED_CONTRACT_SELF_APPLICATION_REPORT.json`
- per-pass evidence under `PRE_RELEASE_DECLARED_CONTRACT_EVIDENCE/`
- release disposition: `PASS_RELEASE` or `NO_CHANGE`


## Canonical package-validation methodology integration (Alpha 20)

`PACKAGE_VALIDATION_METHODOLOGY.md` and `PACKAGE_VALIDATION_METHODOLOGY.json` are normative inputs to this gate. N074 must inventory, and N076 must execute, all twelve ordered check classes: physical integrity, completeness, addressability, version coherence, entrypoint coherence, structural completeness, semantic parity, correction-loop reachability, validator reality, positive/negative regressions, black-box pre-flight, and execution smoke test.

A local structural approximation cannot substitute for a declared command. The exact sealed ZIP is extracted into a clean consumer workspace; commands run only from that extraction. Any missing path, stale version, wrong entrypoint, failed validator/regression, unreachable correction loop, unsafe archive path, or missing green-light evidence routes to N077. After five failed cycles the terminal is `NO_CHANGE / PRE_RELEASE_DECLARED_CONTRACT_MISMATCH`.

The final report must include cycle number, archive SHA-256, every executed command and exit code, all twelve check results, and `GREEN_LIGHT: true|false`.
