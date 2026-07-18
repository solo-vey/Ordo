# 029. Comparative Matrix

**Version:** `1.0`  
**Backlog:** `BL-BENCH-029`  
**Status:** canonical contract

## 1. Purpose

The Comparative Matrix is a deterministic derived view over active comparable registry records. It is not a second source of truth and must be reproducible from the Benchmark Result Registry.

## 2. Canonical row key

Default row granularity:

```text
test_case_id × run_id × package_variant_id × package_version × attempt_id
```

Views may group by variant or test case, but grouped values must preserve drill-down to source records.

## 3. Required columns

- test case and version;
- RUN and contract version;
- package variant and package version;
- Driver and version;
- attempt and execution timestamp;
- terminal disposition;
- blind-isolation/contamination status;
- process raw and final scores;
- Passport, Jira, Implementation Prompt, Manual QA and Automation scores with `N/A` states;
- aggregate document score and formula version;
- overall score and formula version, if approved;
- applied process/document caps;
- comparability status;
- registry record ID and evidence links.

## 4. Missing-data semantics

The matrix must distinguish:

- `N/A` — artifact not applicable by contract;
- `NP` — artifact correctly not produced for the terminal path;
- `PE` — pending evaluation;
- `MB` — missing blocking artifact;
- `EX` — excluded from comparison;
- numeric score — completed evaluation.

No missing state may be converted to zero unless an active scoring contract explicitly requires that conversion.

## 5. Derived views

The package defines these standard views:

1. `attempt_detail` — one row per attempt;
2. `variant_summary` — comparable attempts grouped by package variant;
3. `run_summary` — grouped by RUN scenario;
4. `artifact_summary` — grouped by artifact type;
5. `stability_summary` — variance across repeated attempts;
6. `coverage_summary` — completed combinations against planned matrix.

## 6. Aggregation rules

- arithmetic mean is allowed only over homogeneous comparable records;
- sample count must always be shown;
- variance/dispersion must be shown when repeated attempts exist;
- capped and uncapped values must not be mixed;
- records from different evaluation contract versions require either normalized migration or separate cohorts;
- rank ordering is prohibited when comparability status is not `comparable`.

## 7. Regeneration

Every matrix carries:

- `matrix_build_id`;
- registry high-water mark/event hash;
- active policy versions;
- filters;
- generated timestamp;
- included and excluded record counts.

Any registry append that changes active records triggers a new build; older matrices remain historical derived artifacts.

## 8. Templates

- `templates/COMPARATIVE_MATRIX.template.csv` — standard columns;
- `templates/COMPARATIVE_MATRIX_BUILD.template.json` — reproducibility metadata;
- `schemas/comparative_matrix_build.schema.json` — metadata validation.
