# Chapter 54. Multi-target Runtime Compilation Layer

M60 adds a horizontal compilation-target model to Ordo. The idea is simple: Ordo does not replace JSON with another format. It generates several derived representations from one canonical model.

```text
source/program.ordo.yaml
        ↓
canonical normalized model
        ↓
target emitters
        ├─ compiled/program.ir.json
        ├─ compiled/program.ordo.view
        └─ runtime/session.ordo.trace
```

## Why not replace JSON

Semantic JSON IR works well as a machine contract:

```text
stable
hashable
machine-readable
convenient for the CLI
convenient for verify-session
```

For a model, however, JSON often looks like “data” that can be slightly rearranged or extended. Ordo therefore adds an AI-facing projection that looks like a code-like contract without becoming a second source of truth.

## The first three targets

M60 uses only three formats:

```text
json-ir
ordo-code-view
session-trace
```

Python and Java targets are not part of this stage.

## The main M60 formula

```text
JSON IR decides.
Ordo-code explains.
Session-trace proves.
```

## `json-ir`

`compiled/program.ir.json` remains the canonical runtime target. The CLI executes runtime logic from it.

A runtime package is never created without `json-ir`, even when `--runtime-view ordo-code` is selected.

## `ordo-code-view`

`compiled/program.ordo.view` is a code-like projection for the model. It presents a node contract in a form that explicitly shows:

```text
kind
question
allowed answers
transition
reject rules
evidence requirements
```

The model does not read this file directly. It receives fragments through the CLI:

```bash
ordo next-step . --format ordo-code
ordo render-runtime-view . --format ordo-code --node <NODE_ID>
```

## `session-trace`

`runtime/session.ordo.trace` is an append-only proof program. The CLI writes it during an actual intake run. The model may not write or repair the trace itself.

## Target manifest

To prevent targets from drifting apart, M60 adds:

```text
compiled/targets.manifest.json
```

It records:

```text
canonical_ir_hash
target paths
target roles
target hashes
derived_from_ir_hash
mutable session-trace metadata
```

The command:

```bash
ordo verify-targets .
```

must report:

```text
target-set: consistent
```

## Main danger

A multi-target system is dangerous when each target starts living a separate life.

The rule is therefore strict:

```text
one canonical IR;
all other targets are derived;
all targets are verified by hashes;
Runtime Mode works only through the CLI.
```
