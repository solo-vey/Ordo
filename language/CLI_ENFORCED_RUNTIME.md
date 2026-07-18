# CLI-Enforced Runtime Mode

M59.1 introduces the first trust-layer change for Runtime Mode: a runtime package must carry an embedded runtime CLI and must hard-stop if no approved CLI can execute.

## Principle

```text
A runtime package without a runnable CLI is not an enforced runtime package.
```

The package may still be inspected by a human or model, but Ordo determinism is not enforced unless runtime commands are executed and report evidence exists.

## Runtime package requirement

A runtime profile package includes:

```text
cli_embedded/ordo
cli_embedded/README.md
compiled/program.ir.json
START_HERE_RUNTIME_MODE.md
START_PROMPT_RUNTIME_MODE.md
output_templates/
reports/CLI_VALIDATION_SUMMARY.md
reports/BUILD_MANIFEST.json
reports/SHA256SUMS.txt
```

`cli_embedded/ordo` exposes only runtime commands. Authoring and release commands are blocked in the embedded runtime profile.

## Hard-stop fallback

If `cli_embedded/ordo` cannot execute, the assistant/runner must stop. It must not silently continue with direct IR reading or memory-based execution.

Required message:

```text
This environment cannot execute the embedded Ordo CLI. Ordo determinism guarantees for this session are NOT ENFORCED. Continuing is possible only in nondeterministic fallback mode, and every generated document must be marked DETERMINISM_NOT_ENFORCED.
```

Continuation requires explicit user approval. If fallback is approved, generated files must carry the marker:

```text
DETERMINISM_NOT_ENFORCED
```

## Trust level

M59.1 runtime packages declare:

```text
trust_level = level_1_cli_in_package_hard_stop
```

This is not MCP-level isolation. It makes accidental silent CLI bypass visible and blocks normal runtime execution when no CLI is available.

## M59.3 update — tamper-evident session chain

Runtime Mode now requires a hash-chain snapshot for every CLI-governed runtime transition. Snapshots live under:

```text
runtime/state_snapshots/SESSION-*.json
```

Each snapshot records `seq`, `node`, `answer_digest`, `prev_snapshot_hash`, `ir_hash`, `cli_version`, `timestamp_utc`, and `snapshot_hash`.

The runtime CLI exposes:

```bash
ordo verify-session <package>
```

Accepted terminal verdict:

```text
session-chain: intact
```

Failure verdicts include:

```text
session-chain: broken at seq N
session-chain: CANARY LEAK — raw IR was read
```

Compiled IR also contains a canary node that is never returned by runtime helper commands. A canary leak invalidates the session and requires restarting guided intake through CLI.

Manifest compatibility:

```text
trust_level = level_1_cli_in_package_hard_stop
trust_level_detail = level_1_cli_in_package_hard_stop_hash_chain_human_verify
```
