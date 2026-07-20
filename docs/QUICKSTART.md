# Ordo Quickstart

Run every command from the repository root. Python 3.10 or newer is required.

## Check Python

```bash
python3 --version
```

Continue only when the reported version is `3.10` or newer. On macOS, the Xcode-provided `python3` may be older. Use an installed interpreter such as `python3.11` consistently for both venv creation and later commands when needed.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ./cli
```

## Validate an Ordo package

```bash
python tools/run_golden_examples.py --example package-validation
```

This runs `lint`, `compile`, `test`, and `coverage` against a temporary copy of `packages/ordo_project_builder`.

## Find the next Process Rail step

```bash
python tools/run_golden_examples.py --example process-rail-next-step
```

This validates the canonical authoring answers and asks Ordo for the next deterministic step.

## Validate an end-to-end output gate

```bash
python tools/run_golden_examples.py --example history-event-output-gate
```

This runs the non-interactive intake and output-validation flow against a temporary package copy.

## Run every CI-backed example

```bash
python tools/run_golden_examples.py --all
```

## Expected result

A successful command:

- exits with status code `0`;
- reports the selected golden scenario as passed;
- leaves generated package outputs only in temporary directories;
- cleans those temporary directories after the run.

The manifest at [`../examples/golden_examples.json`](../examples/golden_examples.json) is the source of truth for the commands. CI executes the same runner and fails when documentation, manifest, or behavior diverge.

Continue with the [`documentation map`](README.md).
