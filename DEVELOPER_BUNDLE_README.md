# M62.2 — APF Documentation and Book Section

M62.2 documents `ordo.applied_project_factory` as a standard applied module and explains the APF + Visual Graph + PathWalk review route.

Start here:

- `APF_STANDARD_MODULE_GUIDE.md`
- `APF_COMPANION_WORKFLOW.md`
- `STANDARD_APPLIED_MODULES.md`
- `packages/ordo_applied_project_factory/docs/APF_STANDARD_MODULE_GUIDE.md`
- `M62_2_APF_DOCUMENTATION_AND_BOOK_SECTION_REPORT.md`

M62.2 is documentation-only: no APF branch rewrite, no runtime-core changes, no IR/opcode additions, and no runtime execution/scoring.

---

# M62.1 — APF Package Import

M62.1 imports `ordo.applied_project_factory` v0.1.0-alpha.14 into the current Ordo language package as a **standard applied module**:

```text
packages/ordo_applied_project_factory/
```

APF is the self-hosted authoring package for creating or improving Ordo playbooks/process packages. It is not a companion utility and not runtime core.

Start here:

- `APF_PACKAGE_IMPORT.md`
- `STANDARD_APPLIED_MODULES.md`
- `packages/ordo_applied_project_factory/README.md`
- `packages/ordo_applied_project_factory/ORDO_PARENT_PACKAGE_IMPORT.md`

M62.1 is an import milestone only: APF branch logic, runtime-core semantics, scoring, calibration, and language IR/opcodes are unchanged.

---

# M62.0 — APF Integration Correlation Plan

M62.0 starts the Applied Project Factory integration line after M61 Companion Utilities Line Closure. It is docs/design-only: APF is correlated and classified as a future standard applied module import target, but APF code is not imported yet.

Start here:

- `APF_INTEGRATION_CORRELATION_PLAN.md`
- `STANDARD_APPLIED_MODULES.md`
- `APF_LANGUAGE_PATTERN_CANDIDATES.md`
- `M62_0_APF_INTEGRATION_CORRELATION_PLAN_REPORT.md`

Next planned milestone: `M62.1 — APF Package Import into Current Language Package`.

---

# M61 Line Closure

M61 is closed as the stable companion-utility line. Use the M61 Line Closure archives for handoff when the user needs the complete Visual Graph + PathWalk workflow. Runtime execution, scoring, calibration, and additional noise variants remain future work.

See `M61_LINE_CLOSURE_REPORT.md` and `M61_COMPANION_UTILITIES_LINE_CLOSURE.md`.

---

# Ordo Workspace — M61.3 Utility Documentation Consolidation

M61.3 consolidates the included companion utilities into one stable author/reviewer route. It adds `COMPANION_UTILITY_WORKFLOW.md` and mirrors it under `utilities/` and `docs/`.

Primary workflow:

```text
source/program.ordo.yaml
  → Visual Graph Generator: inspect graph visually
  → PathWalk: graph summary, terminal paths, clean/noise cases, review cards
  → Visual Graph annotation overlay: optional comments/highlights
```

M61.3 is docs-only. Runtime execution of generated testcases, scoring, calibration, benchmark orchestration, and watchdog hardening remain future work.

Start here:

- `COMPANION_UTILITY_WORKFLOW.md`
- `COMPANION_UTILITIES.md`
- `utilities/README.md`
- `utilities/ordo_visual_graph_generator/README.md`
- `ordo_pathwalk/REAL_MODULE_TESTCASE_GENERATION.md`

---

# M61.1 Developer Bundle Note

This bundle includes the companion utilities packaging plan. PathWalk remains the included utility. Visual Graph Generator is planned for a later import under `utilities/ordo_visual_graph_generator/` and is not included in M61.1.

---

## M60.8 Stable Developer Handoff Consolidation

M60.8 is the current stable developer bundle handoff. It adds package-selection guidance, a stable quickstart, and a future backlog. It does not change runtime semantics, scoring weights, or PathWalk generator behavior.

Start with:

- `STABLE_DEVELOPER_HANDOFF.md`
- `STABLE_PACKAGE_INDEX.md`
- `FUTURE_BACKLOG.md`

## M60.6.2 Calibration Report Refinement

M60.6.2 refines the calibration-preparation analysis from the M60.6/M60.6.1 artifact-only dry-run evidence.

Key decision:

```text
Do not change path_quality_score weights from M60.6 dry-run data.
```

Reason: the M60.6 dry-run baseline is fully saturated (`60/60` passed; all component metrics are `1.0`), so it is valid readiness evidence but has zero variance and cannot support weight calibration.

Added artifacts:

- `M60_6_2_CALIBRATION_REFINEMENT_REPORT.md`
- `M60_6_2_CALIBRATION_REFINEMENT_REPORT.json`
- `M60_6_2_VALIDATION_REPORT.json`
- `reports/m60_6_2_calibration_refinement/*.csv`

M60.6.2 does not change runtime-core semantics, default scoring weights, or the PathWalk execution contract.

