# Ordo PathWalk Scenario Testing

**Milestone:** M60.3.1 Scenario Testing Documentation Layer  
**Status:** conceptual and compatibility documentation  
**Scope:** PathWalk-style external/companion scenario testing utilities  
**Important:** PathWalk is not part of the required Ordo runtime package.

## What PathWalk is

PathWalk is a scenario-testing approach for checking whether an AI model can move through an Ordo decision path while respecting the runtime protocol.

It is useful because ordinary CLI regression tests answer only one question:

```text
Does the CLI behave correctly?
```

PathWalk-style scenario testing asks a different question:

```text
Does the model actually use the CLI correctly across a whole guided interaction?
```

## What PathWalk is not

PathWalk is not:

```text
an Ordo opcode
a required runtime artifact
a replacement for verify-session
a replacement for CLI regression tests
a license to read compiled/* directly in enforced mode
```

It is a companion testing layer that may be distributed separately.

## Why it matters after M59/M60

M59 and M60 make runtime execution more deterministic and more auditable:

```text
embedded CLI
hard-stop when CLI is unavailable
per-node evidence reports
hash-chain snapshots
verify-session
canary scan
target manifest
ordo-code-view
session.ordo.trace
runtime-view modes
```

A scenario-testing utility can now measure how well a model follows those rules instead of relying on the model's self-report.

## Recommended PathWalk architecture

A PathWalk-compatible utility should be structured around four components:

```text
scenario generator
  creates synthetic or reference decision paths and expected outcomes

runtime package provider
  supplies or builds an Ordo runtime package for a selected runtime_view

model runner / harness
  gives the model only the permitted CLI protocol and scenario prompts

scorer
  reads runtime artifacts after the run and compares them to ground truth
```

The scorer should evaluate files written by the CLI, not the model's claims.

## M60 runtime artifacts to understand

A PathWalk-style scorer should understand at least:

```text
compiled/targets.manifest.json
ordo.runtime.json
runtime/live_session_state.json
runtime/evidence/*_evidence.json
runtime/state_snapshots/*.json
runtime/session.ordo.trace
reports/target_verification_report.json
reports/session_verification_report.json
```

It should treat `compiled/program.ir.json` as the canonical machine target, but in enforced mode the model under test must not read it directly.

## Runtime view test matrix

PathWalk can compare model behavior across runtime views:

```text
enforced + json
enforced + ordo-code
enforced + json,ordo-code
ir_readable baseline
freeform baseline
```

This is one of the main reasons to keep PathWalk separate from runtime core. It can test the same scenario under multiple model-access conditions and reveal whether the Ordo-code view improves model discipline.

## Required enforced-mode commands

A modern M60-compatible PathWalk harness should instruct the model to use:

```bash
./cli_embedded/ordo runtime-status .
./cli_embedded/ordo verify-targets .
./cli_embedded/ordo next-step . --format auto
./cli_embedded/ordo intake . --submit <NODE_ID> --answer-file <answer-file>
./cli_embedded/ordo verify-session .
```

It should not instruct the model to use the old experimental launcher:

```bash
python3 cli_embedded/ordo_run.py ...
```

## Scoring dimensions

A useful PathWalk score should be split rather than collapsed into one number:

```text
path correctness
  Did the accepted terminal path match the scenario ground truth?

protocol compliance
  Did the model call next-step before asking questions?
  Did it submit answers through intake --submit?
  Did it include evidence/report/trace digest references?

runtime integrity
  Did verify-targets and verify-session pass?

compiled-read violations
  Did the model try to read compiled/* directly?

robustness
  Did the model handle distractions, clarifications, invalid choices, or corrections without bypassing the CLI?
```

## Backtracking note

Backtracking/correction scenarios are valuable, but M60.3 does not define a required `restore-session` command. A PathWalk utility may still model corrections, but any future restore capability should be append-only and must be integrated with evidence reports, session-chain, and session.ordo.trace.

Until that exists, scenario suites should clearly mark restore/backtrack cases as either:

```text
supported by the package's own flow; or
requires future restore-session support
```

## Compatibility checklist

A PathWalk-style utility is M60-compatible only if it can answer yes to the following:

```text
Does it use ./cli_embedded/ordo in enforced mode?
Does it support runtime_view=json?
Does it support runtime_view=ordo-code?
Does it run verify-targets?
Does it run verify-session?
Does it inspect runtime/session.ordo.trace?
Does it inspect runtime/evidence reports?
Does it treat model direct access to compiled/* as a violation?
Does it avoid scoring based only on model self-report?
```

If not, it can still be useful as an older baseline harness, but it should not be treated as a full M60 enforced-runtime scenario tester.


## M60.3.2 safety compatibility

A PathWalk-style utility must account for M60.3.2 fail-fast behavior. Bare `intake` without `--submit`, `--answers`, or `--non-interactive` is not a valid automation command. In a non-TTY subprocess it must return a clear failure instead of waiting for `input()`.

Recommended smoke check:

```bash
./cli_embedded/ordo intake . < /dev/null
```

Expected result:

```text
failed reason=no_answers_and_not_interactive_and_no_tty
```

This confirms that the CLI will not hang a benchmark worker.

PathWalk should also keep model-facing `next-step` stdout compact and use report files for full scoring details.

## M60.4 native restore-session compatibility

M60.4 upgrades correction/backtrack from an external harness concern into a runtime command:

```bash
./cli_embedded/ordo restore-session . --to-seq <N>
```

PathWalk-style utilities should stop inventing their own rollback mechanism once they target M60.4 or later. They should use the embedded CLI command and score the restore as an append-only runtime event.

A restore-compatible scorer should verify:

```text
restore report exists
restore evidence report exists
restore snapshot exists
session.ordo.trace contains action: restore_session
live_session_state points to the restored current node
verify-session still returns session-chain: intact
```

The old approach of truncating local state, rewriting history, or using a fork-only `restore-session` outside the embedded CLI surface should be treated as deprecated for M60.4+ compatibility.

## M60.5 readiness smoke before model/API runs

Before running a model provider benchmark, run the PathWalk matrix smoke:

```bash
PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli matrix-smoke \
  --out /tmp/pathwalk_matrix_smoke \
  --depth 2 \
  --branching 2 2 \
  --force
```

This verifies that the utility can build and score M60 runtime packages in `json`, `ordo-code`, and `json,ordo-code` runtime views. It is a compatibility smoke, not a calibrated model benchmark.
