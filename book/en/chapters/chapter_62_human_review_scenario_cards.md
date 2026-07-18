# Chapter 62. Human Review Scenario Cards

M61.0 adds an intermediate PathWalk layer between generated real-module testcase artifacts and future runtime execution.

Its purpose is simple: QA, a developer, or a reviewer should be able to read a generated case as a scenario card instead of reverse-engineering raw JSON.

## What existed before

After M60.7, the artifact-only chain is:

```text
source/program.ordo.yaml
→ REAL_MODULE_GRAPH_SUMMARY.json
→ REAL_MODULE_TERMINAL_PATHS.json
→ clean path cases
→ bounded noise cases
```

The clean and noise cases are structured, but they are primarily machine artifacts.

M61.0 adds a human layer:

```text
clean path cases + bounded noise cases
→ human review scenario cards
```

## Command

```bash
PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli real-module-review-cards \
  --summary runs/real_module_clean_cases/SUMMARY.json \
  --summary runs/real_module_noise_cases/SUMMARY.json \
  --out runs/real_module_review_cards \
  --force
```

## Artifacts

The command creates:

```text
cards/<card_id>.json
cards/<card_id>.md
REVIEW_CARDS.json
REVIEW_CARDS.md
RAW_REVIEW_CARD_MATRIX.csv
VALIDATION_REPORT.json
```

`cards/*.md` is the primary human-facing format. A card shows:

- case ID;
- path ID;
- noise pattern;
- scripted steps;
- expected behavior;
- expected terminal;
- expected outputs;
- review checklist.

## What this does not do

M61.0 does not execute the runtime.

It also does not perform:

- model/API benchmark runs;
- scoring;
- calibration;
- watchdog or process-boundary hardening;
- runtime-harness matrix execution.

This boundary is deliberate. It avoids reopening the blocked M60.6.5 / M60.6.4.1 runtime-execution branch.

## Readiness is explicit

Review-card artifacts separate readiness states:

```text
review_cards_ready        # target of M61.0
runtime_execution_ready   # false
scoring_ready             # false
calibration_ready         # false
```

The cards are ready for human review. They are not evidence that runtime execution passed or that a model is good.

## Why this is useful

Human review cards provide practical value without heavy execution infrastructure:

- terminal-path coverage can be reviewed manually;
- distraction, invalid-branch, clarification, and skip-ahead cases become readable;
- the cards can serve as QA checklists;
- future runtime-execution work can be prepared on top of reviewed scenarios.

## Stop boundary

M61.0 is the correct layer after the M60.8 handoff because it improves usability without opening runtime orchestration.

Future work remains separate:

```text
M62.0 Runtime Execution of Generated Testcases
backtrack
correction_backtrack
scoring generated cases
calibration generated cases
watchdog/process-boundary hardening
```

The main principle is:

```text
first make generated cases understandable to people;
then execute them safely;
only after that score and calibrate.
```