# Ordo Developer Bundle — M59.3

Use `language/` as the language source, `cli/` as deterministic helper layer, and `packages/` as canonical examples/regression packages.

M55 standardizes Runtime Mode start files for all subject packages:

```text
START_HERE_RUNTIME_MODE.md      # full runtime rules inside the package
START_PROMPT_RUNTIME_MODE.md    # minimal prompt only
reports/CLI_VALIDATION_SUMMARY.md
```

Do not paste the full runtime protocol into every user prompt. The prompt should tell the AI/runner to read `START_HERE_RUNTIME_MODE.md` and start runtime loading.

Primary commands:

```bash
ordo runtime-status <package>
ordo lint <package>
ordo compile <package>
ordo test <package>
ordo coverage <package>
ordo runtime-entry <package>
ordo next-step <package> --state run_state.json
ordo intake <package> --submit <NODE_ID> --answer "<answer>" --state run_state.json
ordo check-gate <package> <GATE_ID> --state run_state.json
ordo validate-state <package> --state run_state.json
ordo generate-output <package>
ordo validate-output <package>
ordo validate-artifacts <package>
ordo consistency <package>
ordo go-no-go <package>
ordo validate-cli-status <report.json>
ordo verify-session <package>
```

CLI status must be one of: `executed_cli_passed`, `executed_cli_failed`, `logical_self_check_only`, `not_run_cli_unavailable`, `not_run_user_skipped`.

## M56 package build profiles

Ordo subject packages now distinguish three build profiles:

```bash
ordo package <package> --profile dev --out <zip>
ordo package <package> --profile runtime --out <zip>
ordo package <package> --profile evidence --out <zip>
```

- `dev` is the full editable package with source YAML, tests, run inputs, templates, reports, and development material.
- `runtime` is the clean guided-execution package. It uses `compiled/program.ir.json` as the primary runtime source and excludes `source/`, `tests/`, `run_inputs/`, `domain/`, generated outputs, state snapshots, and release zips.
- `evidence` contains validation/provenance/hash reports only.

Runtime packaging creates `ordo.runtime.json`, `reports/BUILD_MANIFEST.json`, and `reports/SHA256SUMS.txt`. The runtime package records the source YAML hash even though editable YAML is not included.

## M57 Runtime Checkpoint Discipline

Runtime Mode now enforces a checkpoint layer: one node, one contract, and one decision at a time. Helper reports expose `checkpoint_table`, `earliest_incomplete_node`, `open_required_fields`, and `forward_allowed`. `next-step` prioritizes the earliest incomplete node, and `generate-output` is blocked while checkpoint gaps remain. Detailed rules live in `language/RUNTIME_CHECKPOINTS.md` and package `START_HERE_RUNTIME_MODE.md`; minimal runtime prompts stay minimal.



## M59.1 — CLI-enforced runtime package

Runtime packages now include `cli_embedded/ordo`. Use that embedded CLI for Runtime Mode instead of relying on model memory or direct IR reading. If the embedded CLI cannot run, hard-stop; fallback requires explicit user approval and `DETERMINISM_NOT_ENFORCED` markers in generated files.

## M59.2 — Incremental intake evidence reports

Runtime intake can now advance exactly one node with:

```bash
ordo intake <package> --submit <NODE_ID> --answer "<answer>" --state run_state.json
```

Each submit writes `reports/intake_submit_report.json`, `runtime/evidence/*_evidence.json`, a state snapshot, and SHA-256 digests. The embedded runtime CLI supports this command inside source-free runtime packages, using `compiled/program.ir.json` as the runtime source.



## M59.3 — Tamper-evident runtime session

Runtime sessions now write hash-chain snapshots under `runtime/state_snapshots/SESSION-*.json`. Use:

```bash
ordo verify-session <package>
```

The successful terminal line is `session-chain: intact`. Broken chains report `session-chain: broken at seq N`; canary leaks report `session-chain: CANARY LEAK — raw IR was read`. Final runtime approval requires a human-run verify-session line, not an AI paraphrase.

## M60.3.2 runtime CLI safety note

This bundle includes the M60.3.2 safety patch: bare `intake <package>` fails fast in non-TTY automation unless `--submit`, `--answers`, or `--non-interactive` is provided. Scenario-testing utilities should use explicit `intake --submit ... --answer-file ...` or `intake --answers ... --non-interactive`.

## M60.6 developer-bundle note

This bundle includes the M60.6 PathWalk calibration-preparation baseline. The dry-run evidence is compact and artifact-only: `DRY_RUN_PLAN.json`, `jobs/*.json`, `job_scripts/*.sh`, `scores/*_score.json`, `RAW_METRICS.csv`, `SUMMARY.json`, and `SUMMARY.md`. Default scoring weights were not changed.

## M60.6.4 transcript replay pilot

This bundle includes PathWalk v9.6.4 transcript-replay pilot support. Use `model-benchmark-pilot` for a no-API protocol pilot and `model-benchmark-collect` to regenerate `SUMMARY.*` and `CALIBRATION_DECISION.*` from `MODEL_BENCHMARK_PLAN.json`. This does not change runtime-core semantics or scoring weights.


