# 037 — Five-Cycle Improvement Mode

## Status

Canonical contract for `BL-BENCH-037`.

## Purpose

Provide a bounded iterative mode for difficult defects while preventing endless tuning, benchmark overfitting and hidden baseline drift.

## Cycle limit

A campaign may execute at most five accepted or rejected patch attempts against one frozen diagnostic objective.

## Cycle structure

Each cycle performs:

1. restate the active hypothesis;
2. choose one bounded patch target;
3. apply one scoped patch;
4. verify the change scope;
5. execute the fixed regression set;
6. compare to the same frozen baseline;
7. classify outcome;
8. decide stop, continue or rollback.

## Mandatory stop conditions

Stop before cycle five when:

- acceptance criteria are met;
- the original defect is no longer reproducible and no protected regression degrades;
- evidence contradicts the active root-cause hypothesis;
- two consecutive cycles produce no measurable improvement;
- a severe new regression appears;
- scope would need to expand beyond the approved campaign;
- evaluation or scenario contracts would need uncontrolled mutation.

## Cycle outcomes

- `IMPROVED_ACCEPTABLE`;
- `IMPROVED_INSUFFICIENT`;
- `NO_CHANGE`;
- `REGRESSED`;
- `HYPOTHESIS_CONTRADICTED`;
- `BLOCKED`.

## Anti-overfitting rules

- The trigger scenario may not be rewritten during the campaign.
- Hidden evaluator evidence remains hidden.
- Regression membership is frozen unless a newly discovered dependency is formally added with rationale.
- Scoring weights may not be tuned to make the patch appear successful.
- Each cycle may change only one primary component class unless a multi-factor diagnosis explicitly requires more.

## End-of-campaign decision

After cycle five, the campaign must terminate as:

- `CAMPAIGN_ACCEPTED`;
- `CAMPAIGN_PARTIALLY_ACCEPTED`;
- `CAMPAIGN_REJECTED`;
- `CAMPAIGN_ESCALATED`.

No sixth cycle is allowed under the same campaign ID.

## Completion evidence

This contract and the campaign template complete `BL-BENCH-037`.
