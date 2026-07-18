# PathWalk Benchmark Purpose and Calibration Contract

Status: `active`
Milestone: `M76.4 / BL-ORDO-006`

## Primary purpose

PathWalk is primarily an **Ordo release-QA benchmark**.

It validates that a model-driven operator can traverse a real Ordo process through the supported runtime interface while preserving graph, protocol, session, backtrack, correction, and distraction-handling invariants.

Primary gate question:

> Does this Ordo runtime/package/process remain safely and correctly operable under representative model behavior?

## Secondary purposes

1. **Model comparison** — allowed only when all compared runs use the same benchmark-pinned dataset, runtime package hash, protocol version, weights profile, seeds, and execution policy.
2. **Compatibility-current validation** — checks the current Ordo workspace/runtime for regressions; it is not directly comparable with benchmark-pinned historical runs.
3. **Research analysis** — permitted as an exploratory use, but PathWalk is not a public leaderboard and does not optimize weights for ranking models.

## Reporting modes

### benchmark-pinned

Use for model-to-model or version-to-version comparison.
All comparison-critical hashes and profiles must match.

### compatibility-current

Use for release QA against the latest workspace/runtime.
Results answer regression/readiness questions and must not be mixed into pinned rankings.

## Score interpretation

`path_quality_score` is a diagnostic composite, not the release gate by itself.

Release QA is fail-closed and requires all hard gates:

- `gate_passed = true` for every required case;
- no direct `compiled/*` access violation in enforced mode;
- `protocol_compliance_rate = 1.0` for every required case;
- required scenario/noise category coverage complete;
- no unresolved infrastructure or evidence-integrity failure;
- runtime/package hashes recorded.

The composite score is used to explain quality within an otherwise valid run and to compare matched benchmark-pinned runs.

## Default score profile

The existing default weights remain the production default:

```json
{
  "cell_match_rate": 0.45,
  "protocol_compliance_rate": 0.25,
  "distraction_recovery_rate": 0.15,
  "backtrack_accuracy": 0.15
}
```

They are **provisionally locked**, not statistically re-estimated.

Reason: current ground-truth data is saturated, and the small synthetic transcript pilot has deliberate variance but is not a sufficient real-model calibration dataset.

## Calibration eligibility gate

Default weights may change only when a candidate dataset satisfies all conditions:

- at least 3 distinct model/version targets;
- at least 2 independent runs per target;
- at least 100 scored cases total;
- at least 20 non-perfect completed cases;
- at least 10 hard or protocol failures;
- at least 3 runtime views or a documented single-view scope;
- repeated seeds/scenarios and failure-bucket coverage;
- manual adjudication for a stratified sample of failures;
- non-zero variance in at least 3 weighted components;
- raw component metrics retained;
- bootstrap confidence intervals or equivalent uncertainty summary;
- candidate weights improve predeclared release-QA discrimination without reducing hard-gate safety.

Until these conditions are met, calibration status is `locked_pending_eligible_real_model_dataset`.

## Anti-gaming rule

No weight change may turn a hard protocol or session-integrity failure into a release PASS. Hard gates always dominate the composite score.
