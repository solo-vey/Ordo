# Comparative Evidence Report: New Office Opening

## Scope

- Task class: `TC01_COMPLEX_MULTI_STEP_PROCESS`
- Case: `EX01_NEW_OFFICE_OPENING`
- Compared implementations: Ordo Playbook and instruction-only execution
- Scenarios: S01–S05
- Evidence status: all ten listed results explicitly admitted as canonical

## Composite results

| Scenario | Ordo Playbook | Instruction-only | Difference | Instruction-only verdict |
|---|---:|---:|---:|---|
| S01 Clean Control | 98 | 94 | +4 | Passed |
| S02 Branch Heavy | 98 | 81 | +17 | Failed behavior |
| S03 Invalid and Irrelevant | 100 | 91 | +9 | Passed; evaluator defect overridden by direct evidence |
| S04 Backtrack and Correct | 98 | 73 | +25 | Failed behavior |
| S05 Incomplete Hard Stop | 100 | 95 | +5 | Passed |
| **Mean** | **98.8** | **86.8** | **+12.0** | — |

## Scenario findings

### S01 Clean Control

Both approaches completed the straightforward path. Ordo retained a small advantage in evidence structure, validation, and deterministic execution.

### S02 Branch Heavy

The instruction-only executor made two critical routing errors. It advanced instead of looping after critical supplier replacement and advanced to pilot day instead of remediation after blocked readiness. The Driver imposed the expected route after each error. Ordo executed the corresponding branch and loop behavior correctly.

### S03 Invalid and Irrelevant

Both approaches safely rejected invalid and irrelevant inputs without fabricating data or advancing incorrectly. The instruction-only evaluator incorrectly claimed D3 existed, but direct inspection showed that D3 was absent and execution correctly remained at N18. The evaluator defect reduced the validation-reliability component.

### S04 Backtrack and Correct

The instruction-only executor did not recognize the restore request and remained at the pre-restore step. The Driver imposed the recovery route. Ordo restored state, invalidated dependent downstream data, and repeated the affected path correctly. This is the largest measured difference in the case.

### S05 Incomplete Hard Stop

Both approaches stopped safely when mandatory geography and target-date data were missing. Neither fabricated data, generated documents, nor claimed completion.

## Quantitative interpretation

For this case, Ordo’s mean composite score is 12.0 points higher. The advantage is concentrated in control-flow-intensive scenarios rather than clean-path completion. The evidence supports the bounded claim that Ordo is better for this example when the process requires branch/loop routing and restore/backtrack behavior.

This report does not yet establish superiority for every task in TC01, for other task classes, or across models. Additional cases and replications are required.

## Method

Scores use the six-component weighted method defined in `00_governance/COMPOSITE_QUALITY_SCORING_METHOD.md`. Raw execution archives are preserved unchanged. English metadata and scorecards record admissions, findings, limitations, and any evaluator overrides.

## Known limitations

- Some instruction-only packages lack an independent final evaluator.
- RUN_03 required a direct-evidence override of a faulty evaluator statement.
- In S02 and S04, the Driver continued after executor routing errors; the error itself is canonical evidence, but future Driver versions should hard-stop on transition mismatch.
- Raw run archives may contain Ukrainian because they preserve the original execution evidence byte-for-byte.
