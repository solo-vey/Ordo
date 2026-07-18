# M53 Runtime Source-of-Truth Report

M53 adds runtime readiness and truthfulness controls to the Ordo Developer Bundle.

## Changed areas

- `cli/ordo/runtime.py`
- `cli/ordo/helpers.py`
- `cli/ordo/cli.py`
- `cli/tests/test_cli_workflow.py`
- `language/RUNTIME_MODEL.md`
- `language/RUN_STATE.md`
- `language/CLI_TRUTHFULNESS.md`
- `cli/docs/CLI_WORKFLOW.md`
- `cli/docs/VALIDATE_OUTPUT.md`
- `book/source/chapters/chapter_48_runtime_source_of_truth.md`

## New behavior

- Helper commands block on missing/stale IR.
- `next-step` is based on compiled IR instead of editable YAML.
- `generate-output` requires prior `validate-state` unless overridden.
- `package` requires prior `validate-output` unless overridden.
- CLI truthfulness claims are machine-checkable.

## Known limitations

- The runtime helper reconstructs the Process Rail helper view from IR for nodes/gates/state/outputs; it does not execute an AI model.
- `validate-cli-status` checks report evidence shape, not the external terminal history.
- Live REST/Mongo/project business code is still out of scope.
