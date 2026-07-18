# Chapter 55. Ordo-code Runtime View

`ordo-code-view` is an AI-facing projection that presents the runtime contract as a code-like fragment. It is not designed for a human developer. Its purpose is to help the model see the process as a strict contract rather than as free-form JSON.

## Example

Instead of exposing raw JSON to the model, the CLI can return:

```ordo
node N_PATH_SELECT {
  kind: branch
  answer_type: enum

  allowed {
    A -> N_EVENT_ALIAS
    B -> N_EVENT_ALIAS
    C -> N_EVENT_ALIAS
    D -> N_EVENT_ALIAS
  }

  reject unless answer in [A, B, C, D]

  evidence required:
    next_step_report
    intake_submit_report
    runtime_evidence
}
```

This fragment is harder for the model to “interpret freely”: it is clear that only A/B/C/D are allowed, any other answer must be rejected, and progression without evidence is not allowed.

## Why this is not Java or Python

Ordo-code is intentionally not a general-purpose language. It has no imports, loops, side effects, or arbitrary logic.

Its role is to be:

```text
code-like
strict
readable by the model
limited to the Ordo state machine
derived from JSON IR
```

## How the model should receive it

Legal:

```bash
cli_embedded/ordo next-step . --format auto
cli_embedded/ordo next-step . --format ordo-code
cli_embedded/ordo render-runtime-view . --format ordo-code --node <NODE_ID>
```

Illegal:

```text
open compiled/program.ordo.view directly
read compiled/program.ir.json directly
reproduce compiled/* in the chat
```

In Runtime Mode, all `compiled/*` files belong to the CLI.

## Runtime view modes

M60.3 allows a runtime package to be created in three modes:

```bash
ordo package . --profile runtime --runtime-view json
ordo package . --profile runtime --runtime-view ordo-code
ordo package . --profile runtime --runtime-view json,ordo-code
```

In `json` mode, `next-step --format auto` returns a normal report without a code-like block.

In `ordo-code` mode, `next-step --format auto` automatically returns `current_contract`.

In `json,ordo-code` mode, either format can be selected explicitly.

## Why this matters

The purpose of Ordo-code view is not to create another runtime. The purpose is to improve model behavior:

```text
fewer invented transitions;
less free interpretation of allowed answers;
better correlation between the compiled project and model responses;
a visible contract fragment at every step.
```

The source of truth does not change:

```text
JSON IR decides.
Ordo-code explains.
```
