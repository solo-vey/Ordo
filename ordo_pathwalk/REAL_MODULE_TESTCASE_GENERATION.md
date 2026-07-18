# PathWalk Real Module Testcase Generation

## Status

Milestone: `M61.0`  
Status: source YAML loader, graph summary, terminal path enumeration, clean-path testcase artifacts, bounded noise testcase artifacts, and human review scenario cards implemented  
Implementation boundary: runtime execution, scoring, calibration, benchmark orchestration, and watchdog/process-boundary hardening are not implemented here

## Purpose

PathWalk should be able to generate testcase artifacts from a real Ordo module, not only from synthetic generated trees.

The intended input is:

```text
source/program.ordo.yaml
```

The implemented M60.7.1/M60.7.2/M60.7.3/M60.7.4/M60.7.5/M61.0 outputs are graph summary, terminal path, clean-path testcase, bounded-noise testcase, and human-review card packages:

```text
REAL_MODULE_GRAPH_SUMMARY.json
REAL_MODULE_GRAPH_SUMMARY.md
REAL_MODULE_TERMINAL_PATHS.json
REAL_MODULE_TERMINAL_PATHS.md
cases/<case_id>.json
cases/<case_id>.md
RAW_TESTCASE_MATRIX.csv
RAW_NOISE_TESTCASE_MATRIX.csv
SUMMARY.json
SUMMARY.md
VALIDATION_REPORT.json
REVIEW_CARDS.json
REVIEW_CARDS.md
RAW_REVIEW_CARD_MATRIX.csv
```

The future output remains a testcase package that represents real decision-tree paths and controlled model-confusion patterns.

## Boundary

This feature belongs to PathWalk as a companion utility. It is not Ordo runtime core.

Generation may read the source YAML because it is authoring/testcase-generation work. Enforced runtime execution must still use the embedded CLI and must not read `compiled/*` directly.

M60.7.1/M60.7.2/M60.7.3/M60.7.4/M60.7.5 explicitly do **not** read `compiled/*` artifacts. M60.7.3 claims clean-path testcase artifact readiness only. M60.7.4 claims bounded-noise testcase artifact readiness only; it does **not** claim runtime execution, scoring, or calibration readiness.

## M60.7.1 / M60.7.2 / M60.7.3 / M60.7.4 CLI

```bash
PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli real-module-graph \
  --source path/to/source/program.ordo.yaml \
  --out runs/real_module_graph \
  --force
```

The graph command writes:

```text
runs/real_module_graph/REAL_MODULE_GRAPH_SUMMARY.json
runs/real_module_graph/REAL_MODULE_GRAPH_SUMMARY.md
runs/real_module_graph/VALIDATION_REPORT.json
```

M60.7.2 terminal path enumeration:

```bash
PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli real-module-paths \
  --summary runs/real_module_graph/REAL_MODULE_GRAPH_SUMMARY.json \
  --out runs/real_module_paths \
  --force
```

The paths command writes:

```text
runs/real_module_paths/REAL_MODULE_TERMINAL_PATHS.json
runs/real_module_paths/REAL_MODULE_TERMINAL_PATHS.md
runs/real_module_paths/VALIDATION_REPORT.json
```

M60.7.3 clean-path testcase artifacts:

```bash
PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli real-module-clean-cases \
  --paths runs/real_module_paths/REAL_MODULE_TERMINAL_PATHS.json \
  --out runs/real_module_clean_cases \
  --force
```

The clean-cases command writes:

```text
runs/real_module_clean_cases/cases/<case_id>.json
runs/real_module_clean_cases/cases/<case_id>.md
runs/real_module_clean_cases/RAW_TESTCASE_MATRIX.csv
runs/real_module_clean_cases/SUMMARY.json
runs/real_module_clean_cases/SUMMARY.md
runs/real_module_clean_cases/VALIDATION_REPORT.json
```

## M60.7.1 graph summary fields

`REAL_MODULE_GRAPH_SUMMARY.json` contains:

