# Runtime Guided Intake Entry Protocol

This document describes the practical entry loop for running a compiled Ordo package in Runtime Mode.

## Current protocol

A runtime session starts from package instructions and then uses embedded CLI only:

```bash
./cli_embedded/ordo runtime-entry .
./cli_embedded/ordo next-step . --format auto
```

The AI must not inspect `compiled/*` directly. `compiled/program.ir.json` is the canonical machine target, but it is owned by CLI. `compiled/program.ordo.view`, when present, is also a compiled target and must be accessed only through CLI-rendered output.

## Runtime views

M60.3 supports three runtime packaging modes:

```bash
ordo package <package> --profile runtime --runtime-view json
ordo package <package> --profile runtime --runtime-view ordo-code
ordo package <package> --profile runtime --runtime-view json,ordo-code
```

`json` mode exposes standard helper reports. `ordo-code` mode makes `next-step --format auto` include a current-node code-like contract fragment. `json,ordo-code` mode allows both explicit formats.

## Per-answer submit loop

For each user answer:

```bash
./cli_embedded/ordo intake . --submit <NODE_ID> --answer-file <tmp_answer.yaml>
```

A valid transition creates or updates:

```text
reports/intake_submit_report.json
runtime/evidence/*_evidence.json
runtime/state_snapshots/SESSION-*.json
runtime/session.ordo.trace
runtime/live_session_state.json
```

The AI must show the evidence path, evidence digest, trace path, and trace digest before asking the next question.

## Verification

Use:

```bash
./cli_embedded/ordo verify-targets .
./cli_embedded/ordo verify-session .
```

A clean session reports:

```text
target-set: consistent
session-chain: intact
session-trace: intact
canary-scan: clean
```

## Mental model

```text
JSON IR decides.
Ordo-code explains.
Session-trace proves.
```
