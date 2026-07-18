# Runtime Guided Intake Entry Protocol

Runtime Guided Intake is the protocol for running an already compiled Ordo package as a deterministic session. The model must not use memory, generic prompting, or direct file inspection as the source of the next question.

## Required startup order in enforced Runtime Mode

```text
START_HERE_RUNTIME_MODE.md
→ cli_embedded/ordo runtime-entry <package>
→ cli_embedded/ordo next-step <package> --format auto
→ user answer
→ cli_embedded/ordo intake <package> --submit <node_id> --answer-file <answer_file>
→ evidence + state snapshot + session trace
→ repeat through CLI output only
```

The editable source of truth remains `source/program.ordo.yaml` in the development profile. Runtime packages intentionally exclude that source. The runtime executor must use the embedded CLI and must not directly read `compiled/*`.

## Legal runtime information sources

The only legal AI-facing Runtime Mode information sources are CLI-rendered outputs:

```text
runtime-entry
runtime-status
next-step
next-step --format auto
next-step --format ordo-code
render-runtime-view
check-gate
validate-state
intake --submit
verify-targets
verify-session
```

Direct opening, parsing, quoting, or using `compiled/program.ir.json`, `compiled/program.ordo.view`, or any other `compiled/*` file is a Runtime Mode violation. The files are machine targets owned by CLI.

## Runtime view modes

M60.3 defines package-level runtime views:

```text
runtime_view=json
runtime_view=ordo-code
runtime_view=json,ordo-code
```

- In `json` mode, `next-step --format auto` emits JSON-style reports without a current contract block.
- In `ordo-code` mode, `next-step --format auto` emits the current node contract fragment rendered by CLI.
- In `json,ordo-code` mode, both explicit output formats are allowed.

The rule remains:

```text
JSON IR decides.
Ordo-code explains.
Session-trace proves.
```

## Required per-step evidence

After every user answer, the AI must submit that answer through CLI. A valid accepted transition writes:

```text
reports/intake_submit_report.json
runtime/evidence/*_evidence.json
runtime/state_snapshots/SESSION-*.json
runtime/session.ordo.trace
runtime/live_session_state.json
```

The AI response must show at minimum:

```text
node: <submitted node>
evidence: <path> sha256=<digest>
session-trace: runtime/session.ordo.trace sha256=<digest>
next: <next node or stop>
```

The AI must not ask the next node question until the submit report and evidence exist.

## Final verification gate

Before final approval, the user should be asked to run:

```bash
<package>/cli_embedded/ordo verify-session <package>
```

The gate is clean only when the user-provided terminal output includes successful verification lines such as:

```text
target-set: consistent
session-chain: intact
session-trace: intact
canary-scan: clean
```

## Gate discipline

The runtime must not:

- invent the next question when CLI has a next step;
- skip a required gate without `check-gate`;
- generate draft artifacts before `validate-state`;
- generate final package artifacts before output validation, consistency, go/no-go, and session verification;
- treat text claims such as `executed_cli_passed` as proof without report files and digests.


## M60.3.2 automation safety: bare intake must fail fast

Runtime automation must not call bare guided intake without an explicit mode. The following is unsafe in non-interactive harnesses and scenario-testing subprocesses:

```bash
./cli_embedded/ordo intake .
```

A compliant runtime CLI must fail fast when all of the following are true:

```text
no --submit
no --answers
no --non-interactive
stdin is not a TTY
```

The required failure reason is:

```text
no_answers_and_not_interactive_and_no_tty
```

Automation must use one of these explicit forms instead:

```bash
./cli_embedded/ordo intake . --submit <NODE_ID> --answer-file <answer-file>
./cli_embedded/ordo intake . --answers <answers.yaml> --non-interactive
```

Interactive prompting is valid only when a human is running the CLI in a real TTY.

## M60.3.2 stdout compactness rule

`next-step` stdout is an AI-facing prompt surface and should remain compact. It should include only the current step summary, report path, digest, protocol line, and the current contract fragment when `ordo-code` is active. Full checkpoint details belong in `reports/next_step_report.json`, not in stdout.

## M60.4 restore-session: append-only correction/backtrack

M60.4 adds a native runtime correction command:

```bash
./cli_embedded/ordo restore-session . --to-seq <N> [--reason "..."]
```

This command is not a destructive rollback. It must never delete or truncate older snapshots, evidence reports, or trace steps. Instead it appends a new restore event:

```text
restore-session
→ reports/restore_session_report.json
→ runtime/evidence/*RESTORE_TO_SEQ_<N>*_evidence.json
→ runtime/state_snapshots/SESSION-*_RESTORE_TO_SEQ_<N>.json
→ runtime/session.ordo.trace step action=restore_session
→ runtime/live_session_state.json updated to the restored state
```

After a restore event, the model must continue from the restored live session state and ask the next question only through `next-step --format auto`.

A valid restore must be checked by the same final command:

```bash
./cli_embedded/ordo verify-session .
```

`verify-session` must validate the restore event through the session chain, session trace, linked evidence report, linked snapshot, target-set, and canary scan.
