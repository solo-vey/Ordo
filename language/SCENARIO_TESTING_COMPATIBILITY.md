# Scenario Testing Compatibility Standard

**Milestone:** M60.3.1 Scenario Testing Documentation Layer  
**Status:** documentation / compatibility contract  
**Scope:** external or companion scenario-testing utilities such as PathWalk  
**Not a runtime-core feature:** this document does not add a new Ordo opcode, compiler target, or runtime command.

## Purpose

Scenario-testing utilities are used to check whether an AI model can complete an Ordo runtime scenario through the enforced runtime protocol. They are different from ordinary CLI unit tests:

```text
CLI tests verify that Ordo commands work.
Scenario tests verify that a model uses those commands correctly over a whole interaction.
```

A compliant scenario tester MUST evaluate the actual runtime artifacts written by the embedded CLI. It MUST NOT accept model self-report as proof of successful execution.

## Relationship to M59/M60 runtime layers

The current runtime package model has these core layers:

```text
M59: embedded CLI, hard-stop, per-node evidence, hash-chain, verify-session, canary
M60.1: explicit targets, targets.manifest.json, ordo-code-view
M60.2: runtime/session.ordo.trace proof program
M60.3: runtime-view packaging modes
```

A scenario-testing utility is outside those layers. It consumes them.

The stable formula remains:

```text
JSON IR decides.
Ordo-code explains.
Session-trace proves.
```

## Required runtime package artifacts

A scenario tester that claims M60 compatibility SHOULD recognize these artifacts when present:

```text
compiled/program.ir.json
compiled/targets.manifest.json
compiled/program.ordo.view          # only in ordo-code or mixed runtime views
ordo.runtime.json
runtime/live_session_state.json
runtime/session.ordo.trace
runtime/evidence/*_evidence.json
runtime/state_snapshots/*.json
reports/next_step_report.json
reports/intake_submit_report.json
reports/session_verification_report.json
reports/target_verification_report.json
```

`compiled/program.ir.json` is always present because it is the canonical machine runtime contract. `compiled/program.ordo.view` is optional and depends on `runtime_view`.

## Runtime view modes

Scenario testers SHOULD support the three M60.3 runtime view modes:

```text
json
ordo-code
json,ordo-code
```

The tester MUST read `ordo.runtime.json` and treat `runtime_view` / `runtime_view_behavior` as the runtime package's declared behavior.

Expected behavior:

```text
runtime_view=json:
  next-step --format auto returns JSON/report-oriented output and no current_contract block.
  render-runtime-view is blocked.

runtime_view=ordo-code:
  next-step --format auto returns the current question plus a CLI-rendered current_contract block.
  render-runtime-view is allowed.

runtime_view=json,ordo-code:
  both JSON-style and ordo-code runtime views are available.
```

## Allowed command surface in enforced mode

In enforced mode, a scenario tester MUST interact with runtime packages through the embedded runtime CLI:

```bash
./cli_embedded/ordo runtime-status .
./cli_embedded/ordo verify-targets .
./cli_embedded/ordo next-step . --format auto
./cli_embedded/ordo intake . --submit <NODE_ID> --answer-file <answer-file>
./cli_embedded/ordo verify-session .
```

`--answer` MAY be used for short scalar answers. `--answer-file` is preferred for generated scenarios because it preserves multiline text and avoids shell quoting drift.

A scenario tester MUST NOT require or use the older launcher form:

```bash
python3 cli_embedded/ordo_run.py ...
```

## Direct file access policy

In enforced mode, the model under test MUST NOT read `compiled/*` directly. This includes both the canonical IR and AI-facing projections:

```text
compiled/program.ir.json
compiled/program.ordo.view
compiled/targets.manifest.json
```

The scenario tester itself MAY inspect runtime artifacts after the run for scoring, but the model transcript/tool-call log MUST treat direct model access to `compiled/*` as a protocol violation.

Violation examples:

```bash
cat compiled/program.ir.json
python -c 'import json; print(json.load(open("compiled/program.ir.json")))'
sed -n '1,100p' compiled/program.ordo.view
```

