# Delivery Policy (M87.7)

Status: normative

## The rule

The project archive may be produced **only** by:

```
python3 tools/build_release_archive.py --out <archive.zip>
```

Manual zipping of the working tree is forbidden. The script:

1. runs the full CLI test suite (partitioned per file);
2. lints every package under `packages/`;
3. verifies backlog/maturity manifest synchronization (`.md` == `.json`);
4. verifies root hygiene (no milestone reports in root);
5. **refuses to build** while any check is red (`reports/delivery/current/DELIVERY_GATE_REPORT.json` records why);
6. on green, regenerates `FINAL_PACKAGE_SELF_CHECK_REPORT.{json,md}` from the
   actual current tree — the self-check can therefore never be stale by
   construction.

## Why

Three consecutive releases (M43, M83.0, CURRENT-2026-07-12 pre-patch) shipped
red: broken CI paths, 62 then 14 failing tests, a NameError in shipped code,
and a stale hand-written self-check each time. Every one of those defects was
already caught by existing checks — the archive was simply produced without
running them. This policy closes delivery onto the project's own gate.

## Performance budget

The APF lint is mandatory on every runner and must fit the standard-CI budget of 512 MiB peak RSS and 15 seconds. The legacy `--skip-heavy` flag is accepted only for command compatibility and does not skip tests or package lints.

## Timeout policy

The delivery gate defaults to 3600 seconds for each test partition and each package lint.

For slower machines:

```bash
python3 tools/build_release_archive.py --check-only   --test-timeout-seconds 7200   --lint-timeout-seconds 7200
```

To disable the script's internal timeouts completely:

```bash
python3 tools/build_release_archive.py --check-only   --test-timeout-seconds 0   --lint-timeout-seconds 0
```

A value of `0` disables only the gate's internal subprocess timeout. Operating-system,
CI-job, shell, container, or hosting-platform time limits can still terminate the run.