```text
schema_version
package / ordo_version / control_level / execution_mode
start_node / start_candidates
counts: nodes, edges, gates, assertions, outputs, unmatched handlers
nodes: id, question, answer_type, allowed_answers, branch answers
edges: from, answer, to, edge_type, target_type, state updates
unmatched_edges
terminal_targets
unresolved_targets
gates
outputs
readiness
```

Readiness has three separate meanings:

```text
graph_summary_ready        # M60.7.1 target
path_enumeration_ready     # whether the graph appears structurally usable for the next step
testcase_generation_ready  # always false in M60.7.1
```


## M60.7.2 terminal path fields

`REAL_MODULE_TERMINAL_PATHS.json` contains:

```text
schema_version
package / source_path / start_node
counts: terminal_paths, cycle_edges, dead_end_paths, outputs_referenced
terminal_paths: path_id, node_sequence, answer_sequence, branch_signature, terminal_target, terminal_type
state_updates
encountered_unmatched_handlers
outputs_allowed_after_terminal
readiness
```

Readiness remains deliberately split:

```text
terminal_path_enumeration_ready  # M60.7.2 target
clean_path_case_generation_ready # structural readiness for a later clean case generator
noise_case_generation_ready      # always false in M60.7.2
testcase_generation_ready        # always false in M60.7.2
```


## M60.7.3 clean-path testcase fields

`SUMMARY.json` contains:

```text
schema_version
package / source_path / start_node
counts: clean_path_cases, ready_cases, terminal_paths_input, noise_patterns
cases: case_id, path_id, case_type, noise_pattern, branch_signature
answer_steps: node, answer, source_answer, to, target_type, edge_type
expected_terminal
expected_outputs
expected_state_updates
readiness
```

Readiness remains deliberately split:

```text
clean_path_cases_ready     # M60.7.3 target
runtime_execution_ready    # always false in M60.7.3
noise_case_generation_ready # always false in M60.7.3
```


## M60.7.4 first noise testcase fields

M60.7.4 adds artifact-only generation for the bounded controlled noise patterns: `distraction`, `invalid_branch`, `clarification_without_submit`, and `skip_ahead`.

```bash
PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli real-module-noise-cases \
  --paths runs/real_module_paths/REAL_MODULE_TERMINAL_PATHS.json \
  --out runs/real_module_noise_cases \
  --pattern distraction \
  --pattern invalid_branch \
  --pattern clarification_without_submit \
  --pattern skip_ahead \
  --force
```

The noise-cases command writes:

```text
runs/real_module_noise_cases/cases/<case_id>.json
runs/real_module_noise_cases/cases/<case_id>.md
runs/real_module_noise_cases/RAW_NOISE_TESTCASE_MATRIX.csv
runs/real_module_noise_cases/SUMMARY.json
runs/real_module_noise_cases/SUMMARY.md
runs/real_module_noise_cases/VALIDATION_REPORT.json
```

`SUMMARY.json` contains:

```text
schema_version
package / source_path / start_node
patterns / pattern_counts
counts: noise_cases, ready_cases, terminal_paths_input, patterns
cases: case_id, path_id, case_type, noise_pattern, branch_signature
scripted_steps: node, input_kind, answer, expected_behavior, submit_expected
clean_answer_steps
expected_terminal
expected_outputs
expected_state_updates
readiness
```

Readiness remains deliberately split:

```text
noise_cases_ready       # M60.7.5 target
runtime_execution_ready # always false in M60.7.5
scoring_ready           # always false in M60.7.5
calibration_ready       # always false in M60.7.5
```

This line implements `distraction`, `invalid_branch`, `clarification_without_submit`, and `skip_ahead`; it does not implement `backtrack` or `correction_backtrack`. They remain future noise-pattern milestones.



## M61.0 human review scenario cards

M61.0 adds a human-readable QA/developer review layer over existing clean and bounded-noise testcase packages. It consumes one or more testcase `SUMMARY.json` files and writes review-card artifacts.

