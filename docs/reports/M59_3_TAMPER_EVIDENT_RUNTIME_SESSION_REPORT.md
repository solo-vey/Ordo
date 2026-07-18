# M59.3 Tamper-Evident Runtime Session Report

M59.3 completes the Level 1 CLI-enforced runtime track without MCP or sandbox isolation.

## Added

- `runtime/state_snapshots/SESSION-*.json` hash-chain snapshots.
- `ordo verify-session <package>` runtime command.
- Embedded runtime CLI support for `verify-session`.
- Snapshot binding to `compiled/program.ir.json` via `ir_hash`.
- Snapshot content self-hash and `prev_snapshot_hash` chain continuity.
- Compiler-generated `N99_CANARY_DO_NOT_EMIT` IR node.
- Runtime loader skip for canary nodes.
- Canary leak scan in `verify-session`.
- `START_HERE_RUNTIME_MODE.md` IR access hard rule.
- Human final verify gate protocol.

## Trust level

Backward-compatible manifest field remains:

```text
trust_level = level_1_cli_in_package_hard_stop
```

M59.3 adds:

```text
trust_level_detail = level_1_cli_in_package_hard_stop_hash_chain_human_verify
```

## Validation

- CLI regression tests: 62/62 passed.
- New M59.3 tests: 4/4 passed.
- Smoke: incremental submit then `verify-session` returns `session-chain: intact`.
- Smoke: deleted initial snapshot returns `session-chain: broken at seq 0`.
- Smoke: emitted canary returns `session-chain: CANARY LEAK — raw IR was read`.
