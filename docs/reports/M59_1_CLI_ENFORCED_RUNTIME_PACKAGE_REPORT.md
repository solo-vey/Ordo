# M59.1 CLI-Enforced Runtime Package Report

## Summary

M59.1 starts the CLI-enforcement track. It changes runtime packaging from “compiled IR only” to “compiled IR plus embedded runtime CLI”.

## Implemented

- Runtime packages now include `cli_embedded/ordo`.
- Embedded CLI exposes runtime commands only.
- Runtime profile includes embedded CLI files in `BUILD_MANIFEST.json` and `SHA256SUMS.txt`.
- `ordo.runtime.json` records `embedded_cli_included`, `embedded_cli_path`, and `trust_level`.
- Runtime start files use hard-stop fallback instead of silent continuation.
- Runtime docs explain `DETERMINISM_NOT_ENFORCED` fallback marking.

## Not included yet

- Incremental `intake --submit`.
- Snapshot hash-chain.
- `verify-session`.
- Canary leak detection.

These are planned for later M59 slices.
