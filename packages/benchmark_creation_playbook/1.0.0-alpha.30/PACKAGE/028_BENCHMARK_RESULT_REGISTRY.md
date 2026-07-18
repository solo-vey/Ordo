# 028. Benchmark Result Registry

**Version:** `1.0`  
**Backlog:** `BL-BENCH-028`  
**Status:** canonical contract

## 1. Purpose

The Benchmark Result Registry is the append-only source of truth for completed or dispositioned benchmark attempts. It stores execution identity, process evaluation, artifact evaluations, comparability status and provenance without silently overwriting historical results.

## 2. Canonical result identity

A result record is uniquely identified by:

```text
benchmark_suite_id
× test_case_id + test_case_version
× run_id + run_contract_version
× package_variant_id + package_version
× driver_id + driver_version
× attempt_id
× process_evaluation_contract_version
× document_evaluation_contract_versions
```

`attempt_id` is immutable and must match the launch, preflight, execution log and terminal disposition evidence.

## 3. Registry record classes

- `attempt_result` — one executed attempt with terminal disposition and scores.
- `supersession_event` — declares that a newer evaluation or rerun supersedes a prior active record.
- `comparability_event` — marks a record comparable, conditionally comparable or excluded.
- `recalculation_event` — records regeneration of derived matrices after registry change.

The registry is append-only. Existing records may not be edited in place except for cryptographically equivalent storage migration with an audit entry.

## 4. Required result fields

Every `attempt_result` must contain:

- stable identity fields and versions;
- timestamps and evaluator identity/class;
- terminal disposition and blind-isolation status;
- process raw score, applied caps and final process score;
- one document evaluation reference per artifact actually produced;
- aggregate document score with explicit aggregation rule;
- overall score only when an approved overall formula exists;
- evidence references and checksums;
- comparability status and exclusion reasons;
- lifecycle status: `active`, `superseded`, `invalidated`, `quarantined`.

Missing artifact evaluations are not silently treated as zero. They must be represented as `not_produced`, `not_applicable`, `missing_blocking` or `pending_evaluation`.

## 5. Score separation

The registry preserves three independent layers:

```text
process_final_score
artifact_final_scores
approved_aggregate_scores
```

Process and document scores must remain independently inspectable. An overall score may not erase either component.

## 6. Registry files

Canonical machine-readable storage:

- `BENCHMARK_RESULT_REGISTRY.jsonl` — append-only event ledger;
- `templates/BENCHMARK_RESULT_RECORD.template.json` — reusable record shape;
- `schemas/benchmark_result_record.schema.json` — structural validation;
- `RESULT_REGISTRY_POLICY.yaml` — lifecycle and comparability policy.

The release package contains templates and policy, not fabricated benchmark results.

## 7. Gates

A record may become `active` only if:

1. identity and versions are complete;
2. terminal disposition evidence exists;
3. process evaluation validates against its active contract;
4. each claimed artifact evaluation validates against its bound artifact contract;
5. checksums resolve;
6. blind/contamination status is explicit;
7. comparability decision is recorded;
8. no existing active record has the same immutable `attempt_id`.

## 8. Prohibited behavior

- overwriting an older score after criteria change;
- merging several attempts into one record;
- comparing records with unknown contract versions;
- treating a contaminated run as clean;
- using latest file modification time as result identity;
- storing only the final number without evidence and cap history.
