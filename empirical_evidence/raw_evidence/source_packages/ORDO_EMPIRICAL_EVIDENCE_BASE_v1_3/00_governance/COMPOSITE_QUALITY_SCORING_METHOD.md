# Composite Quality Scoring Method

## Purpose

The composite score converts a run’s evidence into a transparent 0–100 quality score. It is not a substitute for the underlying findings.

## Components and default weights

| Component | Weight |
|---|---:|
| Correct scenario completion | 15% |
| Branch, loop, rollback, restore, and transition correctness | 25% |
| State, trace, snapshot, and evidence integrity | 20% |
| Artifact quality and completeness | 15% |
| Validation and evaluator reliability | 15% |
| Safe behavior under invalid or missing input | 10% |
| **Total** | **100%** |

## Formula

`Composite Score = sum(component score × component weight)`

Each component is scored from 0 to 100. If a component is genuinely not applicable, its weight is removed and the remaining applicable weights are normalized proportionally.

## Scoring rules

- Reaching `T_COMPLETED` does not by itself imply a high score.
- A wrong critical branch, loop, rollback, or restore transition materially reduces the control-flow score.
- A route imposed by an external Driver after an executor error is not credited as independent control-flow success.
- Missing independent evaluation reduces evaluator-reliability credit but does not automatically invalidate direct evidence.
- Fabricating mandatory data caps the total score at 40.
- Contaminated runs receive no ordinary composite score.
- Test-construction defects are distinguished from model-behavior defects.

## Admission workflow

Before a new result is admitted, present the factual findings, component scores, weighted calculation, proposed verdict, and updated comparison table. Admission occurs only after explicit user confirmation.
