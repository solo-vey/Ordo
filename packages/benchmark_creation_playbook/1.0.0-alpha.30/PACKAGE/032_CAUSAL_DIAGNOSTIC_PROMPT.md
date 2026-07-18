# 032. Causal Diagnostic Prompt

**Backlog:** `BL-BENCH-032`  
**Status:** implemented  
**Version:** `1.0.0`

## Purpose

Provide a deterministic investigation prompt after a weak, inconsistent, capped, or surprising benchmark result. The prompt collects an executor explanation without treating that explanation as ground truth.

## Trigger conditions

Open a diagnostic case when at least one condition is true:

- a process or document score falls below the configured threshold;
- a failure cap is applied;
- expected and observed terminal routes differ;
- two package variants diverge materially on the same comparable cohort;
- a correction, invalidation, or approval is missing or ambiguous;
- an artifact contains behavior not traceable to the active contract;
- an evaluator flags `needs-causal-investigation`.

## Diagnostic isolation

Diagnostics start only after execution and initial evaluation are frozen. The executor must not receive hidden scoring rules before the run ends. Diagnostic responses are stored separately from original execution evidence and cannot retroactively alter the execution log.

## Canonical prompt blocks

The diagnostic request must bind:

1. `diagnostic_case_id`;
2. affected `result_record_id`, `attempt_id`, test case, RUN and package variant;
3. exact artifact or process finding under investigation;
4. frozen evidence snapshot identifiers;
5. requested provenance questions;
6. response schema and uncertainty rule.

## Mandatory questions to the executor

The executor is asked to identify, with exact references where possible:

- which node, obligation, instruction section or semantic intent produced the result;
- which prompt, template, source artifact and contract versions were active;
- which facts were available at the decision point;
- which facts were unavailable, hidden, superseded, corrected or ignored;
- why the chosen route or content appeared valid at that time;
- which gate or validator was expected to detect the defect;
- whether the defect originated before generation, during generation, during rendering or during evaluation;
- what minimal change would prevent recurrence;
- confidence level and unresolved alternatives.

## Required response discipline

The executor must separate:

- `observed_from_available_context`;
- `inferred_explanation`;
- `uncertain_or_unavailable`;
- `proposed_fix`.

Unsupported certainty is forbidden. A response without evidence pointers is usable as a hypothesis only.

## Prompt output

Use `templates/CAUSAL_DIAGNOSTIC_REQUEST.template.json` and validate with `schemas/causal_diagnostic_request.schema.json`.

## Gate

The task is complete when the prompt is reproducible, binds frozen evidence, asks provenance questions, records uncertainty, and cannot modify the original execution record.
