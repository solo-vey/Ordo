# DD-ORDO-M59-003 — Tamper-Evident Runtime Session

Status: accepted  
Milestone: M59.3  
Date: 2026-07-07

## Context

M59.1 put the runtime CLI inside runtime packages and replaced silent fallback with hard-stop. M59.2 added incremental `intake --submit` and per-node evidence reports. Those changes make drift visible, but they do not prove that the runtime state was produced as one unbroken CLI-governed session.

## Decision

Runtime sessions now write a tamper-evident snapshot chain under `runtime/state_snapshots/SESSION-*.json`.

Every chain snapshot records:

```json
{
  "seq": 7,
  "node": "N7_NORMALIZATION_CONTRACT",
  "answer_digest": "sha256:...",
  "prev_snapshot_hash": "sha256:...",
  "ir_hash": "sha256:...",
  "cli_version": "0.34.0",
  "timestamp_utc": "...",
  "snapshot_hash": "sha256:..."
}
```

The CLI exposes:

```bash
ordo verify-session <package>
```

The command checks sequence continuity, `prev_snapshot_hash`, snapshot content hashes, snapshot `ir_hash` against the current `compiled/program.ir.json`, and canary leakage.

## Canary

The compiler inserts a generated `N99_CANARY_DO_NOT_EMIT` node into compiled IR. `load_runtime_source` skips that node, so runtime helper commands never expose it. If the generated canary string appears in runtime-visible outputs, `verify-session` reports:

```text
session-chain: CANARY LEAK — raw IR was read
```

## Human verify gate

Final runtime approval requires the user to run:

```bash
cli_embedded/ordo verify-session <package>
```

The gate is valid only when the user pastes the terminal line verbatim and it says:

```text
session-chain: intact
```

## Consequences

This does not make bypass impossible without MCP or sandbox isolation. It makes silent bypass and accidental drift visible through files that can be rechecked in another session.
