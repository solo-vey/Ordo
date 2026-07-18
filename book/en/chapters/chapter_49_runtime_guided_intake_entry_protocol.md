# Chapter 49. Runtime Guided Intake Entry Protocol

The Runtime Guided Intake Entry Protocol prevents the model from starting guided intake “from memory” or through free-form file reading.

In early versions, runtime started through `START_HERE_RUNTIME_MODE.md`, `ordo.yml`, and compiled IR. After M59/M60, enforced Runtime Mode became stricter: a runtime package does not need source YAML, and the model does not read `compiled/*` files directly.

## Current route

```text
START_HERE_RUNTIME_MODE.md
→ cli_embedded/ordo runtime-entry .
→ cli_embedded/ordo next-step . --format auto
→ user answer
→ cli_embedded/ordo intake . --submit <NODE_ID> --answer-file <answer_file>
→ evidence + snapshot + session-trace
→ next CLI-rendered step
```

This means the model does not decide which node comes next. It receives the next step from the CLI.

## Why compiled IR must not be read directly

`compiled/program.ir.json` is the canonical machine target. In Runtime Mode, however, it belongs to the CLI, not to the model.

The model must not:

```text
open compiled/program.ir.json;
read compiled/program.ordo.view directly;
form questions from compiled/*;
quote compiled/* in chat.
```

The only legal sources are CLI commands:

```text
runtime-entry
next-step
next-step --format auto
next-step --format ordo-code
render-runtime-view
intake --submit
verify-targets
verify-session
```

## Short protocol after an answer

After every user answer, the AI must show a short runtime protocol:

```text
Step: <submitted node>
Action: intake --submit
Result: accepted / rejected / blocked
Evidence: <path> sha256=<digest>
Trace: runtime/session.ordo.trace sha256=<digest>
Decision: ask next / clarify / stop
```

Without evidence and a trace digest, the next question must not be asked.

## Runtime view

M60.3 adds `runtime_view`:

```text
json
ordo-code
json,ordo-code
```

In `json` mode, the AI sees a standard report. In `ordo-code` mode, `next-step --format auto` adds the current contract fragment. In mixed mode, both formats are allowed.

## Main formula

```text
JSON IR decides.
Ordo-code explains.
Session-trace proves.
```

This protocol does not replace `validate-state`, `validate-output`, `validate-artifacts`, `consistency`, `go-no-go`, or `verify-session`. It defines the correct start and cycle for guided intake.