```bash
PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli real-module-review-cards \
  --summary runs/real_module_clean_cases/SUMMARY.json \
  --summary runs/real_module_noise_cases/SUMMARY.json \
  --out runs/real_module_review_cards \
  --force
```

The review-cards command writes:

```text
runs/real_module_review_cards/cards/<card_id>.json
runs/real_module_review_cards/cards/<card_id>.md
runs/real_module_review_cards/REVIEW_CARDS.json
runs/real_module_review_cards/REVIEW_CARDS.md
runs/real_module_review_cards/RAW_REVIEW_CARD_MATRIX.csv
runs/real_module_review_cards/VALIDATION_REPORT.json
```

`REVIEW_CARDS.json` contains:

```text
schema_version
source_summaries
counts: review_cards, ready_cards, runtime_executions, scores
case_type_counts
noise_pattern_counts
cards: card_id, case_id, case_type, noise_pattern, path_id
review_focus
scripted_steps
expected_terminal
expected_outputs
expected_state_updates
checklist
readiness
```

Readiness remains deliberately split:

```text
review_cards_ready      # M61.0 target
runtime_execution_ready # always false in M61.0
scoring_ready           # always false in M61.0
calibration_ready       # always false in M61.0
```

Human review cards are review artifacts, not benchmark results.


## Initial noise taxonomy for later milestones

- `clean_path`
- `distraction`
- `backtrack`
- `skip_ahead`
- `invalid_branch`
- `clarification_without_submit`
- `correction_backtrack`

## Future artifact contract

```text
REAL_MODULE_TESTCASE_PLAN.json
REAL_MODULE_GRAPH_SUMMARY.json
cases/<case_id>.json
cases/<case_id>.md
RAW_TESTCASE_MATRIX.csv
RAW_NOISE_TESTCASE_MATRIX.csv
SUMMARY.json
SUMMARY.md
VALIDATION_REPORT.json
```

## Future CLI surface

```bash
python3 -m ordo_pathwalk.cli real-module-plan \
  --source path/to/source/program.ordo.yaml \
  --out runs/real_module_cases \
  --case-count 30 \
  --noise clean_path,distraction,backtrack,skip_ahead,invalid_branch

python3 -m ordo_pathwalk.cli real-module-collect \
  --plan runs/real_module_cases/REAL_MODULE_TESTCASE_PLAN.json
```

These commands remain a target contract for later implementation steps.

## Implementation sequence

1. Source YAML loader. **Implemented in M60.7.1.**
2. Graph summary extraction. **Implemented in M60.7.1.**
3. Terminal path enumeration. **Implemented in M60.7.2.**
4. Clean-path testcase generation. **Implemented in M60.7.3.**
5. Bounded noise-pattern testcase generation (`distraction`, `invalid_branch`, `clarification_without_submit`, `skip_ahead`). **Implemented in M60.7.5.**
6. Complex conversational recovery patterns (`backtrack`, `correction_backtrack`). **Future improvement; not a current blocker.**
6. Remaining noise-pattern testcase generation.
7. Fixture acceptance and packaging.

## Non-goals

- No scoring weight calibration.
- No real API/model benchmark by default.
- No broad transcript replay matrix.
- No runtime-core semantic changes.
- No reading of `compiled/*` for testcase-generation source analysis.


## M60.7.5 boundary note

M60.7.5 intentionally stops the current noise-pattern expansion after four artifact-only patterns. This prevents the milestone from turning into an endless sequence of small variants. Remaining complex recovery cases are tracked as future improvements and should be reopened only when there is a clear need and a bounded implementation scope.

## M60.7 line closure

The current artifact-only Real Module Testcase Generation line is closed at M60.7.5. PathWalk supports graph summary, terminal path enumeration, clean-path testcase artifacts, and bounded noise testcase artifacts for `distraction`, `invalid_branch`, `clarification_without_submit`, and `skip_ahead`.

Do not keep extending noise variants inside this line by default. More complex recovery patterns such as `backtrack` and `correction_backtrack`, plus runtime execution/scoring, are future milestones.

