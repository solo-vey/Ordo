# SELF_CHECK-004 — Runtime prompt limit and test isolation repair

Status: `repaired_passed`

## Changes

- Increased the maximum `START_PROMPT_RUNTIME_MODE.md` size from 90 to 256 words.
- Applied the same limit to the core CLI and both embedded CLI copies.
- Changed the dependency-lock workflow test to run against a temporary package copy.
- The test no longer leaves `lock_report.json` or `lock_validation_report.json` in the source package.

## Validation

- Focused regression: 2 passed.
- All 13 test files passed in isolated groups.
- Total: 147 tests passed plus 10 subtests.
- `test_cli_workflow.py`: 85 passed.
- Generated lock reports left in source package: none.
- Strict repository gate with `--fail-on-warning`: passed.

## Scope

No navigation, state, compiler, opcode, or business-contract behavior was changed.