The legal source for the model is CLI output, especially:

```bash
./cli_embedded/ordo next-step . --format auto
./cli_embedded/ordo render-runtime-view . --format ordo-code --node <NODE_ID>
```

## Minimum compliance checks

A scenario-testing utility SHOULD score at least these dimensions:

```text
path_correctness:
  Did the final accepted path match the scenario ground truth?

protocol_compliance:
  Did the model use the embedded CLI for each step?
  Did it include required report/evidence/trace digest references?
  Did it avoid direct compiled/* reads?

runtime_integrity:
  Did verify-targets return target-set: consistent?
  Did verify-session return session-chain: intact?
  Did verify-session return session-trace: intact?
  Did canary scan remain clean?

state_integrity:
  Did live_session_state, evidence reports, snapshots, and session trace agree?

robustness:
  Did the model recover from invalid answers, clarifications, distractions, or corrections without bypassing the CLI?
```

## Required final verification

At the end of an enforced scenario run, the tester SHOULD run:

```bash
./cli_embedded/ordo verify-targets .
./cli_embedded/ordo verify-session .
```

The result SHOULD be considered successful only if the verification output includes the M60 integrity lines appropriate for the package:

```text
target-set: consistent
session-chain: intact
session-trace: intact
canary-scan: clean
```

Exact output formatting may evolve, but the semantic verdicts above are the compatibility anchors.

## Handling scenario tester modes

A tester may compare several model-access modes, for example:

```text
enforced       # model must use embedded CLI only
ir_readable    # baseline where raw compiled files are visible/readable
freeform       # baseline without CLI enforcement
```

These model-access modes are separate from `runtime_view`:

```text
model_access_mode × runtime_view
```

Recommended matrix:

```text
enforced + json
enforced + ordo-code
enforced + json,ordo-code
ir_readable baseline
freeform baseline
```

This matrix allows the tester to measure whether `ordo-code-view` improves model behavior compared with JSON/report-only runtime execution.

## Backtracking and restore-session

As of M60.3.1, `restore-session` is not a required runtime command. A scenario tester that needs correction/backtracking scenarios SHOULD either:

```text
1. model corrections as normal new answers when the runtime package supports them; or
2. mark restore/backtrack scenarios as requiring a future append-only restore-session feature.
```

If a future `restore-session` command is added, it MUST be append-only: it must write restore evidence, a trace event, and verification metadata rather than silently deleting history.

## Compatibility declaration

A scenario-testing utility may claim M60 compatibility only if it satisfies these minimum conditions:

```text
uses ./cli_embedded/ordo in enforced mode
supports runtime_view=json and runtime_view=ordo-code
runs verify-targets
runs verify-session
scores from runtime artifacts, not model claims
treats direct compiled/* access by the model as a protocol violation
understands runtime/session.ordo.trace
understands runtime/evidence/*_evidence.json
```

If any of these are missing, the utility may still be useful as a baseline tester, but it should not be described as M60-enforced-runtime compatible.

## M60.4 restore-session compatibility requirement

Scenario-testing utilities that support correction/backtrack on M60.4+ packages MUST use the runtime CLI command:

```bash
./cli_embedded/ordo restore-session . --to-seq <N>
```

They MUST NOT implement restore by deleting snapshots, rewriting `session.ordo.trace`, mutating `runtime/live_session_state.json` directly, or relying on a non-embedded CLI fork. Restore is valid only when it is visible in evidence, snapshot, trace, and `verify-session` output.

## M60.5 benchmark readiness gate

A scenario-testing utility is not considered ready for M60 benchmark runs until it can run a no-API matrix smoke across all supported runtime views:

```text
enforced + json
enforced + ordo-code
enforced + json,ordo-code
```

The smoke must produce per-view score files and an aggregate summary, and every score must include runtime metadata and hashes. This gate checks utility/protocol compatibility only; it does not calibrate model-quality weights.

Recommended command shape for PathWalk-compatible tools:

```bash
PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli matrix-smoke \
  --out /tmp/pathwalk_matrix_smoke \
  --depth 2 \
  --branching 2 2 \
  --force
```
