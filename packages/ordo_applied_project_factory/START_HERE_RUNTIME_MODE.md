# START HERE — Ordo Runtime Mode

This file is the complete Runtime Mode instruction for this Ordo subject package.
The short prompt must only tell the AI/runner to read this file and start the runtime loading protocol.


## 0. IR ACCESS PROTOCOL — HARD RULE

`compiled/program.ir.json` and every file under `compiled/` are CLI-owned runtime internals.

The AI must not open, read, view, cat, parse, quote, summarize, or use `compiled/*` directly for runtime decisions. The only legal Runtime Mode source is the output of `cli_embedded/ordo` commands: `runtime-entry`, `next-step`, `check-gate`, `validate-state`, `intake --submit`, and `verify-session`.

If this rule is violated, the session status becomes `DETERMINISM_VIOLATED`; every generated artifact must receive `DETERMINISM_VIOLATED` as its first line; the only recovery is a full restart of guided intake through the CLI.

Every user-facing runtime question must include the report path and first 12 characters of the SHA-256 digest from the CLI report that supplied the question. A question without `(report path + digest)` is a visible protocol violation.

If the embedded CLI cannot run, do not read IR as a fallback. Apply hard-stop fallback mode instead.

## Runtime loading protocol

1. Read `START_HERE_RUNTIME_MODE.md`.
2. Read `ordo.yml` as the package manifest / entrypoint.
3. Resolve the editable source program declared in `ordo.yml`, normally `source/program.ordo.yaml` in dev packages.
4. Resolve the compiled IR declared in `ordo.yml`, normally `compiled/program.ir.json`.
5. Locate the package-owned runtime CLI at `cli_embedded/ordo` when running a runtime package.
6. Check whether compiled IR exists and is fresh relative to source YAML when source YAML is present.
7. If IR is missing or stale and CLI is available, run the CLI command that compiles or reports the runtime state before guided execution.
8. If `cli_embedded/ordo` or another approved Ordo CLI cannot run, HARD-STOP. Do not continue silently.
9. Load compiled IR as the runtime source for guided execution only through CLI helper outputs.
10. Initialize or load `run_state.json` / report-embedded state.
11. Use `runtime-entry`, `next-step`, `check-gate`, and `validate-state` from IR + state. Do not invent next steps when a current IR exists.

## Source of truth model

```text
ordo.yml = package manifest / entrypoint
source/program.ordo.yaml = editable source of truth in dev profile
compiled/program.ir.json = runtime source for guided execution
run_state.json = current execution state
generated artifacts = rendered output
```

`source/program.ordo.yaml` is used for editing, explanation, and diagnostics in dev packages. If `compiled/program.ir.json` is current, guided question order comes from CLI helper output over the IR, not from memory and not from free reading of YAML.

## No memory mode

Do not conduct guided intake “from memory”, from old conversation context, or from general package instructions when a current compiled IR exists. Use `cli_embedded/ordo runtime-entry` or `cli_embedded/ordo next-step` before the first guided question.

## CLI pipeline

Use the real CLI syntax exposed by `cli_embedded/ordo --help` or `ordo --help`. Standard runtime pipeline:

```bash
cli_embedded/ordo runtime-status <package>
cli_embedded/ordo runtime-entry <package>
cli_embedded/ordo next-step <package> --state run_state.json
cli_embedded/ordo check-gate <package> <GATE_ID> --state run_state.json
cli_embedded/ordo validate-state <package> --state run_state.json
cli_embedded/ordo intake <package> --answers <answers-file> --non-interactive
cli_embedded/ordo generate-output <package> --out <output-dir>
cli_embedded/ordo validate-output <package>
cli_embedded/ordo validate-artifacts <package> --artifacts <output-dir>
cli_embedded/ordo consistency <package> --artifacts <output-dir>
cli_embedded/ordo go-no-go <package>
cli_embedded/ordo validate-cli-status <report.json>
cli_embedded/ordo verify-session <package>
```

In dev workspaces the full `ordo` CLI may also run `lint`, `compile`, `test`, `coverage`, `package`, and other authoring commands. Runtime packages expose only runtime commands through `cli_embedded/ordo`.

## CLI truthfulness rule

Allowed statuses:

```text
CLI status: executed_cli_passed
CLI status: executed_cli_failed
CLI status: logical_self_check_only
CLI status: not_run_cli_unavailable
CLI status: not_run_user_skipped
```

Never write `CLI validation passed` unless CLI commands actually ran and the report contains evidence. Record command evidence in `reports/CLI_VALIDATION_SUMMARY.md` or a JSON validation report. A status without file evidence is not proof.

