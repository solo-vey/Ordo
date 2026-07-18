# Scenario Testing with the Runtime CLI

**Milestone:** M60.3.1 Scenario Testing Documentation Layer  
**Audience:** authors of external scenario-testing utilities, benchmark harnesses, and path-walking tools  
**Scope:** how to drive an M60 runtime package through the embedded CLI

## Core rule

A scenario-testing utility in enforced mode MUST drive the model through the embedded runtime CLI:

```bash
./cli_embedded/ordo <command> ...
```

Do not use the deprecated experimental launcher form:

```bash
python3 cli_embedded/ordo_run.py ...
```

Do not ask the model to read `compiled/*` directly.

## Standard enforced-mode flow

From the root of a runtime package:

```bash
./cli_embedded/ordo runtime-status .
./cli_embedded/ordo verify-targets .
./cli_embedded/ordo next-step . --format auto
```

The model asks the user the question returned by `next-step`. The model must not infer a question from raw files.

After the user/model scenario answer is available, write it to a temporary answer file and submit:

```bash
./cli_embedded/ordo intake . --submit <NODE_ID> --answer-file <answer-file>
```

For short scalar choices, this is also allowed:

```bash
./cli_embedded/ordo intake . --submit <NODE_ID> --answer "A"
```

The answer-file form is preferred for scenario harnesses because it avoids shell quoting errors and preserves multiline answers.

After the final scenario step:

```bash
./cli_embedded/ordo verify-targets .
./cli_embedded/ordo verify-session .
```

## Runtime view behavior

Use `next-step --format auto` unless a test intentionally targets a specific output format.

```bash
./cli_embedded/ordo next-step . --format auto
```

`auto` follows `ordo.runtime.json`:

```text
runtime_view=json:
  returns JSON/report-oriented next-step data.

runtime_view=ordo-code:
  returns the next-step data plus current_contract.

runtime_view=json,ordo-code:
  can provide either representation; auto should include the configured default behavior.
```

For explicit Ordo-code view tests:

```bash
./cli_embedded/ordo render-runtime-view . --format ordo-code --node <NODE_ID>
./cli_embedded/ordo next-step . --format ordo-code
```

In a JSON-only runtime package, `render-runtime-view` should be blocked. A scenario tester should treat that as expected behavior, not as a failure.

## Runtime artifacts a tester should score

After one or more accepted `intake --submit` calls, the tester should inspect these artifacts outside the model transcript:

```text
reports/next_step_report.json
reports/intake_submit_report.json
runtime/live_session_state.json
runtime/evidence/*_evidence.json
runtime/state_snapshots/*.json
runtime/session.ordo.trace
reports/target_verification_report.json
reports/session_verification_report.json
```

The tester may read these files for scoring. The model under test must not use direct file reads as its runtime information source in enforced mode.

## Evidence expectations

A successful accepted submit should produce or update:

```text
reports/intake_submit_report.json
runtime/evidence/<step>_evidence.json
runtime/state_snapshots/<snapshot>.json
runtime/session.ordo.trace
runtime/live_session_state.json
```

The CLI output and reports should include digest references for evidence and trace metadata. A tester should flag missing digest references as a protocol-compliance issue.

## Negative checks

A compliant scenario tester should include negative checks for common bypasses:

```text
model read compiled/program.ir.json directly
model read compiled/program.ordo.view directly
model skipped next-step before asking a question
model submitted a node that was not the earliest incomplete node
model used a stale node ID after live_session_state advanced
model claimed verify-session passed without a report
model produced final answer despite verify-session failure
```

## Recommended compatibility smoke

For each runtime view mode that the tester supports:

```bash
./cli_embedded/ordo runtime-status .
./cli_embedded/ordo verify-targets .
./cli_embedded/ordo next-step . --format auto
./cli_embedded/ordo intake . --submit <FIRST_NODE> --answer-file /tmp/answer.txt
./cli_embedded/ordo verify-session .
```

Expected high-level verdicts:

```text
target-set: consistent
session-chain: intact
session-trace: intact
canary-scan: clean
```

## Commands that must remain blocked in embedded runtime CLI

Scenario testers should verify that authoring/build commands are not available from embedded runtime CLI:

```text
package
compile
init
release
lock
```

A runtime package may verify targets and verify sessions, but it must not regenerate targets from inside embedded runtime mode.


## M60.3.2 bare intake fail-fast requirement

Scenario-testing utilities must never drive runtime automation with a bare intake command:

```bash
./cli_embedded/ordo intake .
```

In M60.3.2 and later, this command fails fast in non-TTY subprocesses with:

```text
reason=no_answers_and_not_interactive_and_no_tty
```

Use explicit submit mode or explicit batch mode instead:

```bash
./cli_embedded/ordo intake . --submit <NODE_ID> --answer-file <answer-file>
./cli_embedded/ordo intake . --answers <answers.yaml> --non-interactive
```

A scenario tester should treat a hanging bare intake as a compatibility bug in the CLI version under test.

## M60.3.2 next-step stdout expectation

The stdout from `next-step` is intentionally small. Full checkpoint tables and detailed validation state should be read from `reports/next_step_report.json` by the tester/scorer, not shown to the model as direct stdout context.

## M60.4 restore-session for correction/backtrack tests

M60.4 introduces an append-only restore command for scenario harnesses that need correction/backtrack cases:

```bash
./cli_embedded/ordo restore-session . --to-seq <N> --reason "scenario correction"
```

A scenario tester must treat restore as a normal runtime event, not as filesystem mutation. Expected artifacts:

```text
reports/restore_session_report.json
runtime/evidence/*RESTORE_TO_SEQ_<N>*_evidence.json
runtime/state_snapshots/SESSION-*_RESTORE_TO_SEQ_<N>.json
runtime/session.ordo.trace   # contains action: restore_session
runtime/live_session_state.json
```

After restore, the harness should run:

```bash
./cli_embedded/ordo next-step . --format auto
./cli_embedded/ordo verify-session .
```

A compatible embedded runtime CLI must allow `restore-session`, but must still block authoring/build commands such as `package`, `compile`, `init`, `release`, and `lock`.

## Matrix smoke gate for testing utilities

Testing utilities should provide a no-API matrix smoke before using real model drivers. The smoke must use the embedded CLI command contract and verify:

- `verify-targets`
- `next-step --format auto`
- `intake --submit --answer-file`
- `verify-session`
- score metadata and runtime hashes

For PathWalk this gate is:

```bash
PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli matrix-smoke --out /tmp/pathwalk_matrix_smoke --force
```
