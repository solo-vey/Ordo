# Ordo Quickstart

Run every command from the repository root. Python 3.10 or newer is required.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ./cli
```

## Golden example 1: package validation

```bash
python tools/run_golden_examples.py --example package-validation
```

This runs `lint`, `compile`, `test`, and `coverage` against a temporary copy of `packages/ordo_project_builder`.

## Golden example 2: Process Rail next step

```bash
python tools/run_golden_examples.py --example process-rail-next-step
```

This validates the canonical authoring answers and asks Ordo for the next deterministic step.

## Golden example 3: end-to-end output gate

```bash
python tools/run_golden_examples.py --example history-event-output-gate
```

This runs the non-interactive intake and output-validation flow against a temporary package copy.

## Run all CI-backed examples

```bash
python tools/run_golden_examples.py --all
```

The manifest at `examples/golden_examples.json` is the source of truth for the commands. CI executes the same runner and fails when documentation, manifest, or behavior diverge. Generated package outputs remain inside temporary directories and are deleted after each run.
