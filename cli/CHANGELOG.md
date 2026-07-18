# M60.3 — Runtime Packaging Modes

- Added behaviorally meaningful runtime view modes for runtime packaging: `json`, `ordo-code`, and `json,ordo-code`.
- `next-step --format auto` now follows `ordo.runtime.json` in packaged runtime profiles: JSON packages emit report-only output, Ordo-code packages emit the CLI-rendered `current_contract`.
- `render-runtime-view` is blocked in JSON-only runtime packages instead of regenerating an unconfigured projection.
- Runtime package validation now requires target files from `compiled/targets.manifest.json` instead of hardcoding `compiled/program.ordo.view` for every mode.

# M60.2 — Session Trace Proof Program

- Added `session-trace` as the third horizontal runtime target.
- Added mutable `runtime/session.ordo.trace`, initialized at compile/package time and appended only by CLI runtime submit.
- `intake --submit` now appends a code-like trace step after every node transition.
- Per-node evidence reports now include `session_trace` metadata, trace fragment, and trace digest.
- `verify-session` now checks target-set, session-chain, session-trace, and canary scan together.
- Runtime packages now include `runtime/session.ordo.trace`; embedded CLI verifies it through `verify-session`.
- Preserved the M60 rule: JSON IR decides; Ordo-code explains; Session-trace proves.

# M60.1 — Multi-target Runtime Compilation Layer

- Added explicit target emission for `json-ir` and `ordo-code-view`.
- Added `compiled/targets.manifest.json` with target hashes and `derived_from_ir_hash`.
- Added `compiled/program.ordo.view` as a CLI-served AI-facing state-machine contract projection.
- Added `ordo render-runtime-view` and `ordo verify-targets`.
- Added `next-step --format ordo-code` for current-node contract fragments.
- Runtime packages include target manifest/view while keeping `compiled/program.ir.json` as canonical source of truth.
- Embedded runtime CLI allowlist now permits `render-runtime-view` and `verify-targets`, while authoring commands remain blocked.

# Ordo CLI changelog

## M59.4 — Runtime UX hardening from external M58 comparison

- Added `ordo intake --submit --answer-file` for UTF-8/YAML/JSON answer payloads.
- Added automatic `runtime/live_session_state.json` resume cache for incremental intake and helper commands.
- Changed new session snapshots to a cleaner envelope shape: `{session_chain, state}` while preserving self-hash verification.
- Kept M59.3 protections: embedded CLI allowlist, per-node evidence reports, branch validation, canary scanning, and `verify-session`.


## v0.22.0-m43 lean cleanup

- Kept the CLI as a deterministic Process Rail helper layer.
- Removed obsolete registry-site/dashboard/publication/catalog commands.
- Removed obsolete release-promotion and global template-registry commands.
- Kept package-local output generation and validation.
- Kept package-level validation/provenance helpers.

## M59.2 — Incremental intake evidence reports

- Added `ordo intake <package> --submit <NODE_ID> --answer "..."` for one-node-at-a-time runtime submission.
- Added per-node evidence reports under `runtime/evidence/`.
- Added SHA-256 report/evidence digests to runtime helper outputs.
- Updated runtime intake to use compiled IR as runtime source, including inside source-free runtime packages.
- Added regression tests for submit evidence, node-skip blocking, and embedded CLI submit from a runtime profile.


## M59.3 — verify-session and canary

- Added `verify-session` runtime command.
- Added M59.3 hash-chain snapshot verification.
- Added compiler canary support and runtime-loader canary suppression.
- Embedded runtime CLI allowlist includes `verify-session`.

## BL-ORDO-048

- Added `compile-prompt`, `validate-prompt`, and `route-runtime` commands.
- Added the `prompt_only` package profile with explicit guarantee-loss and source-binding manifests.
- Added evidence-based routing and model/source/compiler drift revalidation.