## Fallback mode — hard-stop

Hard-stop fallback mode is mandatory when the embedded CLI cannot run.

If `cli_embedded/ordo` or an approved Ordo CLI is unavailable, do not continue as if Runtime Mode is enforced. Stop and tell the user exactly:

```text
This environment cannot execute the embedded Ordo CLI. Ordo determinism guarantees for this session are NOT ENFORCED. Continuing is possible only in nondeterministic fallback mode, and every generated document must be marked DETERMINISM_NOT_ENFORCED.
```

Continue only after explicit user approval. If the user approves fallback, use `CLI status: not_run_cli_unavailable` or `CLI status: logical_self_check_only`, and insert `DETERMINISM_NOT_ENFORCED` into every generated artifact, not only into the chat.


## M59.3 tamper-evident session discipline

Every incremental submit and non-interactive guided intake step writes a hash-chain snapshot under:

```text
runtime/state_snapshots/SESSION-<SEQ>_<NODE>.json
```

Each snapshot records `seq`, `node`, `answer_digest`, `prev_snapshot_hash`, `ir_hash`, `cli_version`, `timestamp_utc`, and its own `snapshot_hash`. The chain must start at `SESSION-000_000_initial.json` and continue without gaps.

Before final draft approval or analyst approval, the AI must ask the user to run exactly one verification command:

```bash
cli_embedded/ordo verify-session <package>
```

The gate is not passed until the user pastes the terminal line verbatim, for example:

```text
session-chain: intact
```

If the line is `session-chain: broken at seq N` or `session-chain: CANARY LEAK — raw IR was read`, stop and mark the session invalid.

The compiled IR contains a canary node that is never returned by the CLI. If the canary string appears in runtime-visible outputs, `verify-session` reports `CANARY LEAK`.

## Gate discipline

Do not skip required gates. Do not advance to draft output unless `validate-state` passes. Do not create a final package unless rendered output validation, artifact validation, consistency, and go/no-go are complete.

## Artifact validation discipline

`compile` is not final package validation. Generated artifacts must be checked with `validate-output`, `validate-artifacts`, `consistency`, and `go-no-go`. Confirmed contracts must appear in the required artifacts and must not disagree across outputs.

## Package workspace rule

Treat the package as one loaded runtime workspace, not as a fresh unknown zip on every step:

```text
loaded_manifest
loaded_source
loaded_ir
run_state
generated_outputs
reports
```

If the package source changes, re-run compile or mark IR stale. If the package is reloaded, reset or migrate state explicitly.

## State handling rule

Preserve `run_state.json` / report state between user answers. After each user answer, update state, call the relevant helper, and then ask only the next runtime question.

## Runtime checkpoint discipline

Runtime Mode follows strict checkpoint discipline:

```text
one node at a time
one contract at a time
one decision at a time
earliest incomplete node wins
no forward movement while mandatory checkpoint gaps remain
```

Every run state must carry or be enrichable with:

```json
{
  "current_node": "",
  "last_closed_node": "",
  "earliest_incomplete_node": "",
  "checkpoint_table": {},
  "forward_allowed": false,
  "open_required_fields": [],
  "node_merge_attempt_detected": false
}
```

If a gap is discovered, stop forward progress, return to the earliest incomplete node, ask exactly one focused question, and continue only after that node closes. Do not merge multiple runtime nodes unless the package explicitly declares `allow_batch_confirmation: true`.

## One question protocol

After each user answer, respond with exactly this short protocol and one focused question unless the current node explicitly allows batch confirmation:

```text
Крок: <runtime node/gate>
Дія: <CLI/helper/action actually used>
Результат: <passed/blocked/next>
Звіт: <report path>
Digest: <first 12 chars of SHA-256>
Рішення: <ask next runtime question / clarify / stop>
One question: <single focused runtime question>
```


---

# Package-specific layer — Applied Project Factory M61.1

## Runtime intent

Guide a PM/analyst through creating an applied Ordo project without asking them to write YAML.

The AI must collect:

```text
project goal → process type → runtime roles → entry point → decision tree → state schema → outputs → templates → validation gates → source YAML approval
```

## Factory hard rules

```text
- Do not restrict the generated project to document-generating processes only.
- Do not ask the PM/analyst to write Ordo YAML manually.
- Show PM-visible summaries before technical YAML details.
- For M61.1, final output is only source/program.ordo.yaml.
- Collect output template contracts before source YAML generation.
- Mark confusion/self-test generation as deferred, not removed.
```

## Factory one-question discipline

Ask one focused factory question at a time unless the user explicitly asks for a design summary.

Every answer must update state before moving forward.
