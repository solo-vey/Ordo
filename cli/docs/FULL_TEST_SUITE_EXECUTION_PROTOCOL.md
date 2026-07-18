# Full Test Suite Execution Protocol

## Purpose

Run the complete CLI regression suite without confusing a tool-call/output limit with a hanging test.

## Required mode

The canonical interactive-agent command is:

```bash
python cli/scripts/run_full_suite_partitioned.py
```

The launcher:

1. discovers every `cli/tests/test_*.py` file;
2. runs each test file in a separate subprocess;
3. records duration and output tail per file;
4. continues after a failure so the full surface is measured;
5. writes `reports/FULL_TEST_SUITE_PARTITIONED_REPORT.json`;
6. returns non-zero if any test file fails.

## Interpretation rule

A tool-call ending early is not evidence that pytest is hanging.

Before declaring a hang:

```text
collect succeeds
→ run the suspected file separately
→ run its individual tests if necessary
→ inspect subprocess exit code and log
→ only then classify as timeout or hang
```

## CI

CI may continue to run a normal single `pytest` process when the CI runner has no short interactive-call limit. Partitioned mode is the required fallback for constrained chat/tool environments.
