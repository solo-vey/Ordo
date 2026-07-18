# Design Decisions

## DD-BENCH-001 — Benchmark playbook is an Ordo Process Rail

**Status:** accepted  
**Date:** 2026-07-16

**Decision:** The benchmark methodology will be materialized as an AI-guided Ordo Process Rail with deterministic helpers, explicit node contracts, checkpoints, gates and versioned artifacts.

**Reason:** A prose-only methodology would reproduce the same selective-rule and memory-drift failures the benchmark is intended to prevent.

## DD-BENCH-002 — Process and document evaluation are separate

**Status:** accepted

**Decision:** Process quality and document quality are reviewed independently and aggregated only after both audits are complete.

**Reason:** Correct terminal routing cannot compensate for shallow generated documents, and strong documents cannot compensate for fabricated facts or a wrong route.

## DD-BENCH-003 — Artifact contracts are authoritative and role-specific

**Status:** accepted

**Decision:** Passport, Jira, Manual QA, Automation and other artifacts each receive their own current evaluation contract. Criteria must not be transferred between artifacts without an explicit rule.

**Reason:** The Jira re-audit showed that importing Passport/unit-test requirements into Jira produced an invalid score.

## DD-BENCH-004 — The result registry is supersession-aware

**Status:** accepted

**Decision:** Re-audits never silently overwrite historical scores. They create a new evaluation record and mark the old one superseded with a reason.

## DD-BENCH-005 — Initial package profile is dev

**Status:** accepted

**Decision:** Version 0.1.0 is a development/authoring package containing editable source, backlog and reports. Runtime and evidence profiles will be built only after execution and evaluation epics are implemented.


## DD-BENCH-0004 — Three canonical Task Classes

**Status:** accepted  
**Date:** 2026-07-16

The playbook uses TC01 bounded transformation, TC02 deterministic process execution and TC03 analytical package engineering. One class is primary; secondary classes require rationale. The current database-change benchmark is TC03 primary / TC02 secondary.

## DD-BENCH-0005 — Test-case source package precedes RUN and variants

**Status:** accepted  
**Date:** 2026-07-16

A benchmark test case must first exist as an approved source package with public/hidden/evaluator separation, fixed authority and evaluation bindings. RUN scenarios and compiled variants are downstream products.

## DD-BENCH-0006 — Scoped YAML patch verification requested

**Status:** backlog accepted; implementation deferred  
**Date:** 2026-07-16

Owner feedback identified a risk that local YAML playbook changes may rebuild unrelated nodes. `BL-BENCH-041` will formalize affected-node allowlists and structural/semantic diff gates. Epic 02 records the requirement but does not claim it implemented.
\n\n## DD-BENCH-0006 — RUN scenarios are orthogonal to package variants\n\n**Status:** accepted  \n**Date:** 2026-07-16\n\nA RUN defines hidden interaction/lifecycle conditions. A package variant defines instruction representation. They must be independently versioned and combined only in result identity.\n\n## DD-BENCH-0007 — Expected terminal is evaluator-only\n\n**Status:** accepted  \n**Date:** 2026-07-16\n\nThe executor must not receive the expected terminal. The Driver enforces state transitions; the evaluator verifies the terminal after execution.\n\n## DD-BENCH-0008 — Baseline RUN semantics are stable\n\n**Status:** accepted  \n**Date:** 2026-07-16\n\nRUN_01–RUN_05 form the canonical baseline. New behaviors use RUN_06+ unless a versioned migration is explicitly approved.\n

## DD-BENCH-0004 — Package variants are isolated experimental treatments

**Status:** accepted

The four package variants have separate source lineage and contamination policies. `PV-DIRECT` cannot consume YAML-derived improvements; compiled variants cannot consume prior run outputs. Comparability requires a complete variant identity tuple and versioned transformation profile.


## DD-BENCH-0010 — Driver authority is separated from evaluator authority

**Status:** accepted  
**Decision:** Drivers control scenario interaction and evidence; evaluators score only sealed results after terminal.

## DD-BENCH-0011 — Driver family is selected mechanically before launch

**Status:** accepted  
**Decision:** Closed node graph selects step-bound; complete obligation/intent model selects semantic-adaptive; otherwise block as unsupported/hybrid.

## DD-BENCH-0012 — Blind contexts are allowlist-built from separate roots

**Status:** accepted  
**Decision:** Never create executor context by filtering a combined private/evaluator bundle.


## DD-BENCH-0011 — Attempt identity and evidence are immutable

**Status:** accepted

Every launch has a unique attempt ID, sealed preflight and append-only event log. Retries create new attempts; evidence is never silently overwritten.

## DD-BENCH-0012 — Executor cannot choose authoritative terminal or self-score

**Status:** accepted

The executor may declare completion only. Driver and terminal gate determine operational disposition; evaluator scores downstream after evidence is sealed.


## DD-BENCH-0009 — Process score is independent from document score

**Status:** accepted

A run can follow the correct route and still generate weak documents, or generate strong-looking documents through an invalid process. Therefore process and document evaluation remain separate until result aggregation.

## DD-BENCH-0010 — Critical failures cap rather than subtract

**Status:** accepted

Critical route, invention, correction, isolation and evidence failures impose a maximum score. The lowest confirmed cap is applied after raw scoring.


## DD-BENCH-0008 — Document criteria are artifact-specific

**Status:** accepted

Document evaluation must bind exactly one artifact contract. Criteria cannot be imported from another artifact type. Jira is a derived delivery view and is not required to duplicate Passport or contain unit-test implementation details.


## DD-BENCH-0021 — Benchmark results are append-only observations

**Status:** accepted  
**Date:** 2026-07-16

Scores and evidence are immutable version-bound records. Corrections, reruns and evaluation migrations create successor records and explicit supersession events. Derived matrices are reproducible views, not sources of truth.

## DD-BENCH-0022 — Comparability is a gate, not an assumption

**Status:** accepted  
**Date:** 2026-07-16

Cross-variant ranking is allowed only for records in an explicitly comparable cohort. Different RUN, model configuration, scoring contract or contamination status must be separated or normalized by an approved rule.


## DD-BENCH-0100 — Executor diagnostic explanation is a hypothesis

**Status:** accepted  
**Date:** 2026-07-16

Executor self-report may explain perceived reasoning but cannot confirm causality without corroboration from frozen package, execution, artifact, validator or evaluation evidence.


## DD-EPIC11-01 — Bounded improvement over free-form tuning

All improvements are versioned, reversible, regression-bound and limited to five cycles per campaign. Benchmark scenarios and scoring cannot be silently tuned to manufacture success.


## DD-EPIC12-001 — Evidence claims require checksum-bound materialization
Chat history is not sufficient evidence.

## DD-EPIC12-002 — Handoff is a deterministic package, not a narrative summary
Receiver preflight, reading order and no-downgrade rules are mandatory.


## v0.13.0 — BL-BENCH-041 closure
Scoped YAML patch verification is enforceable through node allowlists, canonical structural hashes, semantic diffs, out-of-scope rejection and persisted proof reports. Backlog complete: 41/41.