## M60.7 Line Closure

M60.7 is closed at stable M60.7.5 as an artifact-only Real Module Testcase Generation line. Do not continue adding noise variants by default. Supported artifact-only noise patterns are `distraction`, `invalid_branch`, `clarification_without_submit`, and `skip_ahead`. Treat `backtrack`, `correction_backtrack`, runtime execution, scoring, and benchmark orchestration as future improvements unless explicitly reopened.

## M60.7.1 Source YAML Loader and Graph Summary

M60.7.1 adds the first implemented slice of Real Module Testcase Generation: PathWalk can now read a real `source/program.ordo.yaml` in authoring/testcase-generation mode and emit `REAL_MODULE_GRAPH_SUMMARY.json/.md` plus `VALIDATION_REPORT.json`. This does not read `compiled/*`, does not generate testcases yet, and does not change runtime-core semantics or scoring weights.

Command:

```bash
PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli real-module-graph --source path/to/source/program.ordo.yaml --out runs/real_module_graph --force
```

## M60.7.2 Terminal Path Enumeration

M60.7.2 extends the Real Module Testcase Generation line with terminal path enumeration from `REAL_MODULE_GRAPH_SUMMARY.json`. PathWalk now writes `REAL_MODULE_TERMINAL_PATHS.json/.md` plus a validation report. This is still source-analysis/testcase-preparation work: it does not emit testcase/noise artifacts, does not read `compiled/*`, and does not change Ordo runtime-core semantics or scoring weights.

```bash
PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli real-module-paths \
  --summary runs/real_module_graph/REAL_MODULE_GRAPH_SUMMARY.json \
  --out runs/real_module_paths \
  --force
```



## M60.7.5 — Bounded Noise Testcase Artifacts

M60.7.5 extends `real-module-noise-cases` to four artifact-only patterns: `distraction`, `invalid_branch`, `clarification_without_submit`, and `skip_ahead`. This closes the current noise-expansion line; remaining complex patterns are future improvements unless explicitly reopened. Runtime execution, scoring, calibration, and benchmark orchestration remain out of scope.

## M60.7.4 — Noise Testcase Artifacts

Stable M60.7.4 adds `real-module-noise-cases`, which turns `REAL_MODULE_TERMINAL_PATHS.json` into artifact-only noise testcase artifacts for `distraction` and `invalid_branch`: `cases/*.json`, `cases/*.md`, `RAW_NOISE_TESTCASE_MATRIX.csv`, `SUMMARY.json/.md`, and `VALIDATION_REPORT.json`. Runtime execution, scoring, calibration, and benchmark orchestration remain future milestones.

## M60.7.3 — Clean Path Testcase Artifacts

Stable M60.7.3 adds `real-module-clean-cases`, which turns `REAL_MODULE_TERMINAL_PATHS.json` into clean-path testcase artifacts: `cases/*.json`, `cases/*.md`, `RAW_TESTCASE_MATRIX.csv`, `SUMMARY.json/.md`, and `VALIDATION_REPORT.json`. Runtime execution and noise generation remain future milestones.

## M61.0 — Human Review Scenario Cards

M61.0 adds `real-module-review-cards`, an artifact-only QA/developer reading layer over generated clean and bounded-noise real-module testcases. It consumes clean/noise `SUMMARY.json` files and emits `cards/*.md`, `REVIEW_CARDS.md`, `REVIEW_CARDS.json`, `RAW_REVIEW_CARD_MATRIX.csv`, and a validation report.

Runtime execution, scoring, calibration, model/API benchmark orchestration, and watchdog hardening remain future milestones.


## M62.3 developer handoff note

APF language/process-model candidates are classified but not implemented as runtime-core features. Use `APF_LANGUAGE_PATTERN_EXTRACTION_PLAN.md` before starting any APF branch patch or IR promotion work.


## M62 Line Closure

APF is included as a standard applied module. Use `M62_APF_INTEGRATION_LINE_CLOSURE.md` and `STANDARD_APPLIED_MODULES.md` for handoff.

## M63.0 APF rc.1 integration planning

APF `v0.1.0-alpha.14` remains the historical M62 import point. The target for M63 is `ordo.applied_project_factory` `v0.1.0-rc.1` as a release-candidate standard applied module. M63.1 must import the actual rc.1 archive before alpha.14 can be replaced as the current package.


## M63.1 APF rc.1 standard module

The current package includes `ordo.applied_project_factory` as a release-candidate standard applied module.

```text
packages/ordo_applied_project_factory/
  module_id: ordo.applied_project_factory
  version: 0.1.0-rc.1
  lifecycle: release-candidate
  is_standard_applied_module: true
```

APF rc.1 supersedes the historical M62 alpha.14 import point. APF runtime logic remains module-local; candidate language patterns are documented and classified, not promoted automatically to core IR/opcodes.
