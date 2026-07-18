# 017. Universal Launch Protocol

**Playbook version:** 0.6.0  
**Backlog task:** `BL-BENCH-017`  
**Status:** implemented contract; production launcher not claimed

## 1. Purpose

Define one reproducible launch envelope for every benchmark execution across test cases, RUN scenarios and package variants.

## 2. Canonical run identity

A launch is uniquely identified by:

```text
benchmark_suite_id × test_case_id × run_id × package_variant_id × package_version × attempt_id
```

`attempt_id` is immutable and must never be reused after a failed, cancelled or contaminated attempt.

## 3. Mandatory launch inputs

- benchmark suite and test-case contract version;
- canonical `RUN_ID` and RUN contract version;
- package variant and immutable package digest;
- Driver binding record and Driver contract version;
- executor model/provider identity when available;
- blind-isolation manifest;
- output directory reserved for this attempt;
- launch mode: `blind`, `diagnostic-nonblind`, or `replay`;
- explicit prohibition of executor self-scoring.

## 4. Launch sequence

```text
Create launch manifest
→ run preflight integrity gate
→ freeze launch identity and hashes
→ expose only executor-visible context
→ start Driver-mediated interaction
→ append execution evidence
→ obtain terminal disposition
→ seal return package
```

Execution must not start when preflight status is not `passed`.

## 5. Executor-facing launch instruction

The executor receives only:

- authorized package files;
- current Driver question/instruction;
- allowed output location and expected artifact names;
- prohibition on reading evaluator-only or Driver-private data;
- prohibition on scoring its own work;
- requirement to return generated artifacts and an execution completion declaration.

It must not receive expected terminal, score rubric, caps, golden outputs, prior results or root-cause analysis.

## 6. Expected return package

Required:

```text
LAUNCH_MANIFEST.yaml
PREFLIGHT_REPORT.json
EXECUTION_LOG.jsonl
TERMINAL_DISPOSITION.json
OUTPUT_MANIFEST.json
executor_outputs/
```

Optional only when declared by the package variant:

```text
interaction_transcript/
runtime_evidence/
```

Evaluator reports are downstream outputs and must not be placed into the executor return package.

## 7. Relaunch and replay

A retry creates a new `attempt_id`. Replay must reference the source attempt, preserve its sealed evidence and state why replay is permitted. It cannot silently overwrite prior evidence.

## 8. Failure rules

Launch is rejected if identity is incomplete, hashes are missing/mismatched, Driver binding is unsupported, isolation fails, output directory contains residue, or the selected RUN is unavailable.

## 9. Validation gate

Passed only when the launch manifest is complete, preflight passed, all exposed files are allowlisted, and the return package contract is fixed before executor interaction begins.
