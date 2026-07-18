# M68.2 — Clean-Check Output / Exit-Code Hardening Report

Status: `implemented-hardening / passed-cli-validation`

## Scope

M68.2 hardens the existing `ordo clean-check` implementation by stabilizing the machine-readable report surface and by making exit-code semantics explicit in the report itself.

## Changed files

Implementation:

```text
cli/ordo/clean_check.py
cli/tests/test_clean_check_fixtures.py
```

Documentation / reports:

```text
cli/docs/CLEAN_CHECK_COMMAND.md
cli/docs/CLEAN_CHECK_HARDENING_PLAN.md
M68_2_CLEAN_CHECK_OUTPUT_EXIT_CODE_HARDENING_REPORT.md
M68_2_CLEAN_CHECK_OUTPUT_EXIT_CODE_HARDENING_REPORT.json
M68_2_VALIDATION_REPORT.json
language/improvement_intake/m68_2/*
```

Index updates:

```text
README.md
CHANGELOG.md
STABLE_PACKAGE_INDEX.md
language/README.md
language/CHANGELOG.md
language/VALIDATION_REPORT.json
```

## Behavior hardened

The clean-check report now includes:

```text
schema_version
profile_requested
profile
fail_on_warning
exit_code
expanded summary counters
exit_policy
```

The top-level JSON key order is fixture-tested for stability. Programmatic invalid profile input is reported as a warning and falls back to the effective `standard` profile instead of crashing or silently disappearing.

## Exit-code policy

```text
passed + any fail_on_warning setting => 0
passed_with_warnings + fail_on_warning false => 0
passed_with_warnings + fail_on_warning true => 1
blocked => 1
```

## Non-changes

M68.2 does not regenerate runtime artifacts, lockfiles, compiled IR, or embedded CLI bundles. It does not change applied packages, runtime core, compiler behavior, or opcodes.
