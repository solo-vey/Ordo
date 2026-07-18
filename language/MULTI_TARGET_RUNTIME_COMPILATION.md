# M60.3 Multi-target Runtime Compilation Layer

M60 introduces horizontal target emission from the canonical normalized Ordo model. It does **not** replace Semantic JSON IR. It makes the target roles explicit:

```text
JSON IR decides.
Ordo-code explains.
Session-trace proves.
```

## Compilation model

```text
source/program.ordo.yaml
        ↓
canonical normalized model
        ↓
target emitters
        ├─ compiled/program.ir.json        # json-ir
        ├─ compiled/program.ordo.view      # ordo-code-view, optional by runtime_view
        └─ runtime/session.ordo.trace      # session-trace, mutable runtime proof
```

`compiled/program.ir.json` remains the canonical machine contract. Other targets are derived projections or runtime proofs and must not become a second source of truth.

## Targets

### `json-ir`

Canonical runtime IR. The CLI executes from this target and `verify-session` binds snapshots, evidence, canary checks, and trace checks to its `canonical_ir_hash`.

Runtime packages must always include `json-ir`, even when the AI-facing runtime view is `ordo-code`.

### `ordo-code-view`

AI-facing contract projection. It renders node contracts in a code-like form so the model sees explicit node kinds, allowed answers, transitions, rejection rules, and evidence requirements.

The projection is not source of truth. It is legal for the AI only when served by CLI output, for example:

```bash
ordo render-runtime-view <package> --format ordo-code --node <NODE_ID>
ordo next-step <package> --format ordo-code
ordo next-step <package> --format auto
```

Direct AI reading of `compiled/program.ordo.view` is still a Runtime Mode violation because all `compiled/*` files belong to the CLI.

### `session-trace`

Append-only proof program written by the CLI during runtime intake. Each accepted `intake --submit` appends one trace step and links it to evidence and state snapshots.

The AI must not write or repair `runtime/session.ordo.trace`. It may only show the trace path, digest, and last fragment returned by CLI reports.

## Manifest

`compiled/targets.manifest.json` records:

- `canonical_ir_hash`;
- target names and roles;
- target file paths;
- SHA-256 hashes for immutable targets;
- `derived_from_ir_hash` for non-canonical targets;
- `initial_sha256`, `mutable: true`, and trace metadata for `session-trace`.

The manifest exists to prevent drift between target projections.

## Runtime view modes

M60.3 makes runtime view selection a package behavior, not a decorative option.

```bash
ordo package <package> --profile runtime --runtime-view json
ordo package <package> --profile runtime --runtime-view ordo-code
ordo package <package> --profile runtime --runtime-view json,ordo-code
```

Rules:

- `json` packages `json-ir` + `session-trace` and intentionally excludes stale `compiled/program.ordo.view`.
- `ordo-code` packages `json-ir` + `ordo-code-view` + `session-trace`; `next-step --format auto` emits the current contract fragment.
- `json,ordo-code` packages both AI-facing modes and allows explicit `--format json` or `--format ordo-code`.

`ordo.runtime.json` records `runtime_view`, `targets`, `canonical_target`, and `runtime_view_behavior`.

## Verification

`ordo verify-targets <package>` validates target consistency.

`ordo verify-session <package>` validates target-set, session-chain, session-trace, and canary scan together.

Expected clean terminal lines include:

```text
target-set: consistent
session-chain: intact
session-trace: intact
canary-scan: clean
```

## Non-goals

M60.3 does not add Python or Java targets. It also does not add MCP, sandboxing, or a new runtime engine.
