# Chapter 53. CLI-enforced Runtime Package

After the runtime profile appeared, it became clear that a clean runtime package containing `compiled/program.ir.json` but no CLI does not provide full enforcement. The model could read the IR directly and pass through guided intake without deterministic helper reports.

M59 therefore introduces a runtime trust layer: a runtime package must contain not only compiled IR, but also an embedded CLI that is the only legal execution interface.

```text
runtime package = compiled IR + start files + output templates + embedded runtime CLI + evidence layer
```

## Main rule

```text
A runtime package without a runnable CLI is not an enforced runtime package.
```

`ordo package --profile runtime` adds:

```text
cli_embedded/ordo
cli_embedded/README.md
cli_embedded/ordo_pkg/ordo/...
```

The embedded CLI exposes runtime commands only. Authoring, compile, release, and package commands are blocked in the runtime wrapper.

## Hard stop instead of a soft fallback

The old approach allowed the system to say `CLI status: not_run_cli_unavailable` and continue. That was an honest self-report, but it did not change behavior.

The new approach is:

```text
if cli_embedded/ordo cannot run → stop
```

Continuation is allowed only after explicit user approval of a nondeterministic fallback. In that mode, every generated artifact must contain:

```text
DETERMINISM_NOT_ENFORCED
```

## Incremental intake

M59.2 makes guided intake step-by-step. The model should no longer walk through the entire scenario on its own. For every user answer, it calls:

```bash
cli_embedded/ordo intake . --submit <NODE_ID> --answer-file <tmp_answer.yaml>
```

The CLI accepts or blocks the transition, writes an evidence report, and returns a digest. The model may not ask the next question until the submit has been executed.

## Evidence, snapshots, and live state

Every accepted submit writes:

```text
reports/intake_submit_report.json
runtime/evidence/*_evidence.json
runtime/state_snapshots/SESSION-*.json
runtime/live_session_state.json
```

`live_session_state.json` is a UX cache for automatically continuing a session. It does not replace evidence and is not proof by itself.

## Tamper-evident verification

M59.3 adds hash-chain snapshots, `verify-session`, canary detection, and a human final verification gate.

The command:

```bash
cli_embedded/ordo verify-session .
```

checks that the runtime session has not drifted silently. Expected clean lines are:

```text
session-chain: intact
canary-scan: clean
```

A canary does not physically prevent direct IR reading, but it makes leakage provable: if service canary text appears in outputs or trace, the session receives a failure.

## Trust level

M59 defines Level 1 without MCP and without a sandbox:

```text
level_1_cli_in_package_hard_stop_hash_chain_human_verify
```

This is not cryptographic protection against an attacker with full filesystem access. It protects against silent drift and accidental CLI bypass.

## Formula

```text
CLI available → Runtime Mode enforced.
CLI unavailable → hard stop.
CLI bypassed → session invalid / evidence missing / canary or chain failure.
```
