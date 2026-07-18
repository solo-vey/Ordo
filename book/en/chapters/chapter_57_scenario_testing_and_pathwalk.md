# Chapter 57. Scenario Testing and PathWalk

In the previous chapters, we added several verification layers to the Ordo runtime package:

```text
CLI-enforced runtime
per-node evidence
hash-chain snapshots
verify-session
multi-target compilation
Ordo-code runtime view
session-trace proof program
```

These answer the question:

```text
Does a specific runtime run have evidence, and can it be verified?
```

But there is another question:

```text
Does the model behave correctly and consistently across many different scenarios?
```

That requires a separate testing layer. One possible approach is **PathWalk**.

## What scenario testing is

A normal CLI unit test checks a command:

```text
next-step works
intake --submit accepts a correct answer
verify-session detects a damaged trace
```

Scenario testing checks not a command, but the behavior of the model as a whole:

```text
the model receives a runtime package
the model must call next-step
the model asks the user a question
the user or test scenario provides an answer
the model submits the answer through the CLI
the CLI writes evidence, snapshot, and trace
the model moves forward only after an accepted submit
```

Scenario testing therefore answers a practical question:

```text
Is the model actually following the Process Rail, rather than merely saying that it is?
```

## What PathWalk is

PathWalk is a companion utility or benchmark approach for checking traversal of Ordo scenarios.

It can:

```text
create a test decision tree
generate a ground-truth path
let the model walk that path
add noise, clarifications, or incorrect answers
inspect actual runtime artifacts after the run
calculate a score
```

PathWalk is not part of the Ordo core. It is an external or companion layer.

Its purpose is not to replace the runtime CLI, but to test whether the model uses it.

## Why model self-report cannot be trusted

A model can write:

```text
CLI executed and passed.
```

By itself, this proves nothing.

After M59/M60, the evidence is in files:

```text
reports/next_step_report.json
reports/intake_submit_report.json
runtime/evidence/*_evidence.json
runtime/state_snapshots/*.json
runtime/session.ordo.trace
reports/target_verification_report.json
reports/session_verification_report.json
```

PathWalk must inspect these files.

Otherwise, we return to the old problem:

```text
the model said it completed everything correctly
but nobody verified that the CLI was actually invoked
```

## How PathWalk should work with an M60 runtime package

In enforced mode, PathWalk should give the model only the runtime CLI protocol.

A typical cycle is:

```bash
./cli_embedded/ordo runtime-status .
./cli_embedded/ordo verify-targets .
./cli_embedded/ordo next-step . --format auto
./cli_embedded/ordo intake . --submit <NODE_ID> --answer-file <answer-file>
./cli_embedded/ordo verify-session .
```

The model must not directly read:

```text
compiled/program.ir.json
compiled/program.ordo.view
compiled/targets.manifest.json
```

Even `program.ordo.view` is an AI-facing projection, but it must be delivered through the CLI rather than by direct file reading.

## How PathWalk relates to the three M60 targets

M60 has a simple formula:

```text
JSON IR decides.
Ordo-code explains.
Session-trace proves.
```

PathWalk should use it this way:

```text
JSON IR
  is not read directly by the model, but is the canonical runtime contract for the CLI.

Ordo-code view
  can be shown to the model through next-step --format auto or render-runtime-view.

Session-trace
  is verified after the run as the proof program of actual accepted decisions.
```

PathWalk does not create a new source of truth. It verifies whether the model works correctly with the existing sources of evidence.

## Modes worth comparing

PathWalk is especially useful when several modes are compared:

```text
enforced + json
enforced + ordo-code
enforced + json,ordo-code
ir_readable baseline
freeform baseline
```

For example, we can check:

```text
whether the model makes more mistakes in json-only mode
whether Ordo-code view helps it keep allowed answers more accurately
whether mixed mode provides better stability
whether freeform mode drifts from the decision tree faster
```

This is no longer merely a test of Ordo. It is a measurement of model behavior.

## What PathWalk should evaluate

One overall score is not enough. It is better to separate evaluation:

```text
path correctness
  whether the final path matched the expected path

protocol compliance
  whether the model invoked the CLI every time

runtime integrity
  whether verify-targets and verify-session passed

compiled-read violations
  whether the model attempted to read compiled/* directly

robustness
  whether the model handled clarifications, noise, incorrect answers, or corrections
```

This matters because a model may reach the correct final node in the wrong way.

For Ordo, the correct method matters too.

## Backtracking and restore-session

In guided intake, real users often change their minds:

```text
no, let's go back
I made a mistake in the previous answer
choose another branch
```

This is a natural scenario. But as of M60.3, `restore-session` is not yet a mandatory runtime command.

PathWalk can therefore test simple corrections when the tree itself supports them. Full rollback is better implemented as a separate future layer:

```text
restore-session must be append-only
it must write evidence
it must write a trace event
it must be checked by verify-session
it must not silently delete history
```

Backtracking matters, but it should not become chaotic manual state editing.

## What PathWalk must not do

PathWalk must not:

```text
replace the embedded CLI
create evidence reports itself on behalf of the CLI
encourage the model to read compiled/*
calculate success only from the model's response text
treat protocol bypass as acceptable when the final answer looks correct
```

A test utility that does these things may be useful as a baseline, but not for enforced-runtime verification.

## Summary

The runtime CLI verifies one specific run.

PathWalk verifies whether the model consistently completes many different scenarios.

In a correct architecture, they do not compete:

```text
The Ordo runtime package provides rules and evidence.
PathWalk provides an experiment on model behavior.
```

That is why PathWalk should be documented as a separate companion testing layer rather than as part of the language core.

## M60.3.2: why bare intake is forbidden in benchmark automation

A scenario runner must not invoke the CLI like this:

```bash
./cli_embedded/ordo intake .
```

That invocation means: “run guided intake and, if there is no answer, ask through `input()`.” This is normal for a human in a terminal. It is dangerous for a subprocess or benchmark worker because the process can hang.

Starting with M60.3.2, the Ordo runtime CLI must behave as follows:

```text
no --submit
no --answers
no --non-interactive
stdin is not a TTY
        ↓
fail fast
reason: no_answers_and_not_interactive_and_no_tty
```

For PathWalk, this means one simple rule:

```text
in benchmark automation, always use an explicit mode:
- intake --submit ...
- or intake --answers ... --non-interactive
```

Likewise, `next-step` should give the model a short current fragment rather than the full internal checkpoint table. Full details may exist in the report file, but the model should not receive unnecessary runtime noise in stdout.
