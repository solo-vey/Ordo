# M60.7 — Real Module Testcase Generation Kickoff

Generated: 2026-07-08T08:30:00+02:00

## Status

**Milestone type:** design / kickoff contract.  
**Base:** M60.6.4 stable package line.  
**Implementation status:** not implemented yet.  
**Weights:** locked.  
**Runtime-core semantics:** unchanged.

## Goal

Add a PathWalk companion mode that can generate testcase artifacts from a real Ordo module instead of only synthetic generated trees.

Primary input:

```text
source/program.ordo.yaml
```

Primary output:

```text
real-module testcase artifacts
```

This should allow PathWalk to create realistic test cases from the actual decision tree / guided-intake graph and add controlled model-confusion patterns.

## Why this is the right next milestone

M60.6 proved that artifact-only dry-run works and that model benchmark calibration needs richer data. The next useful step is not another subprocess benchmark matrix. The useful step is better input realism: generate test cases from real modules.

This milestone should produce better test material first. Real model benchmark execution and weight calibration remain later milestones.

## Scope

M60.7 is in scope for PathWalk only:

- read a real Ordo source module from `source/program.ordo.yaml`;
- extract decision-tree / graph structure needed for testcase generation;
- enumerate valid terminal paths;
- generate testcase artifacts from real paths;
- add controlled noise/confusion patterns;
- produce a machine-readable generation summary;
- keep execution optional and artifact-oriented.

## Out of scope

M60.7 must not:

- change Ordo runtime-core semantics;
- change `path_quality_score` weights;
- run real model/API benchmark by default;
- revive the blocked M60.6.5 / M60.6.4.1 transcript matrix path;
- read `compiled/*` directly during enforced runtime execution;
- use `python3 cli_embedded/ordo_run.py`;
- treat PathWalk as runtime core.

## Required generation modes

Initial testcase generation should support these noise patterns:

| Pattern | Meaning |
|---|---|
| `clean_path` | valid path with no intentional confusion |
| `distraction` | user asks unrelated or side question during intake |
| `backtrack` | user returns to a previous decision point |
| `skip_ahead` | user tries to answer a future node early |
| `invalid_branch` | user gives an answer not allowed by current branch |
| `clarification_without_submit` | user asks for clarification without committing an answer |
| `correction_backtrack` | user corrects a previously submitted answer |

## Proposed artifact contract

```text
REAL_MODULE_TESTCASE_PLAN.json
REAL_MODULE_GRAPH_SUMMARY.json
cases/<case_id>.json
cases/<case_id>.md
RAW_TESTCASE_MATRIX.csv
SUMMARY.json
SUMMARY.md
VALIDATION_REPORT.json
```

Optional future execution artifacts should follow the proven M60.5.4 pattern:

```text
plan artifacts → independent job scripts / CI jobs → collect from score files
```

## Candidate CLI commands

Proposed, not implemented yet:

```bash
python3 -m ordo_pathwalk.cli real-module-plan   --source path/to/source/program.ordo.yaml   --out runs/real_module_cases   --case-count 30   --noise clean_path,distraction,backtrack,skip_ahead,invalid_branch

python3 -m ordo_pathwalk.cli real-module-collect   --plan runs/real_module_cases/REAL_MODULE_TESTCASE_PLAN.json
```

A later milestone may add execution commands, but M60.7 should first stabilize generation artifacts.

## Acceptance gates for M60.7 implementation

M60.7 implementation is not ready until these gates pass:

```text
source_yaml_loader = passed
graph_summary_generated = passed
terminal_paths_enumerated = passed
case_artifacts_generated = passed
noise_patterns_covered = passed
no_compiled_direct_read_in_enforced_mode = passed
artifact_contract_documented = passed
pytest_added = passed
sample_fixture_run = passed
```

## Regression discipline

Use small, deterministic fixture modules first. Do not begin with large real-world modules until the fixture path is stable.

Recommended implementation phases:

1. `M60.7.1` — source YAML loader and graph summary.
2. `M60.7.2` — terminal path enumeration.
3. `M60.7.3` — testcase artifact schema and clean-path generation.
4. `M60.7.4` — noise pattern generation.
5. `M60.7.5` — fixture acceptance and packaging.

## Calibration lock

M60.7 testcase generation may improve benchmark input quality, but it does not unlock calibration by itself.

Weight calibration remains blocked until a later run has:

```text
real model/transcript evidence
nonzero variance
repeatability analysis
manual failure review
calibration decision artifact
```
