# Self-check Repair 1 — Runtime Contract Hygiene

Status: `repaired_passed`

## Finding

M71.4 normative prompt-application trace schema/example were stored under `packages/history_event_guided_intake/runtime/contracts/`, while repository source hygiene reserves `runtime/` for generated runtime artifacts.

## Repair

Moved without semantic changes:

- `runtime/contracts/prompt_application_trace.schema.json` → `source/contracts/runtime/prompt_application_trace.schema.json`
- `runtime/contracts/prompt_application_trace.example.json` → `source/contracts/runtime/prompt_application_trace.example.json`

Updated active tests and documentation references. Historical M71.4 reports remain unchanged as audit records. The repository hygiene policy was not weakened.

## Validation

- M71.4 focused tests: 6 passed
- History Event package strict clean-check: passed, 43 checks, 0 warnings, 0 errors
- Repository strict clean gate with fail-on-warning: passed, exit code 0
- Generated artifact hygiene: passed

## Untouched

Business navigation, confirmed-event logic, state model, compiler, opcodes, compiled IR, core CLI session-trace writer, and repository hygiene policy.
